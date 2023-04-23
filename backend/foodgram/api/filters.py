import django_filters
from rest_framework import filters

from recipes.models import Recipe, Tag
from users.models import User


class RecipeFilter(django_filters.FilterSet):
    """Фильтр для рецептов по тегам и автору."""

    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = django_filters.ModelChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def filter_is_favorited(self, queryset, name, value):
        print(value)
        return queryset.filter(favorites__user=self.request.user)

    def filter_is_in_shopping_cart(self, queryset, mame, value):
        return queryset.filter(shoppingcarts__user=self.request.user)


class IngredientSearchFilter(filters.SearchFilter):
    search_param = 'name'
