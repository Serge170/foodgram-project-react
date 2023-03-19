'''Настройка админ панели'''

from django.contrib import admin
from users.models import Subscriptions, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    '''Модель пользователя для админки'''
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')
    empty_value_display = '-пусто-'


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    '''Модель подписки для админки'''
    list_display = ('id', 'user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
    empty_value_display = '-пусто-'
