import django_filters

from recipes.models import Recipe, Tag
from users.models import User


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_is_favorited',
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        field_name='in_shopping_cart',
        method='filter_in_shopping_cart'
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = django_filters.ModelChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)

    def filter_is_favorited(self, queryset, name, value):
        print(queryset)
        print(name)
        print(value)
        return queryset.filter(favorites__user=self.request.user)

    def filter_in_shopping_cart(self, queryset, mame, value):
        return queryset.filter(shoppingcarts__user=self.request.user)
