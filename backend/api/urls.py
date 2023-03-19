''' Urls.'''
from api.views import IngredientsViewSet, RecipesViewSet, TagsViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views import CustomUserViewSet, UsersListView, UsersViewSet

app_name = 'api'

router = DefaultRouter()

router.register('users', CustomUserViewSet, basename='users')
router.register('ingredients', IngredientsViewSet)
router.register('ingredients', IngredientsViewSet)
router.register('tags', TagsViewSet)
router.register('recipes', RecipesViewSet)

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
]
