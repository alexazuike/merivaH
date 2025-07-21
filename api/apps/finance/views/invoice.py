import json
from typing import List

from rest_framework import viewsets, filters, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.db import transaction

from api.includes import exceptions
from api.includes.pagination import CustomPagination
from api.apps.patient import models as patient_models
from api.includes import utils
from api.apps.finance.libs import invoice as invoice_lib
from api.apps.finance import models, serializers
from api.apps.finance import filters as finance_filters


class InvoiceViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = models.Invoice.objects.all()
    serializer_class = serializers.InvoiceSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = finance_filters.InvoiceFilter
    ordering = ("-id",)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return serializers.InvoiceResponseSerializer
        return super().get_serializer_class()

    @extend_schema(request=None, responses=serializers.InvoiceSerializer)
    @action(
        detail=True,
        methods=["patch"],
        url_path="confirm",
        permission_classes=[permissions.IsAuthenticated],
    )
    def confirm(self, request, pk=None):
        invoice: models.Invoice = self.get_object()
        user_data = utils.trim_user_data(utils.model_to_dict(request.user))
        patient = patient_models.Patient.objects.get(id=invoice.patient["id"])
        invoice_util = invoice_lib.Invoice(
            patient=patient, invoice=invoice, user_data=user_data
        )
        invoice = invoice_util.confirm_invoice()
        serializer = serializers.InvoiceSerializer(instance=invoice)
        return Response(data=serializer.data, status=200)

    @extend_schema(
        request=serializers.InvoicePaymentSerializer,
        responses=serializers.InvoiceSerializer,
    )
    @action(
        detail=True,
        methods=["put"],
        url_path="pay",
        permission_classes=[permissions.IsAuthenticated],
    )
    def pay_invoice(self, request, pk=None):
        invoice: models.Invoice = self.get_object()
        user: User = request.user
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        if not user.has_perm("finance.accept_payment"):
            raise exceptions.PermissionDenied(
                "Permission to accept payments for invoices not granted"
            )
        serializer = serializers.InvoicePaymentSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save(invoice_obj=invoice, user_data=user_data)
        return Response(
            serializers.InvoiceResponseSerializer(invoice).data,
            status=status.HTTP_202_ACCEPTED,
        )

    @extend_schema(
        request=serializers.SummaryBillSerializer(many=True),
        responses=serializers.InvoiceSerializer,
    )
    @action(
        detail=True,
        methods=["put"],
        url_path="bills",
        url_name="edit_bills",
    )
    @transaction.atomic
    def edit_bills(self, request, pk=None):
        """Edit bills"""
        invoice: models.Invoice = self.get_object()
        if str(invoice.status).casefold() != models.InvoiceStatus.DRAFT.casefold():
            raise exceptions.BadRequest("Cannot edit an invoice not in draft")
        serializer = serializers.SummaryBillSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        request_data = json.loads(json.dumps(serializer.data))
        patient: patient_models.Patient = patient_models.Patient.objects.get(
            id=invoice.patient.get("id")
        )
        user_data = utils.trim_user_data(utils.model_to_dict(instance=request.user))
        invoice_utils = invoice_lib.Invoice(
            invoice=invoice,
            patient=patient,
            user_data=user_data,
        )
        invoice = invoice_utils.edit_bills(bills=request_data, user=request.user)
        serializer = serializers.InvoiceSerializer(instance=invoice)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
