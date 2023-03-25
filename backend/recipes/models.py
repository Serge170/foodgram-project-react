""" Создание моделей."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from users.models import User as User


class Tags(models.Model):
    """ Настройка модели Тэг."""
    name = models.CharField(max_length=100, verbose_name='Название тега')
    color = models.CharField(
        max_length=100,
        default='#E26C2D',
        verbose_name='Цвет')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='slug')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    """ Настройка модели Ингридиенты."""
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
        return f'{self.name}, {self.measurement_unit}'


class Recipes(models.Model):
    """ Настройка модели Рецепты."""
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
    text = models.TextField(max_length=1500, verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredients,
        through='IngredientsRecipes',
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты',
        related_name='recipes')
    tags = models.ManyToManyField(
        Tags,
        blank=False,
        verbose_name='tags')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1, 'Время приготовления не может быть меньше 1 минуты!'
            ),
            MaxValueValidator(
                1441, 'Время приготовления не может быть более 24 часов!'
            )
        ],
        default=1,
        verbose_name='Время приготовления',
        help_text='Время приготовления в минутах',
    )
    
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientsRecipes(models.Model):
    """ Модель для настройки количества ингредиентов."""
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
                1, 'Количество ингредиентов не может быть меньше 1!'
            ),
            MaxValueValidator(
                1000, 'Количество ингредиентов не может быть больше 1000!'
            )
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
        return f'{self.ingredients} – {self.amount}'


class FavoriteResipes(models.Model):
    """ Модель избранных рецептов пользователя."""
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

    def __str__(self):
        return f'{self.user} добавил "{self.recipes}" в Избранное'


class ShoppingCart(models.Model):
    """ Модель списка покупок."""
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

    def __str__(self):
        return f'{self.user} добавил "{self.recipes}" в свою корзину'
