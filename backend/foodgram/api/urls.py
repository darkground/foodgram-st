from django.urls import path, include

from rest_framework.routers import SimpleRouter

from .views import (
    IngredientViewSet,
    RecipeViewSet,
    UserAccountViewSet
)

router = SimpleRouter()
router.register('users', UserAccountViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]