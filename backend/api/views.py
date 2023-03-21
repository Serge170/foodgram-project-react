''' Настройка Вьюсетов.'''
from api.filters import IngredientsFilter, RecipesFilter
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAuthorAdminOrReadOnly
from api.serializers import (FavoriteResipesSerializer, IngredientsSerializer,
                             RecipesCreateSerializer, RecipesReadSerializer,
                             SubscriptionsSerializer, TagsSerializer)
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (FavoriteResipes, Ingredients, IngredientsRecipes,
                            Recipes, ShoppingCart, Tags)
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    ''' Вьюсет тэгов.'''
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    ''' Вьюсет ингредиентов.'''
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = IngredientsFilter


class RecipesViewSet(viewsets.ModelViewSet):
    ''' Вьюсет рецептов.'''
    queryset = Recipes.objects.all()
    serializer_class = RecipesReadSerializer
    permission_classes = (IsAuthorAdminOrReadOnly,)
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
    def shopping_cart(self, request, pk):
        return self.post_del_recipes(request, pk, ShoppingCart)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ''' Скачивает список покупок.'''
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

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=FavoriteResipesSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=FavoriteResipes)

    @staticmethod
    def delete_method_for_actions(request, pk, model):
        user = request.user
        recipes = get_object_or_404(Recipes, id=pk)
        model_obj = get_object_or_404(model, user=user, recipes=recipes)
        model_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def post_method_for_actions(request, pk, serializers):
        data = {'user': request.user.id, 'recipes': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
