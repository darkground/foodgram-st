from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from core.models import Favorite, Ingredient, IngredientInRecipe, Recipe, ShoppingCart, Subscription, User


class UserAccountSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField('get_is_subscribed')

    def get_is_subscribed(self, obj):
        user = getattr(self.context.get('request'), 'user')
        if user:
            return (
                user.is_authenticated and
                Subscription.objects.filter(user__exact=user, subscribed_to__exact=obj).exists()
            )
        return False

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        ]


class UserRegisterSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        ]
        extra_kwargs = {"password": {"write_only": True}}


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = [
            'id',
            'name',
            'measurement_unit'
        ]


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientInRecipe
        fields = [
            'id',
            'name',
            'measurement_unit',
            'amount'
        ]


class RecipeSerializer(serializers.ModelSerializer):
    author = UserAccountSerializer()
    ingredients = IngredientInRecipeSerializer(source="ingredient_amounts", many=True)
    is_favorited = serializers.SerializerMethodField('get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField('get_is_in_shopping_cart')

    def get_is_favorited(self, obj):
        user = getattr(self.context.get('request'), 'user')
        if user:
            return (
                user.is_authenticated and
                Favorite.objects.filter(user__exact=user, recipe__exact=obj).exists()
            )
        return False

    def get_is_in_shopping_cart(self, obj):
        user = getattr(self.context.get('request'), 'user')
        if user:
            return (
                user.is_authenticated and
                ShoppingCart.objects.filter(user__exact=user, recipe__exact=obj).exists()
            )
        return False

    class Meta:
        model = Recipe
        fields = [
            'id',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        ]