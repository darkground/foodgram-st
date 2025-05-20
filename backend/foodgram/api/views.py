from djoser.views import UserViewSet

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import pagination
from rest_framework import permissions

from core.models import User
from .serializers import UserAccountSerializer, UserRegisterSerializer

# Create your views here.

class UserAccountViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserAccountSerializer

    # TODO change to auth or read only after djoser
    permission_classes = [permissions.AllowAny]
    pagination_class = pagination.LimitOffsetPagination

    @action(
            methods=['get'], detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegisterSerializer
        return UserAccountSerializer