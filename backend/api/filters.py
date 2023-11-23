from django_filters import AllValuesMultipleFilter
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe
from users.models import User


class RecipeTagFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method="favorited_method")
    is_in_shopping_cart = filters.BooleanFilter(
        method="in_shopping_cart_method"
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = AllValuesMultipleFilter(field_name='tags__slug',
                                   method='filter_tags')

    def favorited_method(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite__user=user)
        return queryset.none()

    def in_shopping_cart_method(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_cart__user=user)
        return queryset.none()

    def filter_tags(self, queryset, name, value):
        if value:
            return queryset.filter(
                tags__slug__in=value).distinct()
        return queryset

    class Meta:
        model = Recipe
        fields = ("author", "tags")
