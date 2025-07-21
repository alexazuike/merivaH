from django_filters.rest_framework.filterset import FilterSet
import django_filters
from django.db.models import Q, QuerySet

from . import models


class ServiceCenterFilter(FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = models.ServiceCenter
        fields = ["name"]


class LabUnitFilter(FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = models.LabUnit
        fields = ["name"]


class LabPanelFilter(FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    active = django_filters.BooleanFilter(field_name="active")
    status = django_filters.BooleanFilter(field_name="status", lookup_expr="iexact")

    class Meta:
        model = models.LabPanel
        fields = ["name", "active", "status"]


class LabObservationFilter(FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    uom = django_filters.CharFilter(field_name="uom", lookup_expr="icontains")

    class Meta:
        model = models.LabObservation
        fields = ["name", "uom"]


class LabSpecimenTypeFilter(FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    color = django_filters.CharFilter(field_name="color", lookup_expr="icontains")
    description = django_filters.CharFilter(
        field_name="description", lookup_expr="icontains"
    )
    status = django_filters.BooleanFilter(field_name="status", lookup_expr="iexact")

    class Meta:
        model = models.LabSpecimenType
        fields = ["name", "color", "description", "status"]


class LabSpecimenFilter(FilterSet):
    asn = django_filters.CharFilter(field_name="asn", lookup_expr="icontains")
    status = django_filters.CharFilter(field_name="status", lookup_expr="icontains")

    class Meta:
        model = models.LabSpecimen
        fields = ["asn", "status"]


class LabOrderFilter(FilterSet):
    patient_uhid = django_filters.CharFilter(
        field_name="patient__uhid", lookup_expr="icontains"
    )
    patient_name = django_filters.CharFilter(
        method="filter_patient_name", label="Patient Name"
    )
    patient_phone = django_filters.CharFilter(
        field_name="patient__phone_number", lookup_expr="iexact"
    )
    asn = django_filters.CharFilter(field_name="asn", lookup_expr="icontains")

    service_center = django_filters.ModelMultipleChoiceFilter(
        label="Service Center",
        field_name="service_center__id",
        to_field_name="id",
        queryset=models.ServiceCenter.objects.all(),
    )

    lab_unit = django_filters.CharFilter(method="filter_lab_unit", label="lab_unit_id")

    class Meta:
        model = models.LabOrder
        fields = ["patient_uhid", "patient_name", "patient_phone", "asn"]

    def filter_patient_name(self, queryset, name, value):
        return queryset.filter(
            Q(patient__firstname__icontains=value)
            | Q(patient__lastname__icontains=value)
            | Q(patient__middlename__icontains=value)
        )

    def filter_lab_unit(self, queryset: QuerySet, name, value):
        lab_unit = models.LabUnit.objects.filter(id=int(value))
        if lab_unit.exists():
            lab_panels = models.LabPanel.objects.filter(lab_unit=lab_unit.first())
            if lab_panels.exists():
                panel_ids = list(lab_panels.values_list("id", flat=True))
                return queryset.filter(lab_panels__contained_by=panel_ids)
        return queryset


class LabReportsFilter(FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_at")
    lab_unit = django_filters.ModelMultipleChoiceFilter(
        label="Lab Unit ID",
        field_name="panel__lab_unit__id",
        to_field_name="id",
        queryset=models.LabUnit.objects.all(),
    )
    service_center = django_filters.ModelMultipleChoiceFilter(
        label="Service Center ID",
        field_name="lab_order__service_center__id",
        to_field_name="id",
        queryset=models.ServiceCenter.objects.all(),
    )
    asn = django_filters.CharFilter(
        label="ASN", field_name="lab_order__asn", lookup_expr="icontains"
    )
    patient_uhid = django_filters.CharFilter(
        label="Patient UHID", field_name="patient__uhid", lookup_expr="icontains"
    )

    patient_name = django_filters.CharFilter(
        method="filter_patient_name", label="Patient Name"
    )
    status = django_filters.CharFilter(
        label="status", field_name="status", lookup_expr="iexact"
    )
    approved_date = django_filters.DateFromToRangeFilter(field_name="approved_on")

    class Meta:
        model = models.LabPanelOrder
        fields = [
            "service_center",
            "lab_unit",
            "asn",
            "patient_uhid",
            "patient_name",
            "status",
        ]

    def filter_patient_name(self, queryset, name, value):
        return queryset.filter(
            Q(patient__firstname__icontains=value)
            | Q(patient__lastname__icontains=value)
            | Q(patient__middlename__icontains=value)
        )


class LabPanelOrderFilter(LabReportsFilter):
    class Meta:
        model = models.LabPanelOrder
        fields = [
            "patient_uhid",
            "patient_name",
            "patient_phone",
            "lab_unit",
            "status",
            "service_center",
            "status",
            "worklist",
            "sent",
        ]

    patient_phone = django_filters.CharFilter(
        method="filter_patient_phone", label="Patient Phone"
    )
    worklist = django_filters.BooleanFilter(method="filter_worklist", label="Worklist")
    sent = django_filters.BooleanFilter(
        field_name="is_result_sent", label="Result Sent/Print"
    )

    def filter_patient_phone(self, queryset, name, value):
        return queryset.filter(patient__phone_number__iexact=value)

    def filter_worklist(self, queryset, name, value):
        if value:
            return queryset.filter(
                ~Q(status__iexact="approved") & ~Q(status__iexact="cancelled")
            )
        return queryset
