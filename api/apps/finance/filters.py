from django_filters.rest_framework import FilterSet
from django.db.models import QuerySet
from django.db.models import Q
from django.contrib.auth.models import User
import django_filters

from . import models
from api.includes import utils


class PaymentMethodFilter(FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    exclude = django_filters.AllValuesMultipleFilter(
        label="exclude names", field_name="name", lookup_expr="iexact", exclude=True
    )

    class Meta:
        model = models.PaymentMethod
        fields = ("name", "exclude")


class PayerFilter(FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    address = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = models.Payer
        fields = ("name",)


class PayerSchemeFilter(FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    type = django_filters.ChoiceFilter(choices=models.PayerSchemeType.choices())
    price_list = django_filters.ModelMultipleChoiceFilter(
        label="Price List ID",
        queryset=models.PriceList.objects.all(),
        field_name="price_list__id",
        to_field_name="id",
    )

    payer = django_filters.ModelMultipleChoiceFilter(
        label="Payer ID",
        queryset=models.Payer.objects.all(),
        field_name="payer__id",
        to_field_name="id",
    )

    class Meta:
        model = models.PayerScheme
        fields = ["type", "price_list", "payer", "name"]


class BillableItemFilter(FilterSet):
    description = django_filters.CharFilter(lookup_expr="icontains")
    cost_lt = django_filters.NumberFilter(lookup_expr="lt")
    cost_gt = django_filters.NumberFilter(lookup_expr="gt")
    selling_price_lt = django_filters.NumberFilter(lookup_expr="lt")
    selling_price_gt = django_filters.NumberFilter(lookup_expr="gt")
    module = django_filters.ChoiceFilter(
        choices=utils.Modules.choices(), method="filter_module"
    )

    class Meta:
        model = models.BillableItem
        fields = ("item_code", "cost", "module", "description")

    def filter_module(self, queryset, name, value):
        if value == "":
            return queryset
        value = utils.Modules.get_module_value(value)
        return queryset.filter(module=value)


class BillFilter(FilterSet):
    class Meta:
        model = models.Bill
        fields = [
            "bill_item_code",
            "transaction_date",
            "selling_price",
            "cost_price",
            "trx_date",
            "is_invoiced",
            "is_reserved",
            "is_capitated",
            "is_service_rendered",
            "patient",
            "module",
            "status",
        ]

    patient = django_filters.CharFilter(method="filter_patient", label="Patient ID")
    module = django_filters.ChoiceFilter(
        choices=utils.Modules.choices(), method="filter_module", label="Module"
    )
    status = django_filters.ChoiceFilter(
        choices=models.BillStatus.choices(), method="filter_status", label="Status"
    )
    trx_date = django_filters.DateFromToRangeFilter(
        field_name="transaction_date", label="Transaction Date Range"
    )
    selling_price = django_filters.RangeFilter(
        field_name="selling_price", label="Selling Price"
    )
    cost_price = django_filters.RangeFilter(field_name="cost_price", label="Cost Price")

    def filter_patient(self, queryset: QuerySet, name, value):
        return queryset.filter(patient__id__iexact=value)

    def filter_module(self, queryset: QuerySet, name, value):
        return queryset.filter(module__icontains=value)

    def filter_status(self, queryset: QuerySet, name, value):
        return queryset.filter(cleared_status__iexact=value)


class PriceListItemFilter(FilterSet):

    module = django_filters.ChoiceFilter(
        choices=utils.Modules.choices(), method="filter_module", label="Module"
    )

    price_list_exclude = django_filters.ModelMultipleChoiceFilter(
        label="Exclude Price List",
        field_name="price_list__id",
        to_field_name="id",
        queryset=models.PriceList.objects.all(),
        method="filter_exclude_price_list",
    )

    price_list = django_filters.ModelMultipleChoiceFilter(
        label="Price List",
        field_name="price_list__id",
        to_field_name="id",
        queryset=models.PriceList.objects.all(),
    )

    class Meta:
        model = models.PriceListItem
        fields = [
            "bill_item_code",
            "module",
            "price_list",
            "price_list_exclude",
            "is_auth_req",
            "is_capitated",
            "is_exclusive",
            "post_auth_allowed",
        ]

    def filter_module(self, queryset: QuerySet, name, value):
        if value == "":
            return queryset
        value = utils.Modules.get_module_value(value)
        return queryset.filter(module=value)

    def filter_exclude_price_list(self, queryset: QuerySet, name, value):
        return queryset.exclude(price_list__id__in=value)


class InvoiceFilter(FilterSet):
    class Meta:
        model = models.Invoice
        fields = [
            "status",
            "patient",
            "confirmed_at",
            "created_at",
            "due_date",
            "created_at",
            "scheme_type",
            "payer_scheme",
        ]

    status = django_filters.MultipleChoiceFilter(
        field_name="status",
        lookup_expr="iexact",
        choices=models.InvoiceStatus.choices(),
    )
    created_at = django_filters.DateFromToRangeFilter(field_name="created_at")
    confirmed_at = django_filters.DateFromToRangeFilter(field_name="confirmed_at")
    patient = django_filters.CharFilter(method="filter_patient", label="Patient ID")

    def filter_patient(self, queryset: QuerySet, name, value):
        return queryset.filter(patient__id__iexact=value)


class PaymentFilter(FilterSet):
    patient_id = django_filters.CharFilter(method="filter_patient", label="Patient ID")
    date = django_filters.DateFromToRangeFilter(field_name="created_at")
    patient_name = django_filters.CharFilter(
        method="filter_patient_name", label="Patient Name"
    )
    patient_uhid = django_filters.CharFilter(
        method="filter_patient_uhid", label="Patient UHID"
    )
    payment_method = django_filters.ModelMultipleChoiceFilter(
        label="Payment Method ID",
        field_name="payment_method__id",
        to_field_name="id",
        queryset=models.PaymentMethod.objects.all(),
    )
    cashier = django_filters.ModelMultipleChoiceFilter(
        label="Cashier ID",
        field_name="created_by__id",
        to_field_name="id",
        queryset=User.objects.all(),
    )

    class Meta:
        model = models.Payment
        fields = [
            "date",
            "patient_id",
            "patient_name",
            "patient_uhid",
            "payment_method",
            "cashier",
        ]

    def filter_patient(self, queryset: QuerySet, name, value):
        return queryset.filter(patient__id__iexact=value)

    def filter_patient_name(self, queryset, name, value):
        return queryset.filter(
            Q(patient__firstname__icontains=value)
            | Q(patient__lastname__icontains=value)
            | Q(patient__middlename__icontains=value)
        )

    def filter_patient_uhid(self, queryset, name, value):
        return queryset.filter(patient__uhid__iexact=value)


class RevenueFilter(FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="serviced_rendered_at")
    patient_name = django_filters.CharFilter(
        method="filter_patient_name", label="Patient Name"
    )
    patient_uhid = django_filters.CharFilter(
        method="filter_patient_uhid", label="Patient UHID"
    )
    bill_source = django_filters.ChoiceFilter(choices=utils.Modules.search_choices())

    class Meta:
        model = models.Bill
        fields = [
            "date",
            "bill_source",
            "billed_to_type",
            "billed_to",
            "patient_name",
            "patient_uhid",
        ]

    def filter_patient_name(self, queryset, name, value):
        return queryset.filter(
            Q(patient__firstname__icontains=value)
            | Q(patient__lastname__icontains=value)
            | Q(patient__middlename__icontains=value)
        )

    def filter_patient_uhid(self, queryset, name, value):
        return queryset.filter(patient__uhid__iexact=value)
