from django.urls import include, path
from djoser.views import TokenCreateView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from .views import (
    TagViewSet, RecipeViewSet, IngredientViewSet, CustomUserViewSet,
)

app_name = 'api'

router = DefaultRouter()

router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    # path('auth/token/login/', TokenCreateView.as_view())
    path('auth/', include('djoser.urls.authtoken')),
]


