from django_filters import rest_framework as filters

from . import models
from api.apps.finance import models as fin_models


class PatientReportFilter(filters.FilterSet):
    date = filters.DateFromToRangeFilter(field_name="created_at")
    uhid = filters.CharFilter(field_name="uhid", lookup_expr="icontains")
    firstname = filters.CharFilter(field_name="firstname", lookup_expr="icontains")
    lastname = filters.CharFilter(field_name="lastname", lookup_expr="icontains")
    scheme = filters.ModelMultipleChoiceFilter(
        label="Payer Scheme ID",
        field_name="payment_scheme__payer_scheme__id",
        to_field_name="id",
        queryset=fin_models.PayerScheme.objects.all(),
    )
    dob = filters.DateFromToRangeFilter(field_name="date_of_birth")

    class Meta:
        model = models.Patient
        fields = ["date", "uhid", "firstname", "lastname", "scheme", "dob"]


class PatientFilter(filters.FilterSet):
    firstname = filters.CharFilter(method="filter_firstname", label="First Name")
    lastname = filters.CharFilter(method="filter_lastname", label="Last Name")
    middlename = filters.CharFilter(method="filter_middlename", label="Middle Name")
    uhid = filters.CharFilter(field_name="uhid", lookup_expr="icontains")
    religion = filters.CharFilter(method="filter_religion", label="Religion")

    class Meta:
        model = models.Patient
        fields = [
            "firstname",
            "lastname",
            "middlename",
            "gender",
            "phone_number",
            "religion",
            "date_of_birth",
            "uhid",
        ]

    def filter_firstname(self, queryset, name, value):
        return queryset.filter(firstname__icontains=value)

    def filter_lastname(self, queryset, name, value):
        return queryset.filter(lastname__icontains=value)

    def filter_middlename(self, queryset, name, value):
        return queryset.filter(middlename__icontains=value)

    def filter_uhid(self, queryset, name, value):
        return queryset.filter(uhid__iexact=value)

    def filter_religion(self, queryset, name, value):
        return queryset.filter(religion__icontains=value)


class PatientFileFilter(filters.FilterSet):
    title = filters.CharFilter(field_name="title", lookup_expr="icontains")

    class Meta:
        model = models.PatientFile
        fields = ["title", "patient", "document_type"]
