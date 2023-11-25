from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import RecipeTagFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (IngredientSerializer,
                             RecipeCreateUpdateSerializer, RecipeSerializer,
                             RecipeSubscibeSerializer, SubscriptionSerializer,
                             TagSerializer)
from api.utils import draw_shopping_cart
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                            ShoppingCart, Tag)
from users.models import Subscription, User


class CustomUserViewSet(UserViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,),)
    def subscriptions(self, request):
        user = self.request.user
        queryset = user.follower.all()
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = self.request.user
        author = get_object_or_404(User, pk=id)
        if user == author:
            return Response(
                {'errors': 'Нельзя подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST,)

        if Subscription.objects.filter(user=user, author=author).exists():
            return Response({'errors': 'Подписка уже оформлена'},
                            status=status.HTTP_400_BAD_REQUEST,)

        queryset = Subscription.objects.create(author=author, user=user)
        serializer = SubscriptionSerializer(queryset,
                                            context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        user = self.request.user
        author = get_object_or_404(User, pk=id)
        if not Subscription.objects.filter(
                user=user, author=author).exists():
            return Response({'errors': 'Вы уже отписаны'},
                            status=status.HTTP_400_BAD_REQUEST,)
        subscription = get_object_or_404(Subscription,
                                         user=user, author=author)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeTagFilter
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update', 'update'):
            return RecipeCreateUpdateSerializer

        return RecipeSerializer

    def add_bind(self, model, user, pk, name):
        try:
            # recipe = get_object_or_404(Recipe, pk=pk)
            recipe = Recipe.objects.get(pk=pk)
            bind = model.objects.filter(user=user, recipe=recipe)
            if bind.exists():
                return Response(
                    {'errors': f'Нельзя повторно добавить рецепт в {name}'},
                    status=status.HTTP_400_BAD_REQUEST,)
            model.objects.create(user=user, recipe=recipe)
            serializer = RecipeSubscibeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception:
            return Response({'errors': 'Такого рецепта не существует'},
                            status=status.HTTP_400_BAD_REQUEST,)

    def delete_bind(self, model, user, pk, name):
        recipe = get_object_or_404(Recipe, pk=pk)
        bind = model.objects.filter(user=user, recipe=recipe)
        if not bind.exists():
            return Response(
                {'errors': f'Нельзя повторно удалить рецепт из {name}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        bind.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='favorite',
        url_name='favorite',
    )
    def favorite(self, request, pk=None):
        user = request.user
        if request.method == 'POST':
            name = 'избранное'
            return self.add_bind(Favorite, user, pk, name)
        if request.method == 'DELETE':
            name = 'избранного'
            return self.delete_bind(Favorite, user, pk, name)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='shopping_cart',
        url_name='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        if request.method == 'POST':
            name = 'список покупок'
            return self.add_bind(ShoppingCart, user, pk, name)
        if request.method == 'DELETE':
            name = 'списка покупок'
            return self.delete_bind(ShoppingCart, user, pk, name)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredients.objects.filter(
            recipe__shopping_cart__user=request.user).values(
            name=F('ingredient__name'),
            unit=F('ingredient__measurement_unit')
        ).order_by('name').annotate(total=Sum('amount'))

        response = HttpResponse(
            content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="shopping-list.pdf"')
        draw_shopping_cart(response, ingredients)
        return response
