from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        db_index=True,
        max_length=50,
        verbose_name='Электронная почта',
        help_text='Адрес электронной почты',
    )
    username = models.CharField(
        unique=True,
        db_index=True,
        max_length=100,
        verbose_name='Логин',
        help_text='Логин пользователя',
    )
    password = models.CharField(
        max_length=255,
        verbose_name='Пароль',
        help_text='Пароль пользователя',
    )
    first_name = models.CharField(
        max_length=50,
        verbose_name='Имя пользователя',
        help_text='Имя пользователя',
    )
    last_name = models.CharField(
        max_length=50,
        verbose_name='Фамилия',
        help_text='Фамилия',
    )
    is_subcribed = models.BooleanField(
        default=False,
        verbose_name='Подписка на автора',
        help_text='Отметьте для подписки на автора',
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username
