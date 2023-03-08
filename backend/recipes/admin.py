from django.contrib import admin

from .models import Tags


class TagsAdmin(admin.ModelAdmin):
    """Тэги с поиском по названию."""
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)


admin.site.register(Tags, TagsAdmin)
