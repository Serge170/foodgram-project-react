''' Создание моделей.'''

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from users.models import User as User


class Tags(models.Model):
    ''' Настройка модели Тэг.'''
    name = models.CharField(max_length=100, verbose_name='Название тега')
    color = models.CharField(
        max_length=100,
        default='#E26C2D',
        verbose_name='Цвет')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='slug')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredients(models.Model):
    ''' Настройка модели Ингридиенты.'''
    name = models.CharField(max_length=100, verbose_name='Название ингридиета')
    measurement_unit = models.CharField(
        max_length=100,
        verbose_name='Единица измерения')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredients'
            )]
        verbose_name = 'Ингридиет'
        verbose_name_plural = 'Ингридиеты '
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipes(models.Model):
    ''' Настройка модели Рецепты.'''
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта')
    name = models.CharField(max_length=100, verbose_name='Название рецепта')
    image = models.ImageField(
        upload_to='recipes/',
        null=True,
        blank=False,
        verbose_name='Изображение')
    text = models.TextField(max_length=1000, verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredients,
        through='IngredientsRecipes',
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты',
        related_name='recipes')
    tags = models.ManyToManyField(
        Tags,
        blank=False,
        null=True,
        verbose_name='tags')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовление',
        validators=[MinValueValidator(1, message='Время меньше 1 минуты'),
                    MaxValueValidator(300, message='Время больше 300 минут'),
                    ])

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientsRecipes(models.Model):
    ''' Модель для настройки количества ингредиентов.'''
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='amount_ingredients',
        verbose_name='Ингредиент',
        help_text='Ингредиент',
    )
    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='amount_ingredients',
        verbose_name='Рецепт',
        help_text='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1, 'Количество ингредиентов меньше 1!'
            ),
            MaxValueValidator(
                100, 'Количество ингредиентов больше 100!')
        ],
        default=1,
        verbose_name='Количество',
        help_text='Количество',
    )

    class Meta:
        verbose_name = 'Количествово ингредиентов'
        verbose_name_plural = 'Количествово ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredients'],
                name='unique_ingredients_in_recipes',
            )
        ]

    def __str__(self):
        return f'{self.ingredients} {self.recipes}'


class FavoriteResipes(models.Model):
    ''' Модель избранных рецептов пользователя.'''
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
    )
    recipes = models.ForeignKey(
        Recipes,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorite_recipes'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class ShoppingCart(models.Model):
    ''' Модель списка покупок.'''
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipes = models.ForeignKey(
        Recipes,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
