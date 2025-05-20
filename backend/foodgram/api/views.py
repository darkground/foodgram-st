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

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = pagination.LimitOffsetPagination

    @action(
            methods=['get'], detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = pagination.LimitOffsetPagination

    @action(methods=['get'], detail=False)
    def get_link(self, request):
        return Response("https://foodgram.example.org/s/3d0") # TODO