''' Настройка админ панели.'''
from django.contrib import admin
from recipes.models import (FavoriteResipes, Ingredients, IngredientsRecipes,
                            Recipes, ShoppingCart, Tags)


class TagsAdmin(admin.ModelAdmin):
    ''' Модель Tags в интерфейсе админ панели.'''
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)


class RecipesAdmin(admin.ModelAdmin):
    ''' Модель Recipes в интерфейсе админ панели.'''
    list_display = ('author', 'name', 'cooking_time', 'ingredients')
    search_fields = ('name', 'author', 'tags')
    list_filter = ('author', 'name', 'tags')


class IngredientsAdmin(admin.ModelAdmin):
    ''' Модель Ingredients в интерфейсе админ панели.'''
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class IngredientsRecipesAdmin(admin.ModelAdmin):
    ''' Модель Ingredients в интерфейсе админ панели.'''
    list_display = (
        'ingredients',
        'recipes',
        'amount',
    )
    empty_value_display = '-пусто-'


class FavoriteResipesAdmin(admin.ModelAdmin):
    ''' Модель FavoriteResipes в интерфейсе админ панели.'''
    list_display = (
        'user',
        'recipes',
    )
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    ''' Модель ShoppingCart в интерфейсе админ панели.'''
    list_display = (
        'user',
        'recipes',
    )
    empty_value_display = '-пусто-'


admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Recipes, RecipesAdmin)
admin.site.register(IngredientsRecipes, IngredientsRecipesAdmin)
admin.site.register(FavoriteResipes, FavoriteResipesAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Tags, TagsAdmin)
