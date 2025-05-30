from django.views.generic.base import RedirectView
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from django.http import FileResponse, Http404
from django.urls import reverse

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import permissions, status

from django_filters.rest_framework import DjangoFilterBackend

from core.const import SHORT_LINK_ID_BASE
from core.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    User
)

from .pagination import LimitPagePagination
from .permissions import IsAuthorOrReadOnly
from .filters import IngredientFilter, RecipeFilter
from .serializers import (
    AvatarUploadSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    RecipeShortSerializer,
    UserAccountSerializer,
    UserWithRecipeSerializer,
    SubscribeSerializer
)


class UserAccountViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserAccountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = LimitPagePagination

    @action(methods=['get'], detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(methods=['put', 'delete'], detail=True,
            permission_classes=[permissions.IsAuthenticated])
    def avatar(self, request, id):
        if request.method == 'PUT':
            serializer = AvatarUploadSerializer(
                request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.user.avatar:
            request.user.avatar.delete()
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribed__user=request.user)

        pages = self.paginate_queryset(queryset)
        serializer = UserWithRecipeSerializer(
            pages, many=True, context={'request': request})

        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, id):
        subscriber = request.user
        user = self.get_object()
        sub = subscriber.subscribers.filter(subscribed_to=user)

        if request.method == 'POST':
            subSerializer = SubscribeSerializer(
                data={'user': subscriber.id, 'subscribed_to': user.id},
                context={'request': request}
            )
            subSerializer.is_valid(raise_exception=True)
            subSerializer.save()

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
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly
    ]
    pagination_class = LimitPagePagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = self.get_object()
        shopcart = user.shopping_cart.filter(recipe=recipe)

        if request.method == "POST":
            if shopcart.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(
                RecipeShortSerializer(recipe).data,
                status=status.HTTP_201_CREATED,
            )

        if not shopcart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        shopcart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = self.get_object()
        fav = user.favorites.filter(recipe=recipe)

        if request.method == "POST":
            if fav.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=user, recipe=recipe)
            return Response(
                RecipeShortSerializer(recipe).data,
                status=status.HTTP_201_CREATED,
            )

        if not fav.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        fav.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = (
            IngredientInRecipe.objects
            .filter(recipe__in=request.user.shopping_cart.values('recipe'))
            .values(name=F('ingredient__name'),
                    unit=F('ingredient__measurement_unit'))
            .annotate(amount=Sum('amount'))
            .order_by('name')
        )

        buy_list = 'Список покупок:'

        if ingredients:
            for ingred in ingredients:
                buy_list += (
                    f'\n{ingred["name"]} - '
                    f'{ingred["amount"]} ({ingred["unit"]})'
                )
        else:
            buy_list += '\nПусто!'

        return FileResponse(
            buy_list,
            filename='shoplist.txt',
            as_attachment=True,
            content_type='text/plain'
        )

    @action(methods=['get'], detail=True, url_path='get-link')
    def get_link(self, request, pk):
        recipe = self.get_object()
        link = reverse('short-link', kwargs={'short_link': f'{recipe.id:x}'})
        url = request.build_absolute_uri(link)
        return Response({'short-link': url}, status=status.HTTP_200_OK)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class ShortRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, short_link):
        try:
            recipe_id = int(short_link, SHORT_LINK_ID_BASE)
            get_object_or_404(Recipe, id=recipe_id)
            return f'/recipes/{recipe_id}'
        except (Http404, ValueError):
            return '/404'
