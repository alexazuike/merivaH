from django_filters.rest_framework import FilterSet
from django.db.models import QuerySet
from django.db.models import Q
import django_filters

from . import models


class UserFilters(FilterSet):
    username = django_filters.CharFilter(field_name="username", lookup_expr="icontains")
    email = django_filters.CharFilter(field_name="email", lookup_expr="icontains")
    first_name = django_filters.CharFilter(
        field_name="first_name", lookup_expr="icontains"
    )
    last_name = django_filters.CharFilter(
        field_name="last_name", lookup_expr="icontains"
    )
    date_joined = django_filters.DateFromToRangeFilter(field_name="date_joined")
    name = django_filters.CharFilter(method="filter_name", label="Name")

    class Meta:
        model = models.User
        fields = (
            "username",
            "is_active",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "groups",
            "name",
        )

    def filter_name(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
            | Q(username__icontains=value)
        )
