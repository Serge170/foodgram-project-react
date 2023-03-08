"""Файл для настройки пагинации"""
from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """Настраиваем пагинацию, 6 рецептов на страницу"""
    page_size = 6
    page_size_query_param = 'limit'
