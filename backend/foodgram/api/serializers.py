from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .fields import Base64ImageField
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор модели User."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Вычисление значения поля is_subscribed."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=obj.id).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор модели User для создания пользователя."""
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с таким email уже существует.'
            )
        ]
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'required': True},
        }


class TagSerializer(serializers.ModelSerializer):
    """Сериализация тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализация ингредиентов. """

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализация модели RecipeIngredient, для отображения в рецептах
    количества ингредиентов.
    """

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов, с перечнем ингредиентов и тегов."""

    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipeingredients', read_only=True
    )
    image = Base64ImageField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time',
        )

    def get_is_favorited(self, obj):
        """Вычисление значения поля is_favorited."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(favorites__user=user, id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        """Вычисление значения поля is_in_shopping_cart."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shoppingcarts.filter(recipe=obj.id).exists()

    @staticmethod
    def create_ingredients(recipe, ingredients):
        """Добавление ингредиентов в рецепт."""
        objs = (
            RecipeIngredient(
                recipe=recipe,
                ingredient=get_object_or_404(
                    Ingredient, id=ingredient.get('id')
                ),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients
        )
        RecipeIngredient.objects.bulk_create(objs)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        super().update(instance, validated_data)
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_ingredients(instance, ingredients)
        return instance

    def validate_ingredients(self):
        ingredients = self.initial_data.get('ingredients')
        if ingredients is None:
            raise serializers.ValidationError(
                'Список ингредиентов отсутствует.'
            )

        if len(ingredients) == 0:
            raise serializers.ValidationError(
                'Список ингредиентов пуст.'
            )

        id_ingredients = [ingredient.get('id') for ingredient in ingredients]
        if len(set(id_ingredients)) < len(id_ingredients):
            raise serializers.ValidationError(
                'Выбрано два одинаковых ингредиента.'
            )

        for ingredient in ingredients:
            amount = ingredient.get('amount')
            if isinstance(amount, str) and not amount.isdigit():
                raise serializers.ValidationError(
                    'Количество ингредиентов должно быть положительным числом.'
                )
            if int(ingredient.get('amount')) <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиентов не может быть меньше/равно нулю.'
                )

        return ingredients

    def validate_tags(self) -> list[Tag]:
        tags = self.initial_data.get('tags')
        if tags is None:
            raise serializers.ValidationError(
                'Список тегов отсутствует.'
            )
        if len(tags) == 0:
            raise serializers.ValidationError(
                'Не выбрано ни одного тега.'
            )
        unique_tags = []
        for tag in tags:
            tag_obj = get_object_or_404(Tag, id=tag)
            if tag_obj in unique_tags:
                raise serializers.ValidationError(
                    'Выбрано два одинаковых тега.'
                )
            unique_tags.append(tag_obj)
        return unique_tags

    def validate(self, data):
        data['ingredients'] = self.validate_ingredients()
        data['tags'] = self.validate_tags()

        return super().validate(data)


class RecipeShortSerializer(serializers.ModelSerializer):
    """Краткая форма рецепта, для использования в некоторых ViewSet."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowUserSerializer(serializers.ModelSerializer):
    """Сериализация модели User для подписок."""

    recipes = RecipeShortSerializer(read_only=True, many=True)
    recipe_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipe_count',
        )
        read_only_fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipe_count',
        )

    def get_recipe_count(self, obj):
        """Вычисляет количество рецептов автора."""
        return Recipe.objects.filter(author=obj).count()

    def get_is_subscribed(self, obj):
        """Авторы в списке подписок всегда имеют признак is_subscribed=True."""
        return True
