"""Файл настройки селиализаторов"""
from api.fields import Base64ImageField, Hex2NameColor
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (FavoriteResipes, Ingredients, IngredientsRecipes,
                            Recipes, ShoppingCart, Subscriptions, Tags)
from rest_framework import serializers
from users.models import User


class CreateUserSerializer(UserCreateSerializer):
    """Создание пользователя селиализаторов"""
    class Meta:
        model = User
        fields = ('email', 'password', 'username', 'first_name', 'last_name',)
        extra_kwargs = {'password': {'write_only': True}}


class CustomUserSerializer(UserSerializer):
    """Получение пользователя селиализаторов"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Subscriptions.objects.filter(
            user=user, author=obj
        ).exists() if user.is_authenticated else False


class SubscribeRecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time',)


class SubscriptionsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='author.id')
    email = serializers.EmailField(source='author.email')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'recipes', 'is_subscribed', 'recipes_count',)

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = Recipes.objects.filter(author=obj.author)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = SubscribeRecipesSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipes.objects.filter(author=obj.author).count()

    def get_is_subscribed(self, obj):
        return Subscriptions.objects.filter(
            user=obj.user,
            author=obj.author
        ).exists()


class TagsSerializer(serializers.ModelSerializer):
    """ Сериализатор просмотра тегов """
    color = Hex2NameColor()

    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = '__all__'


class IngredientsGetSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientsRecipes
        fields = ('id', 'name', 'amount', 'measurement_unit',)


class IngredientsRecipesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientsRecipes
        fields = ('id', 'amount')


class RecipesReadSerializer(serializers.ModelSerializer):
    """Сериализатор чтения рецептов"""

    tags = serializers.SerializerMethodField()
    ingredients = IngredientsGetSerializer(
        many=True,
        source='amount_ingredient')
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
        request = self.context.get('request', None)
        if request:
            current_user = request.user
        return ShoppingCart.objects.filter(
            user=current_user.id,
            recipes=obj.id,
        ).exists()

    def get_is_favorited(self, obj):
        request = self.context.get('request', None)
        if request:
            current_user = request.user
        return FavoriteResipes.objects.filter(
            user=current_user.id,
            recipes=obj.id
        ).exists()


class RecipesCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов"""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True)
    ingredients = IngredientsRecipesSerializer(
        many=True,
        source='amount_ingredient')
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = (
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        request = self.context.get('request', None)
        tags_list = []
        ingredients_list = []
        request_methods = ['POST', 'PATCH']

        if request.method in request_methods:
            if 'tags' in data:
                tags = data['tags']

                for tag in tags:
                    if tag.id in tags_list:
                        raise serializers.ValidationError(
                            F'Тег {tag} повторяется')
                    tags_list.append(tag.id)

                if len(tags_list) == 0:
                    raise serializers.ValidationError(
                            'Список тегов не должен быть пустым')
                all_tags = Tags.objects.all().values_list('id', flat=True)
                if not set(tags_list).issubset(all_tags):
                    raise serializers.ValidationError(
                        F'Тега {tag} не существует')

            if 'amount_ingredient' in data:
                ingredients = data['amount_ingredient']
                for ingredient in ingredients:
                    ingredient = ingredient['ingredient'].get('id')

                    if ingredient in ingredients_list:
                        raise serializers.ValidationError(
                            F'Ингредиент {ingredient} повторяется')
                    ingredients_list.append(ingredient)

                all_ingredients = Ingredients.objects.all().values_list(
                    'id', flat=True)

                if not set(ingredients_list).issubset(all_ingredients):
                    raise serializers.ValidationError(
                        'Указанного ингредиента не существует')

                if len(ingredients_list) == 0:
                    raise serializers.ValidationError(
                        'Список ингредиентов не должен быть пустым')
        return data

    @staticmethod
    def create_ingredients(recipes, ingredients):
        ingredient_liist = []
        for ingredient_data in ingredients:
            ingredient_obj = Ingredients.objects.get(
                id=ingredient_data.get('ingredient')['id'])
            ingredient_liist.append(
                IngredientsRecipes(
                    ingredient=ingredient_obj,
                    amount=ingredient_data.get('amount'),
                    recipes=recipes,
                )
            )
        IngredientsRecipes.objects.bulk_create(ingredient_liist)

    def create(self, validated_data):
        request = self.context.get('request', None)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('amount_ingredient')
        recipes = Recipes.objects.create(author=request.user, **validated_data)
        recipes.tags.set(tags)
        self.create_ingredients(recipes, ingredients)
        return recipes

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientsRecipes.objects.filter(recipes=instance).delete()
        instance.tags.set(validated_data.pop('tags'))
        ingredients = validated_data.pop('amount_ingredient')
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipesReadSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class RecipesShortSerializer(serializers.ModelSerializer):
    """ Сериализатор полей избранных рецептов и покупок """

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteResipesSerializer(serializers.ModelSerializer):
    """  Сериализатор избранных рецептов """

    class Meta:
        model = FavoriteResipes
        fields = ('user', 'recipes',)

    def validate(self, data):
        user = data['user']
        if user.favorites.filter(recipes=data['recipes']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное.'
            )
        return data

    def to_representation(self, instance):
        return RecipesShortSerializer(
            instance.recipes,
            context={'request': self.context.get('request')}
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок """

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipes',)

    def validate(self, data):
        user = data['user']
        if user.shopping_list.filter(recipes=data['recipes']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в корзину'
            )
        return data

    def to_representation(self, instance):
        return RecipesShortSerializer(
            instance.recipes,
            context={'request': self.context.get('request')}
        ).data
