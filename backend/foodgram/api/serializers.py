from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from drf_extra_fields import fields as drfx_fields

from core.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Subscription,
    User
)

from core.const import (
    MIN_COOKING_TIME,
    MAX_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT,
    MAX_INGREDIENT_AMOUNT
)


class UserAccountSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField('get_is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user:
            return (
                user.is_authenticated
                and user.subscribers.filter(subscribed_to__exact=obj).exists()
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
        extra_kwargs = {'password': {'write_only': True}}


class AvatarUploadSerializer(serializers.ModelSerializer):
    avatar = drfx_fields.Base64ImageField()

    def update(self, instance, validated_data):
        avatar = validated_data.get('avatar')
        if avatar is None:
            raise serializers.ValidationError(
                {'avatar': 'Это поле является обязательным.'}
            )

        instance.avatar = avatar
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('avatar',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = [
            'id',
            'name',
            'measurement_unit'
        ]


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = [
            'id',
            'name',
            'measurement_unit',
            'amount'
        ]


class IngredientInRecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        min_value=MIN_INGREDIENT_AMOUNT, max_value=MAX_INGREDIENT_AMOUNT)

    class Meta:
        model = IngredientInRecipe
        fields = [
            'id',
            'amount'
        ]


class RecipeSerializer(serializers.ModelSerializer):
    author = UserAccountSerializer()
    ingredients = IngredientInRecipeSerializer(
        source="ingredient_amounts", many=True)
    is_favorited = serializers.SerializerMethodField('get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user:
            return (
                user.is_authenticated
                and user.favorites.filter(recipe__exact=obj).exists()
            )
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user:
            return (
                user.is_authenticated
                and user.shopping_cart.filter(recipe__exact=obj).exists()
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


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeCreateSerializer(many=True)
    image = drfx_fields.Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME, max_value=MAX_COOKING_TIME)

    class Meta:
        model = Recipe
        fields = [
            'name',
            'image',
            'text',
            'cooking_time',
            'ingredients'
        ]

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError(
                'Картинка является обязательным полем.')
        return image

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Ингредиенты является обязательным полем.')

        ids = [ingredient['ingredient'].id for ingredient in ingredients]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальны.')

        return ingredients

    def make_ingredients(self, recipe, ingredients):
        return IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ])

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.make_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = self.validate_ingredients(
            validated_data.pop('ingredients', None))
        instance.ingredient_amounts.all().delete()
        self.make_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time'
        ]


class UserWithRecipeSerializer(UserAccountSerializer):
    recipes = serializers.SerializerMethodField('get_recipes')
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
            'recipes',
            'recipes_count'
        ]

    def get_recipes(self, obj):
        request = self.context['request']
        query_params = request.query_params

        recipes = obj.recipes.all()
        recipes_limit = query_params.get("recipes_limit")

        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]

        return RecipeShortSerializer(
            recipes, context={"request": request}, many=True).data


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = [
            "user",
            "subscribed_to"
        ]

    def validate(self, data):
        user = data.get('user')
        subscriber = data.get('subscribed_to')
        if user == subscriber:
            raise serializers.ValidationError(
                'Нельзя подписаться на себя')
        sub = subscriber.subscribed.filter(user=user)
        if sub.exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя')
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = [
            'user',
            'recipe'
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = [
            'user',
            'recipe'
        ]
