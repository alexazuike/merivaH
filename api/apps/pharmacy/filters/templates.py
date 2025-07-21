from django_filters.rest_framework import FilterSet
from django.db.models import QuerySet, Q
import django_filters

from api.apps.pharmacy import models


class TemplateFilter(FilterSet):
    title = django_filters.CharFilter(field_name="title")
    date = django_filters.DateFromToRangeFilter(field_name="created_at")
    user = django_filters.CharFilter(method="filter_user", label="User Name")

    class Meta:
        model = models.Template
        fields = ("title", "description", "is_public")

    def filter_user(self, queryset: QuerySet, name, value):
        return queryset.filter(
            Q(created_by__first_name__icontains=value)
            | Q(created_by__last_name__icontains=value)
        )
