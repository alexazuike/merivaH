from django_filters.rest_framework.filterset import FilterSet
import django_filters
from django.db.models import Q

from . import models
from api.apps.facilities import models as facilities_models


class ServiceCenterFilter(FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = models.ServiceCenter
        fields = ["name"]


class ModalityFilter(FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = models.Modality
        fields = ["name"]


class ImagingObservationFilter(FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    active = django_filters.BooleanFilter(field_name="active")
    status = django_filters.BooleanFilter(field_name="status")
    modality = django_filters.ModelChoiceFilter(
        field_name="modality__id",
        queryset=models.Modality.objects.all(),
    )

    class Meta:
        model = models.ImagingObservation
        fields = ["name", "active", "status", "modality"]


class ImagingObservationFilter(FilterSet):
    modality = django_filters.ModelChoiceFilter(
        field_name="img_unit__slug",
        to_field_name="slug",
        queryset=models.Modality.objects.all(),
    )

    class Meta:
        model = models.ImagingObservation
        fields = ["name", "active", "modality", "status"]


class ImagingOrderFilter(FilterSet):
    patient_uhid = django_filters.CharFilter(
        method="filter_patient_uhid", label="Patient UHID"
    )
    patient_name = django_filters.CharFilter(
        method="filter_patient_name", label="Patient Name"
    )
    patient_phone = django_filters.CharFilter(
        method="filter_patient_phone", label="Patient Phone"
    )
    img_id = django_filters.CharFilter(method="filter_img_id", label="Imaging ID")

    class Meta:
        model = models.ImagingOrder
        fields = ["patient_uhid", "patient_name", "patient_phone", "img_id"]

    def filter_patient_uhid(self, queryset, name, value):
        return queryset.filter(patient__uhid__iexact=value)

    def filter_patient_name(self, queryset, name, value):
        return queryset.filter(
            Q(patient__firstname__icontains=value)
            | Q(patient__lastname__icontains=value)
            | Q(patient__middlename__icontains=value)
        )

    def filter_patient_phone(self, queryset, name, value):
        return queryset.filter(patient__phone_number__iexact=value)

    def filter_img_id(self, queryset, name, value):
        return queryset.filter(img_id__iexact=value)


class ImagingObservationOrderFilter(FilterSet):
    patient_uhid = django_filters.CharFilter(
        method="filter_patient_uhid", label="Patient UHID"
    )
    patient_name = django_filters.CharFilter(
        method="filter_patient_name", label="Patient Name"
    )
    patient_phone = django_filters.CharFilter(
        method="filter_patient_phone", label="Patient Phone"
    )
    service_center = django_filters.ModelMultipleChoiceFilter(
        label="Service Center ID",
        field_name="img_order__service_center__id",
        to_field_name="id",
        queryset=models.ServiceCenter.objects.all(),
    )
    modality = django_filters.ModelMultipleChoiceFilter(
        label="Modality ID",
        field_name="img_obv__modality__id",
        to_field_name="id",
        queryset=models.Modality.objects.all(),
    )

    facility = django_filters.ModelMultipleChoiceFilter(
        label="Facility ID",
        field_name="img_order__referral_facility__id",
        to_field_name="id",
        queryset=facilities_models.Facility.objects.all(),
    )

    sent = django_filters.BooleanFilter(
        field_name="is_result_sent", label="Result Sent/Print"
    )

    status = django_filters.CharFilter(field_name="status", method="filter_status")

    worklist = django_filters.BooleanFilter(method="filter_worklist", label="Worklist")
    date = django_filters.DateFromToRangeFilter(field_name="created_at")

    class Meta:
        model = models.ImagingObservationOrder
        fields = [
            "patient_uhid",
            "patient_name",
            "patient_phone",
            "service_center",
            "modality",
            "facility",
            "status",
            "worklist",
        ]

    def filter_patient_uhid(self, queryset, name, value):
        return queryset.filter(patient__uhid__iexact=value)

    def filter_patient_name(self, queryset, name, value):
        return queryset.filter(
            Q(patient__firstname__icontains=value)
            | Q(patient__lastname__icontains=value)
            | Q(patient__middlename__icontains=value)
        )

    def filter_patient_phone(self, queryset, name, value):
        return queryset.filter(patient__phone_number__iexact=value)

    def filter_status(self, queryset, name, value):
        return queryset.filter(status__iexact=value)

    def filter_worklist(self, queryset, name, value):
        return queryset.filter(img_order__worklist=value)

    def filter_worklist(self, queryset, name, value):
        if value:
            return queryset.filter(
                ~Q(status__iexact="approved") & ~Q(status__iexact="cancelled")
            )
        return queryset
