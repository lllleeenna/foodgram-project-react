from django.contrib import admin

from recipes.models import (Favorite, Follow, Ingredient, Recipe,
                            RecipeIngredient, RecipeTag, ShoppingCart, Tag)


class RecipeTagInline(admin.TabularInline):
    """Отображение тегов на странице рецепта."""

    model = RecipeTag
    extra = 1


class RecipeIngredientInline(admin.TabularInline):
    """Отображение ингредиентов на странице рецепта."""

    model = RecipeIngredient
    extra = 1


class TagAdmin(admin.ModelAdmin):
    """Класс для работы с тегами в админ-панели."""

    list_display = ('id', 'name', 'color', 'slug',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = (RecipeTagInline,)


class IngredientAdmin(admin.ModelAdmin):
    """Класс для работы с тегами в админ-панели."""

    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    inlines = (RecipeIngredientInline,)


class RecipeAdmin(admin.ModelAdmin):
    """Класс для работы с рецептами в админ-панели."""

    list_display = ('id', 'name', 'author')
    list_filter = ('name', 'author', 'tags',)
    search_fields = ('name', 'author__username',)
    readonly_fields = ('count_favorite',)
    inlines = (RecipeIngredientInline, RecipeTagInline,)
    add_fieldsets = (
        (None, {'fields': ('count_favorite',),}),
    )

    def count_favorite(self, obj):
        return obj.favorites.count()

    count_favorite.short_description = 'Количество добавлений в избранное'


class RecipeTagAdmin(admin.ModelAdmin):
    """Класс для связи рецепта и тегов в админ-панели."""

    list_display = ('id', 'recipe', 'tag',)
    search_fields = ('recipe',)


class RecipeIngredientAdmin(admin.ModelAdmin):
    """Класс для связи рецепта и ингредиентов в админ-панели."""

    list_display = ('id', 'recipe', 'ingredient',)
    search_fields = ('recipe',)


class FollowAdmin(admin.ModelAdmin):
    """Класс для работы с подписками в админ-панели."""

    list_display = ('id', 'user', 'author',)
    search_fields = ('user', 'author',)


class ShoppingCartAdmin(admin.ModelAdmin):
    """Класс для работы со списком покупок в админ-панели."""

    list_display = ('id', 'user', 'recipe',)
    search_fields = ('user', 'recipe', )


class FavoriteAdmin(admin.ModelAdmin):
    """Класс для работы избранными рецептами в админ-панели."""

    list_display = ('id', 'user', 'recipe',)
    search_fields = ('user', 'recipe',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
