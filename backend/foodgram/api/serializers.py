from rest_framework import serializers

from core.models import Subscription, User

class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField('get_is_subscribed')

    def get_is_subscribed(self, obj):
        user = getattr(self.context.get('request'), 'user', None)
        if user and not user.is_anonymous:
            return Subscription.objects.filter(
                user__exact=user, subscribed_to__exact=obj).exists()
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
