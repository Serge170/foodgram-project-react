""" Файл настройки селиализаторов."""

from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from recipes.models import (FavoriteResipes, Ingredients, IngredientsRecipes,
                            Recipes, ShoppingCart, Tags)
from users.models import Subscriptions, User
from users.serializers import CustomUserSerializer
from .fields import Base64ImageField


class RecipesShortSerializer(serializers.ModelSerializer):
    """ Сериализатор полей избранных рецептов и покупок."""

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientsSerializer(serializers.ModelSerializer):
    """ Сериализатор полей ингридиентов."""
    class Meta:
        model = Ingredients
        fields = '__all__'


class ShoppingCartSerializer(serializers.ModelSerializer):
    """ Сериализатор для списка покупок."""
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipes',)

    def validate(self, data):
        user = data['user']
        if user.shopping_cart.filter(recipes=data['recipes']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в корзину'
            )
        return data

    def to_representation(self, instance):
        return RecipesShortSerializer(
            instance.recipes,
            context={'request': self.context.get('request')}
        ).data


class FavoriteResipesSerializer(serializers.ModelSerializer):
    """ Сериализатор избранных рецептов."""
    class Meta:
        model = FavoriteResipes
        fields = ('user', 'recipes')

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipes = data['recipes']
        if FavoriteResipes.objects.filter(
            user=request.user, recipes=recipes
        ).exists():
            raise serializers.ValidationError({
                'status': 'Рецепт уже есть в избранном!'
            })
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShoppingCartSerializer(
            instance.recipes, context=context).data


class TagsSerializer(serializers.ModelSerializer):
    """ Сериализатор просмотра тегов."""
    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')


class IngredientsRecipesSerializer(serializers.ModelSerializer):
    """ Сериализатор связи ингридиентов и рецетов."""
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientsRecipes
        fields = ('id', 'amount')


class IngredientsGetSerializer(serializers.ModelSerializer):
    """ Сериализатор получения ингридиентов."""
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit')

    class Meta:
        model = IngredientsRecipes
        fields = ('id', 'name', 'amount', 'measurement_unit',)


class RecipesReadSerializer(serializers.ModelSerializer):
    """ Сериализатор чтения рецептов."""
    tags = serializers.SerializerMethodField()
    ingredients = IngredientsGetSerializer(
        many=True,
        source ='amount_ingredients')
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
    read_only_fields = ('id', 'author', 'is_favorited',
                        'is_favorited')

    def get_tags(self, obj):
        return TagsSerializer(
            Tags.objects.filter(recipes=obj),
            many=True,).data

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipes=obj.id
        ).exists()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return FavoriteResipes.objects.filter(
            user=request.user,
            recipes=obj.id
        ).exists()


class ShortRecipesSerializer(serializers.ModelSerializer):
    """ Сериализатор для краткого отображения сведений о рецепте"""
    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(CustomUserSerializer):
    """ Сериализатор подписок."""
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )
        read_only_fields = ('email', 'username')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Subscriptions.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes_count(self, author):
        return author.recipes.count()

    def get_recipes(self, author):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = author.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipesShortSerializer(recipes, many=True, read_only=True)
        return serializer.data


class RecipesCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True,
    )
    ingredients = IngredientsRecipesSerializer(
        many=True,
        source ='amount_ingredients'
    )
    image = Base64ImageField(max_length=None)
    author = serializers.SlugRelatedField(
        slug_field='username', default=serializers.CurrentUserDefault(),
        write_only=True, queryset=User.objects.all()
    )

    class Meta:
        model = Recipes
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'name', 'image',
            'text', 'cooking_time'
        )

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        if not ingredients:
            raise serializers.ValidationError(
                'Необходим минимум один ингредиент для рецепта'
            )
        if not tags:
            raise serializers.ValidationError(
                'Необходим минимум один тег для рецепта'
            )
        ingredient_list = []
        for ingredient_item in ingredients:
            if not Ingredients.objects.filter(
                    pk=ingredient_item['id']).exists():
                raise serializers.ValidationError(
                    'Ингредиента с таким id не существует'
                )
            if int(ingredient_item['id']) in ingredient_list:
                raise serializers.ValidationError('Укажите уникальный '
                                                  'ингредиент')
            if 'amount' not in ingredient_item:
                raise serializers.ValidationError('Количество ингредиента '
                                                  'не может быть пустым')
            amount = int(ingredient_item['amount'])
            if amount <= 0 or amount > 32766:
                raise serializers.ValidationError(
                    'Укажите корректное количество ингредиента, '
                    'в диапазоне от 1 до 32766'
                )
            ingredient_list.append(ingredient_item['id'])
        data['ingredients'] = ingredients
        data['tags'] = tags
        return data

    @staticmethod
    def create_ingredients(ingredients, recipes):
        """Добавляет ингредиенты в рецепт."""
        ingredients_list = [
            IngredientsRecipes(
                ingredients=get_object_or_404(
                    Ingredients, pk=ingredients.get('id')
                ),
                recipes=recipes, amount=ingredients.get('amount'),
            )
            for ingredients in ingredients
        ]
        ingredients_list.sort(key=(lambda item: item.ingredients.name))
        IngredientsRecipes.objects.bulk_create(ingredients_list)

    def create(self, validated_data):
        ingredients = validated_data.pop('amount_ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        for ingredient in ingredients:
            id = ingredient.get('id')
            amount = ingredient.get('amount')
            ingredient_id = get_object_or_404(Ingredients, id=id)
            IngredientsRecipes.objects.create(
                recipes=recipe, ingredients=ingredient_id, amount=amount
            )
        return recipe

    def update(self, instance, validated_data):
        """Обновляет рецепт."""
        instance.tags.clear()
        instance.ingredients.clear()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('amount_ingredients')
        instance.tags.set(tags)
        self.create_ingredients(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Метод для отображения данных в соответствии с ТЗ."""
        return RecipesReadSerializer(
            instance, context={'request': self.context.get('request')}
        ).data
