from rest_framework import status
from rest_framework.response import Response

from recipes.models import Follow, Favorite, ShoppingCart


def create_obj(attrs, model, serializer):
    """Создание записей в таблицах Favorite, Follow, ShoppingCart."""
    model_attr = {
        Follow: 'author',
        Favorite: 'recipe',
        ShoppingCart: 'recipe'
    }

    if model.objects.filter(**attrs).exists():
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
