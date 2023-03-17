''' Определяем Urls.'''
from api.views import (CustomUserViewSet, IngredientsViewSet, RecipesViewSet,
                       TagsViewSet, UsersListView, UsersViewSet)
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path(
        'users/subscriptions/',
        UsersListView.as_view(),
        name='subscriptions'
    ),
    path(
        'users/<int:user_id>/subscribe/',
        UsersViewSet.as_view(),
        name='subscribe'
    ),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
