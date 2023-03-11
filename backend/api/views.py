from django.http import FileResponse
from api.filters import IngredientsFilter, RecipesFilter
from api.serializers import (CustomUserSerializer, IngredientsSerializer,
                             RecipesReadSerializer, RecipesCreateSerializer,
                             SubscriptionsSerializer, TagsSerializer)
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (FavoriteResipes, Ingredients, IngredientsRecipes,
                            Recipes, ShoppingCart, Subscriptions, Tags)
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import User

from .pagination import LimitPageNumberPagination
from .permissions import IsAuthorOrReadOnly


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    search_fields = ('username', 'email')
    permission_classes = (AllowAny)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        queryset = Subscriptions.objects.filter(user=user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = SubscriptionsSerializer(
                Subscriptions.objects.create(user=request.user, author=author),
                context={'request': request},
            )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        Subscriptions.objects.filter(user=request.user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = IngredientsFilter


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesReadSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipesReadSerializer
        return RecipesCreateSerializer

    def post_del_recipes(self, request, pk, database):
        recipes = get_object_or_404(Recipes, id=pk)
        if request.method == 'POST':
            if not database.objects.filter(
                    user=self.request.user,
                    recipes=recipes).exists():
                database.objects.create(
                    user=self.request.user,
                    recipes=recipes)
                serializer = SubscriptionsSerializer(recipes)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            text = 'errors: Объект уже в списке.'
            return Response(text, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            if database.objects.filter(
                    user=self.request.user,
                    recipes=recipes).exists():
                database.objects.filter(
                    user=self.request.user,
                    recipes=recipes).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            text = 'errors: Объект не в списке.'
            return Response(text, status=status.HTTP_400_BAD_REQUEST)

        else:
            text = 'errors: Метод обращения недопустим.'
            return Response(text, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        return self.post_del_recipes(request, pk, FavoriteResipes)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.post_del_recipes(request, pk, ShoppingCart)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Скачивает список покупок"""
        user = request.user
        purchases = ShoppingCart.objects.filter(user=user)
        file = 'shopping-list.txt'
        with open(file, 'w') as f:
            shop_cart = dict()
            for purchase in purchases:
                ingredients = IngredientsRecipes.objects.filter(
                    recipes=purchase.recipes.id
                )
                for r in ingredients:
                    i = Ingredients.objects.get(pk=r.ingredients.id)
                    point_name = f'{i.name} ({i.measurement_unit})'
                    if point_name in shop_cart.keys():
                        shop_cart[point_name] += r.amount
                    else:
                        shop_cart[point_name] = r.amount

            for name, amount in shop_cart.items():
                f.write(f'* {name} - {amount}\n')

        return FileResponse(open(file, 'rb'), as_attachment=True)
