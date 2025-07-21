from django_filters.rest_framework import FilterSet
from django.db.models import QuerySet, Q
import django_filters

from api.apps.pharmacy import models
from api.apps.inventory import models as inv_models


class PrescriptionFilter(FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_at")
    fulfilled_date = django_filters.DateFromToRangeFilter(field_name="fulfilled_at")
    cancelled_date = django_filters.DateFromToRangeFilter(field_name="cancelled_at")
    prc_id = django_filters.CharFilter(
        label="Prescription ID", field_name="prc_id", lookup_expr="icontains"
    )
    patient_uhid = django_filters.CharFilter(
        label="Patient UHID", field_name="patient__uhid", lookup_expr="icontains"
    )
    patient_name = django_filters.CharFilter(
        method="filter_patient_name", label="Patient Name"
    )
    store = (
        django_filters.ModelMultipleChoiceFilter(
            label="Stores",
            field_name="store__id",
            to_field_name="id",
            queryset=inv_models.Store.objects.all(),
        ),
    )

    class Meta:
        model = models.Prescription
        fields = (
            "status",
            "prc_id",
            "patient_uhid",
            "patient_name",
            "date",
            "fulfilled_date",
            "cancelled_date",
        )

    def filter_patient_name(self, queryset: QuerySet, name, value):
        return queryset.filter(
            Q(patient__firstname__icontains=value)
            | Q(patient__lastname__icontains=value)
            | Q(patient__middlename__icontains=value)
        )
