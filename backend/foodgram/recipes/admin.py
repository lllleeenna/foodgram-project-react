from django.contrib import admin

from recipes.models import (
    Tag, Ingredient, Recipe, Follow,
    ShoppingCart, Favorite, RecipeTag, RecipeIngredient
)


class TagAdmin(admin.ModelAdmin):
    """Класс для работы с тегами в админ-панели."""

    list_display = ('id', 'name', 'color', 'slug',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class IngredientAdmin(admin.ModelAdmin):
    """Класс для работы с тегами в админ-панели."""

    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    """Класс для работы с рецепатми в админ-панели."""

    list_display = ('id', 'name', 'author', 'text', 'image')
    search_fields = ('name', 'author',)


class RecipeTagAdmin(admin.ModelAdmin):
    """Класс для связи рецепта и тегов в админ-панели."""
    list_display = ('tag', 'recipe',)


class RecipeIngredientAdmin(admin.ModelAdmin):
    """Класс для связи рецепта и ингредиентов в админ-панели."""
    list_display = ('ingredient', 'recipe',)


class FollowAdmin(admin.ModelAdmin):
    """Класс для работы с подписками в админ-панели."""

    list_display = ('user', 'author',)
    search_fields = ('user', 'author',)


class ShoppingCartAdmin(admin.ModelAdmin):
    """Класс для работы со списком покупок в админ-панели."""

    list_display = ('user', 'recipe',)
    search_fields = ('user', 'recipe', )


class FavoriteAdmin(admin.ModelAdmin):
    """Класс для работы избранными рецептами в админ-панели."""

    list_display = ('user', 'recipe',)
    search_fields = ('user', 'recipe',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)

