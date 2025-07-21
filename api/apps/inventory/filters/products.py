from django_filters.rest_framework import FilterSet
from django.db.models import QuerySet
import django_filters

from api.apps.inventory import models as inv_models
from api.apps.pharmacy import models as pharm_models
from api.includes import utils


class ProductFilter(FilterSet):
    generic_drug = django_filters.ModelMultipleChoiceFilter(
        label="Generic Drug ID",
        field_name="generic_drug__id",
        to_field_name="id",
        queryset=pharm_models.GenericDrug.objects.all(),
    )

    class Meta:
        model = inv_models.Product
        fields = ("code", "generic_drug")
