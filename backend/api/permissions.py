"""Файл настроки уровней доступа"""
from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Настройка доступа на чтение"""
    message = 'Редактирование чужого рецепта запрещено!'

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Настройка доступа на редактирование"""
    message = 'Редактировать контент может только администратор!'

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS or request.user.is_staff
        )
