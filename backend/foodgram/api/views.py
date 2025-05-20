from djoser.views import UserViewSet

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import permissions, status

from django_filters.rest_framework import DjangoFilterBackend

from core.models import Ingredient, Recipe, Subscription, User

from .pagination import LimitPagePagination
from .permissions import IsAuthorOrReadOnly
from .filters import IngredientFilter
from .serializers import (
    AvatarUploadSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    UserAccountSerializer,
    UserWithRecipeSerializer
)

# Create your views here.

class UserAccountViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserAccountSerializer

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = LimitPagePagination

    @action(
            methods=['get'], detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
            methods=['put', 'delete'], detail=True,
            permission_classes=[permissions.IsAuthenticated])
    def avatar(self, request, id):
        if request.method == 'PUT':
            serializer = AvatarUploadSerializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.user.avatar:
            request.user.avatar.delete()
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
            methods=['get'], detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribers__user=request.user)

        pages = self.paginate_queryset(queryset)
        serializer = UserWithRecipeSerializer(pages, many=True, context={'request': request})

        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, id):
        subscriber = request.user
        user = self.get_object()
        sub = Subscription.objects.filter(user=subscriber, subscribed_to=user)

        if request.method == 'POST':
            if subscriber == user or sub.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)

            Subscription.objects.create(user=subscriber, subscribed_to=user)

            serializer = UserWithRecipeSerializer(user, context={
                'request': request,
                'recipes_limit': request.query_params.get('recipes_limit')
            })

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not sub.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        sub.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = LimitPagePagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['get'], detail=False)
    def get_link(self, request):
        return Response('https://foodgram.example.org/s/3d0') # TODO


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter