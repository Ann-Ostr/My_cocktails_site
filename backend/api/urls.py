from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
)
from api.views import CustomUserViewSet

app_name = 'api'
router = DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredienrs')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')), # Работа с пользователями
    path('auth/', include('djoser.urls.authtoken')), # Работа с токенами
]