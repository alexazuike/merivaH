from django_filters.rest_framework.filterset import FilterSet
import django_filters
from django.db.models import Q, QuerySet
from django.contrib.auth.models import User

from api.apps.facilities import models as facilities_models
from .models import Encounter, Clinic, EncounterTemplate


class ClinicFilter(FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    department = django_filters.ModelMultipleChoiceFilter(
        label="Department Id",
        field_name="department__id",
        to_field_name="id",
        queryset=facilities_models.Department.objects.all(),
    )

    class Meta:
        model = Clinic
        fields = ["is_active", "department", "name"]


class EncounterReportsFilter(FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_datetime")
    department = django_filters.ModelMultipleChoiceFilter(
        label="Clinic Department ID",
        field_name="clinic__Department__id",
        to_field_name="id",
        queryset=facilities_models.Department.objects.all(),
    )
    clinic = django_filters.ModelMultipleChoiceFilter(
        label="Clinic ID",
        field_name="clinic__id",
        to_field_name="id",
        queryset=Clinic.objects.all(),
    )
    provider = django_filters.ModelMultipleChoiceFilter(
        label="Provider ID",
        field_name="provider__id",
        to_field_name="id",
        queryset=User.objects.all(),
    )
    status = django_filters.CharFilter(
        label="status", field_name="status", lookup_expr="iexact"
    )
    acknowledged_date = django_filters.DateFromToRangeFilter(
        field_name="acknowledged_at"
    )
    acknowledger = django_filters.ModelMultipleChoiceFilter(
        label="User ID",
        field_name="acknowledged_by__id",
        to_field_name="id",
        queryset=User.objects.all(),
    )
    signed_date = django_filters.DateFromToRangeFilter(field_name="signed_date")

    class Meta:
        model = Encounter
        fields = ["date", "department", "clinic", "provider", "status"]


class EncounterFilter(EncounterReportsFilter):
    class Meta:
        model = Encounter
        fields = [
            "encounter_id",
            "patient_name",
            "patient_uhid",
            "clinic",
            "department",
            "provider",
            "status",
            "date",
            "worklist",
        ]

    patient_name = django_filters.CharFilter(
        method="filter_patient_name", label="Patient Name"
    )
    patient_uhid = django_filters.CharFilter(
        method="filter_patient_uhid", label="Patient UHID"
    )

    date = django_filters.DateFromToRangeFilter(field_name="created_datetime")
    worklist = django_filters.BooleanFilter(method="filter_worklist", label="Worklist")

    def filter_patient_name(self, queryset, name, value):
        return queryset.filter(
            Q(patient__firstname__icontains=value)
            | Q(patient__lastname__icontains=value)
            | Q(patient__middlename__icontains=value)
        )

    def filter_patient_uhid(self, queryset, name, value):
        return queryset.filter(patient__uhid__iexact=value)

    def filter_worklist(self, queryset, name, value):
        if value:
            return queryset.filter(
                ~Q(status__iexact="DS") & ~Q(status__icontains="cancelled")
            )
        return queryset


class EncounterTemplateFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    user = django_filters.ModelChoiceFilter(
        label="User ID",
        field_name="created_by__id",
        to_field_name="id",
        queryset=User.objects.all(),
    )
    date = django_filters.DateFromToRangeFilter(field_name="created_at")
    clinic = django_filters.NumberFilter(method="filter_clinic", label="CLinic Id")

    class Meta:
        model = EncounterTemplate
        fields = ("title", "user", "date", "is_active", "is_default", "clinic")

    def filter_clinic(self, queryset: QuerySet, name, value):
        if value:
            return queryset.filter(Q(clinic__in=[value]) | Q(is_default=True))
        return queryset.filter(Q(is_default=True))
