''' Файл настройки селиализаторов.'''
from api.fields import Base64ImageField
from recipes.models import (FavoriteResipes, Ingredients, IngredientsRecipes,
                            Recipes, ShoppingCart, Tags)
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from users.models import Subscriptions
from users.serializers import CustomUserSerializer
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

class RecipesShortSerializer(serializers.ModelSerializer):
    ''' Сериализатор полей избранных рецептов и покупок.'''

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientsSerializer(serializers.ModelSerializer):
    ''' Сериализатор полей ингридиентов.'''
    class Meta:
        model = Ingredients
        fields = '__all__'


class ShoppingCartSerializer(serializers.ModelSerializer):
    ''' Сериализатор для списка покупок.'''
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


class FavoriteResipesSerializer(serializers.ModelSerializer):
    ''' Сериализатор избранных рецептов.'''
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
    ''' Сериализатор просмотра тегов.'''
    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')


class IngredientsRecipesSerializer(serializers.ModelSerializer):
    ''' Сериализатор связи ингридиентов и рецетов.'''
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientsRecipes
        fields = ('id', 'amount')


class IngredientsGetSerializer(serializers.ModelSerializer):
    ''' Сериализатор получения ингридиентов.'''
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit')

    class Meta:
        model = IngredientsRecipes
        fields = ('id', 'name', 'amount', 'measurement_unit',)


class RecipesReadSerializer(serializers.ModelSerializer):
    ''' Сериализатор чтения рецептов.'''
    tags = serializers.SerializerMethodField()
    ingredients = IngredientsGetSerializer(
        many=True,
        source='amount_ingredients')
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


class ShortRecipesSerializer(serializers.ModelSerializer):
    ''' Сериализатор для краткого отображения сведений о рецепте'''
    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(CustomUserSerializer):
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


# class RecipesCreateSerializer(serializers.ModelSerializer):
#     ''' Сериализатор создания рецептов.'''
#     tags = serializers.PrimaryKeyRelatedField(
#         queryset=Tags.objects.all(),
#         many=True)
#     ingredients = IngredientsRecipesSerializer(
#         many=True,
#         source='amount_ingredients')
#     image = Base64ImageField()

#     class Meta:
#         model = Recipes
#         fields = (
#             'tags',
#             'ingredients',
#             'name',
#             'image',
#             'text',
#             'cooking_time',
#         )

#     def validate(self, data):
#         request = self.context.get('request', None)
#         tags_list = []
#         ingredients_list = []
#         request_methods = ['POST', 'PATCH']

#         if request.method in request_methods:
#             if 'tags' in data:
#                 tags = data['tags']

#                 for tag in tags:
#                     if tag.id in tags_list:
#                         raise serializers.ValidationError(
#                             F'Тег {tag} повторяется')
#                     tags_list.append(tag.id)

#                 if len(tags_list) == 0:
#                     raise serializers.ValidationError(
#                         'Список тегов не должен быть пустым')
#                 all_tags = Tags.objects.all().values_list('id', flat=True)
#                 if not set(tags_list).issubset(all_tags):
#                     raise serializers.ValidationError(
#                         F'Тега {tag} не существует')
#             if 'amount_ingredients' in data:
#                 ingredients = data['amount_ingredients']
#                 for ingredients in ingredients:
#                     ingredients = ingredients['ingredients'].get('id')

#                     if ingredients in ingredients_list:
#                         raise serializers.ValidationError(
#                             F'Ингредиент {ingredients} повторяется')
#                     ingredients_list.append(ingredients)

#                 all_ingredients = Ingredients.objects.all().values_list(
#                     'id', flat=True)

#                 if not set(ingredients_list).issubset(all_ingredients):
#                     raise serializers.ValidationError(
#                         'Указанного ингредиента не существует')

#                 if len(ingredients_list) == 0:
#                     raise serializers.ValidationError(
#                         'Список ингредиентов не должен быть пустым')
#         return data

#     @staticmethod
#     def create_ingredients(recipes, ingredients):
#         ingredients_liist = []
#         for ingredients_data in ingredients:
#             ingredients_obj = Ingredients.objects.get(
#                 id=ingredients_data.get('ingredients')['id'])
#             ingredients_liist.append(
#                 IngredientsRecipes(
#                     ingredients=ingredients_obj,
#                     amount=ingredients_data.get('amount'),
#                     recipes=recipes,
#                 )
#             )
#         IngredientsRecipes.objects.bulk_create(ingredients_liist)

#     def create(self, validated_data):
#         request = self.context.get('request', None)
#         tags = validated_data.pop('tags')
#         ingredients = validated_data.pop('amount_ingredients')
#         recipes = Recipes.objects.create(author=request.user, **validated_data)
#         recipes.tags.set(tags)
#         self.create_ingredients(recipes, ingredients)
#         return recipes

#     def update(self, instance, validated_data):
#         instance.tags.clear()
#         IngredientsRecipes.objects.filter(recipes=instance).delete()
#         instance.tags.set(validated_data.pop('tags'))
#         ingredients = validated_data.pop('amount_ingredients')
#         self.create_ingredients(instance, ingredients)
#         return super().update(instance, validated_data)

#     def to_representation(self, instance):
#         return RecipesReadSerializer(instance, context={
#             'request': self.context.get('request')
#         }).data
    

class RecipesCreateSerializer(ModelSerializer):
    ''' Сериализатор создания рецептов.'''
    tags = serializers.PrimaryKeyRelatedField(queryset=Tags.objects.all(),
                                  many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientsRecipesSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError({
                'ingredients': 'Нужен хотя бы один ингредиент!'
            })
        ingredients_list = []
        for item in value:
            ingredient = get_object_or_404(Ingredients, id=item['id'])
            if ingredient in ingredients_list:
                raise ValidationError({
                    'ingredients': 'Ингридиенты не должны повторяться!'
                })
            if int(item['amount']) <= 0:
                raise ValidationError({
                    'amount': 'Количество ингредиента должно быть больше 0!'
                })
            ingredients_list.append(ingredient)
        return value

    def validate_tags(self, value):
        if not value:
            raise ValidationError({
                'tags': 'Нужно выбрать хотя бы один тег!'
            })
        tags_set = set(value)
        if len(value) != len(tags_set):
            raise ValidationError({
                'tags': 'Теги должны быть уникальными!'
            })
        return value

    def create_ingredients_amounts(self, ingredients, recipes):
        for ingredient in ingredients:
            ing, _ = IngredientsRecipesSerializer.objects.get_or_create(
                ingredient=get_object_or_404(
                    Ingredients.objects.filter(id=ingredient['id'])
                ),
                amount=ingredient['amount'],
            )
            recipes.ingredients.add(ing.id)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipes = Recipes.objects.create(**validated_data)
        recipes.tags.set(tags)
        self.create_ingredients_amounts(recipes=recipes,
                                        ingredients=ingredients)
        return recipes

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amounts(recipes=instance,
                                        ingredients=ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipesReadSerializer(instance,
                                    context=context).data
