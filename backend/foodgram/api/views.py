from django.db.models import Sum, Count
from django.http import HttpResponse
from django.core.files import File
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import (
    TagSerializer, RecipeSerializer, IngredientSerializer,
    RecipeShortSerializer, CustomUserSerializer, FollowUserSerializer
)
from users.models import User
from recipes.models import Tag, Recipe, Ingredient, ShoppingCart, Favorite


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(url_path='subscriptions', methods=['get'], detail=False)
    def get_subscriptions(self, response):
        """Список подписок пользователя."""
        follow = User.objects.filter(author__user=response.user)
        page = self.paginate_queryset(follow)
        # if page is not None:
            # serializer = FollowUserSerializer(page, many=True)
        # return self.get_paginated_response(serializer.data)
        serializer = FollowUserSerializer(follow, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Список тегов, получение тега по id."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Получение списка рецептов, одного рецепта.
    Создание рецепта, обновление и удаление.
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        print('View Recipe creaate')
        print('request_data = ', self.request.data.get('tags'))
        # tags = Tag.objects.filter(id__in=self.request.data.get('tags'))
        # print(tags)
        serializer.save(author=self.request.user)

    @action(url_path='download_shopping_cart', methods=['get'], detail=False)
    def get_sdownload_shopping_cart(self, request):
        """Формирует и возвращает список ингредиентов, на основе рецептов,
        добавленных в список покупок.
        """
        if self.request.user.is_anonymous:
            return HttpResponse(
                'Пользователь не авторизован',
                status=status.HTTP_401_UNAUTHORIZED,
            )

        queryset_shopping_cart = ShoppingCart.objects.filter(
            user=self.request.user
        ).select_related(
            'recipe'
        ).values_list(
            'recipe__recipeingredients__ingredient__name',
            'recipe__recipeingredients__ingredient__measurement_unit'
        ).annotate(
            amount=Sum('recipe__recipeingredients__amount')
        )
        f_name = f'media/shoppingcart/{self.request.user}_shoppingcart.txt'
        with open(f_name, 'w') as f:
            file_shopping = File(f)
            file_shopping.write('Список покупок:\n')
            for ingredient in queryset_shopping_cart:
                file_shopping.write(
                    f'{ingredient[0]}: {ingredient[2]} {ingredient[1]}\n'
                )
        with open(f_name, 'rb') as f:
            return HttpResponse(
                f,
                status=status.HTTP_200_OK,
                headers={
                    'Content - Type': 'text/html; charset=UTF-8',
                    'Content-Disposition': 'attachment; filename="shoppingcart.txt"',
                }
            )

    @action(url_path='shopping_cart', methods=['post', 'delete'], detail=True)
    def get_shopping_cart(self, request, pk):
        """Добавление и удаление рецепта из списка покупок пользователя."""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe):
                return Response(
                    {
                        'errors': f'Рецепт "{recipe}" уже добавлен в список покупок {user}.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(
                RecipeShortSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':
            if not ShoppingCart.objects.filter(user=user, recipe=recipe):
                return Response(
                    {'errors': f'Рецептa "{recipe}" нет в списке покупок {user}.'}
                )
            ShoppingCart.objects.get(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(url_path='favorite', methods=['post', 'delete'], detail=True)
    def get_favorite(self, request, pk):
        """Добавление и удаление рецептов из избранного."""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe):
                return Response(
                    {
                        'errors': f'Рецепт "{recipe}" уже добавлен в избранное {user}.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, recipe=recipe)
            return Response(
                RecipeShortSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':
            if not Favorite.objects.filter(user=user, recipe=recipe):
                return Response(
                    {'errors': f'Рецептa "{recipe}" нет в избранном {user}.'}
                )
            Favorite.objects.get(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
