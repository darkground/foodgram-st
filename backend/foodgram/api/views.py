from djoser.views import UserViewSet

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import pagination, permissions

from core.models import Recipe, User
from .serializers import (
    RecipeSerializer,
    UserAccountSerializer,
    UserRegisterSerializer
)

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


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer # TODO

    # TODO change to auth or read only after djoser
    permission_classes = [permissions.AllowAny]
    pagination_class = pagination.LimitOffsetPagination

    @action(methods=['get'], detail=False)
    def get_link(self, request):
        return Response("https://foodgram.example.org/s/3d0") # TODO