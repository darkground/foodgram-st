from django_filters.rest_framework import FilterSet
from django_filters.filters import CharFilter

from core.models import Ingredient

class IngredientFilter(FilterSet):
    name = CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ['name']