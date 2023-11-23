from django_filters import AllValuesMultipleFilter, ModelMultipleChoiceFilter
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Tag
from users.models import User


class RecipeTagFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method="favorited_method")
    is_in_shopping_cart = filters.BooleanFilter(
        method="in_shopping_cart_method"
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = AllValuesMultipleFilter(field_name='tags__slug')

    def favorited_method(self, queryset, name, value):
        if queryset.filter(favorite__user=self.request.user).exists():
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def in_shopping_cart_method(self, queryset, name, value):
        if queryset.filter(shopping_cart__user=self.request.user).exists():
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ("author", "tags")
