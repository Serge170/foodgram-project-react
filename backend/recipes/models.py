from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from users.models import User as User

# Create your models here.
"""Рецепт
Рецепт должен описываться такими полями:
Автор публикации (пользователь).
Название.
Картинка.
Текстовое описание.
Ингредиенты: продукты для приготовления блюда по рецепту.
Множественное поле, выбор из предустановленного списка,
с указанием количества и единицы измерения.
Тег (можно установить несколько тегов на один рецепт,
выбор из предустановленных).
Время приготовления в минутах.
Все поля обязательны для заполнения."""


class Tags(models.Model):
    """Тег
Тег должен описываться такими полями:
Название.
Цветовой HEX-код (например, #49B64E).
Slug.
Все поля обязательны для заполнения и уникальны."""
    name = models.CharField(max_length=50, verbose_name='Название тега')
    color = models.CharField(
        'Цвет',
        max_length=7,
        unique=True)
    slug = models.SlugField(max_length=200, unique=True, verbose_name='slug')


class Ingredients(models.Model):
    """Ингредиент
Данные об ингредиентах хранятся в нескольких связанных таблицах.
В результате на стороне пользователя ингредиент
должен описываться такими полями:
Название.
Количество.
Единицы измерения.
Все поля обязательны для заполнения."""
    name = models.CharField(max_length=50, verbose_name='Название ингридиета')
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Единица измерения'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient'
            )]
        verbose_name = 'Ингридиет'
        verbose_name_plural = 'Ингридиеты '
        ordering = ('name', )

    def __str__(self):
        return self.name


class Recipes(models.Model):
    """"Рецепт должен описываться такими полями:
Автор публикации (пользователь).
Название.
Картинка.
Текстовое описание.
Ингредиенты: продукты для приготовления блюда по рецепту.
Множественное поле, выбор из предустановленного списка,
с указанием количества и единицы измерения.
Тег (можно установить несколько тегов на один рецепт,
выбор из предустановленных).
Время приготовления в минутах.
Все поля обязательны для заполнения."""
    """Модель рецепта."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта')
    name = models.CharField(max_length=50, verbose_name='Название рецепта')
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
        related_name='recipes',
        )
    tags = models.ForeignKey(
        Tags,
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        verbose_name='tags'
        )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовление',
        validators=[MinValueValidator(1, message='Время меньше 1 минуты'),
                    MaxValueValidator(1140, message='Время больше 1490 минут'),
                    ])


class IngredientsRecipes(models.Model):
    """Модель для связи рецептов и ингредиентов."""
    recipes = models.ForeignKey(
        Recipes,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredient_recipes'
    )
    ingredient = models.ForeignKey(
        Ingredients,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredient_recipes'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=(
            MinValueValidator(
                1, message='Выберете хотя бы 1 ингредиент.'),
        )
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return (f'{self.ingredient.name} - {self.amount}'
                f' {self.ingredient.measurement_unit}')


class IngredientsAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='amount_ingredient',
        verbose_name='Ингредиент',
        help_text='Ингредиент',
    )
    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='amount_ingredient',
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
        verbose_name = 'Кол-во ингредиентов'
        verbose_name_plural = 'Кол-во ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient'],
                name='unique_ingredient_in_recipes',
            )
        ]

    def __str__(self):
        return f'{self.ingredient} {self.recipes}'


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
        help_text='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Избранный автор',
        help_text='Избранный автор',
    )

    class Meta:
        verbose_name = 'Избранный автор'
        verbose_name_plural = 'Избранные авторы'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_relationships'
            ),
            models.CheckConstraint(
                name='prevent_self_follow',
                check=~models.Q(user=models.F('author')),
            ),
        ]

    def __str__(self):
        return f'{self.user} {self.author}'


class Favorite(models.Model):
    """Модель избранных рецептов пользователя."""
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
    """Модель списка покупок."""
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


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user',
        verbose_name='Автор'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            ),
        ]
        verbose_name_plural = 'Подписки'
        verbose_name = 'Подписка'
