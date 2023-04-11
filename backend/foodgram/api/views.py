from djoser.views import UserViewSet
from rest_framework import viewsets

from .serializers import (
    CustomUserSerializer, TagSerializer, RecipeSerializer,
    IngredientSerializer, #IngredientAmountSerializer,
)
from users.models import User
from recipes.models import Tag, Recipe, Ingredient


# class CustomUserViewSet(UserViewSet):
#     queryset = User.objects.all()
#     serializer_class = CustomUserSerializer


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


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


# class IngredientAmountViewSet(viewsets.ReadOnlyModelViewSet):
#     """Список ингредиентов и количество для рецепта."""
#     serializer_class = IngredientAmountSerializer
#
#     def get_queryset(self):
#         print('*************')
#         print(self.kwargs)
