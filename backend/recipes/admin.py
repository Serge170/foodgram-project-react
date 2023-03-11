from django.contrib import admin

from .models import (FavoriteResipes, Follow, Ingredients, IngredientsRecipes,
                     Recipes, ShoppingCart, Tags)


class TagsAdmin(admin.ModelAdmin):
    """Тэги с поиском по названию."""
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)


class RecipesAdmin(admin.ModelAdmin):
    """"""
    list_display = ('author', 'name', 'cooking_time')
    search_fields = ('name', 'author', 'tags')
    list_filter = ('author', 'name', 'tags')


class IngredientsAdmin(admin.ModelAdmin):
    """"""
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class IngredientsRecipesAdmin(admin.ModelAdmin):
    """"""
    list_display = (
        'ingredient',
        'recipes',
        'amount',
    )
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    """"""
    list_display = (
        'user',
        'author',
    )
    empty_value_display = '-пусто-'


class FavoriteResipesAdmin(admin.ModelAdmin):
    """"""
    list_display = (
        'user',
        'recipes',
    )
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    """"""
    list_display = (
        'user',
        'recipes',
    )
    empty_value_display = '-пусто-'


admin.site.register(Follow, FollowAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Recipes, RecipesAdmin)
admin.site.register(IngredientsRecipes, IngredientsRecipesAdmin)
admin.site.register(FavoriteResipes, FavoriteResipesAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Tags, TagsAdmin)
