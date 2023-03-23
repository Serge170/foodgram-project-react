from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя"""
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=254,
        unique=True,)
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True,)
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=False)
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=False,)
    password = models.CharField(
        verbose_name='Пароль',
        max_length=150,)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    """ Модель подписок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribtions',
        verbose_name='Автор')

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'], name='unique_subscription'
            )
        ]
