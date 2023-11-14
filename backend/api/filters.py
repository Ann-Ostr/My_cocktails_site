# from django_filters import ModelMultipleChoiceFilter

from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Tag

def favorite(self, queryset, name, value):
        if value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset
    


class RecipeTagFilter(FilterSet):

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    is_favorited = filters.ModelChoiceFilter(
        queryset=favorite,
    )


    class Meta:
        model = Recipe
        fields = ['tags', 'author']


# class RecipeFavoriteFilter(FilterSet):
#     is_favorited = filters.BooleanFilter(method='favorite')

#     def favorite(self, queryset, name, value):
#         if value:
#             return queryset.filter(favorite__user=self.request.user)
#         return queryset

#     class Meta:
#         model = Recipe
#         fields = []
