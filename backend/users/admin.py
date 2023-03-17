'''Настройка админ панели'''

from django.contrib import admin
from users.models import Subscriptions, User

# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     '''Модель пользователя для админки'''
#     list_display = (
#         'pk',
#         'username',
#         'first_name',
#         'last_name',
#         'email',
#     )
#     list_filter = ('username', 'email')
#     search_fields = ('username', 'email')
#     empty_value_display = '-пусто-'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
    empty_value_display = '-пусто-'
