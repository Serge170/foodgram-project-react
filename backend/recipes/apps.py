""" Создание приложения."""
from django.apps import AppConfig


class RecipesConfig(AppConfig):
    """ Создание приложения Recipes."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
