from django_filters.rest_framework import FilterSet
import django_filters

from . import models


class NursingOrderFilter(FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_at")
    station = django_filters.ModelMultipleChoiceFilter(
        label="Nursing Station",
        field_name="station__id",
        to_field_name="id",
        queryset=models.NursingStation.objects.all(),
    )

    class Meta:
        model = models.NursingOrder
        fields = ["status", "date", "station"]
