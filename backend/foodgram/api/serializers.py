from rest_framework import serializers

from core.models import Recipe, Subscription, User


class UserAccountSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField('get_is_subscribed')

    def get_is_subscribed(self, obj):
        user = getattr(self.context.get('request'), 'user')
        if user and user.is_authenticated:
            return (
                user.is_authenticated
                and
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


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name'
        ]


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField('get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField('get_is_in_shopping_cart')

    def get_is_favorited(self, obj):
        return False # TODO

    def get_is_in_shopping_cart(self, obj):
        return False # TODO

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