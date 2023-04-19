import os.path

from django.core.files import File
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from foodgram.settings import MEDIA_ROOT
from recipes.models import (Favorite, Follow, Ingredient, Recipe, ShoppingCart,
                            Tag)
from users.models import User
from .filters import RecipeFilter
from .paginations import PageNumberPaginationLimit
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnlyPermission
from .serializers import (CustomUserSerializer, FollowUserSerializer,
                          IngredientSerializer, RecipeSerializer,
                          RecipeShortSerializer, TagSerializer)


def create_obj(attrs, model, serializer):
    """Создание записей в таблицах Favorite, Follow, ShoppingCart."""
    model_attr = {
        Follow: 'author',
        Favorite: 'recipe',
        ShoppingCart: 'recipe'
    }

    if model.objects.filter(**attrs):
        return Response(
            {'errors': 'Запись уже существует.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    model.objects.create(**attrs)
    return Response(
        serializer(attrs.get(model_attr[model])).data,
        status=status.HTTP_201_CREATED
    )


def delete_obj(attrs, model):
    """Удаление записей из таблиц Favorite, Follow, ShoppingCart."""
    if not model.objects.filter(**attrs):
        return Response(
            {'errors': 'Запись отсутствует.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    model.objects.get(**attrs).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class CustomUserViewSet(UserViewSet):
    """Получение списка пользователей, профиль пользователя,
    текущего пользователя.
    Подписки пользователя, подписаться на пользователя, удалить подписку
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAdminOrReadOnly,)

    @action(
        url_path='subscriptions',
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def get_subscriptions(self, response):
        """Подписки пользователя."""
        follow = User.objects.filter(author__user=response.user)
        serializer = FollowUserSerializer(follow, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        url_path='subscribe',
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def get_subscribe(self, request, id):
        """Подписаться на автора, удалить подписку."""
        attrs = {
            'user': request.user,
            'author': get_object_or_404(User, pk=id)
        }

        if request.method == 'POST':
            if attrs.get('user') == attrs.get('author'):
                return Response(
                    {'errors': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return create_obj(attrs, Follow, FollowUserSerializer)
        if request.method == 'DELETE':
            return delete_obj(attrs, Follow)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Список тегов, получение тега по id."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Получение списка рецептов, одного рецепта.
    Создание рецепта, обновление и удаление.
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnlyPermission,)
    pagination_class = PageNumberPaginationLimit
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        url_path='download_shopping_cart',
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def get_download_shopping_cart(self, request):
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
                    'Content-Disposition': (
                                               'attachment;'
                                               'filename="shoppingcart.txt"',
                    )
                }
            )

    @action(
        url_path='shopping_cart',
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def get_shopping_cart(self, request, pk):
        """Добавление и удаление рецепта из списка покупок пользователя."""
        attrs = {
            'user': request.user,
            'recipe': get_object_or_404(Recipe, pk=pk)
        }

        if request.method == 'POST':
            return create_obj(attrs, ShoppingCart, RecipeShortSerializer)
        if request.method == 'DELETE':
            return delete_obj(attrs, ShoppingCart)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        url_path='favorite',
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def get_favorite(self, request, pk):
        """Добавление и удаление рецептов из избранного."""
        attrs = {
            'user': request.user,
            'recipe': get_object_or_404(Recipe, pk=pk)
        }

        if request.method == 'POST':
            return create_obj(attrs, Favorite, RecipeShortSerializer)
        if request.method == 'DELETE':
            return delete_obj(attrs, Favorite)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def perform_destroy(self, instance):
        image_path = os.path.join(MEDIA_ROOT, str(instance.image))
        os.remove(image_path)
        instance.delete()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
