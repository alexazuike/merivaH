from django_filters.rest_framework import FilterSet
from django.db.models import QuerySet
import django_filters

from api.apps.inventory import models
from api.includes import utils


class StoreFilter(FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = models.Store
        fields = ("name", "type", "is_pharmacy")
