from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from users.models import User
from recipes.validators import validate_amount


class Tag(models.Model):
    """Модель теги."""

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название',
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Цвет',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='URL',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингридиенты."""

    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепты."""

    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    text = models.TextField(verbose_name='Рецепт')
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение',
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления мин.',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        related_name='recipes',
        verbose_name='Теги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингридиенты',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    """Модель для связи тега с рецептами."""

    tag = models.ForeignKey(
        Tag,
        on_delete=models.PROTECT,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Рецепт - Тег'
        verbose_name_plural = 'Рецепты - Теги'
        ordering = ['-id']
        constraints = [
            UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_recipe_tag',
            )
        ]

    def __str__(self):
        return f'{self.recipe.name} - {self.tag.name}'


class RecipeIngredient(models.Model):
    """Модель для связи рецепта и ингредиентов."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipeingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        verbose_name='Ингридиенты',
        related_name='recipeingredients',
    )
    amount = models.PositiveIntegerField(
        validators=[validate_amount],
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Рецепт - Ингредиент'
        verbose_name_plural = 'Рецепты - Ингредиенты'
        ordering = ['-id']
        constraints = [
            UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient',
            )
        ]

    def __str__(self):
        return f'{self.recipe.name} - {self.ingredient.name}'


class Follow(models.Model):
    """Модель подписки на авторов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['user']
        constraints = [
            UniqueConstraint(fields=['user', 'author'], name='unique_follow')
        ]


class ShoppingCart(models.Model):
    """Модель список покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppingcarts',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppingcarts',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ['user']
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopingcart'
            )
        ]


class Favorite(models.Model):
    """Модель избранные рецепты."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ['user']
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]
