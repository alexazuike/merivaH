import json

from django.core.serializers.json import DjangoJSONEncoder
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
)
from drf_spectacular.types import OpenApiTypes
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework import viewsets, filters, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions

from api.includes import exceptions, utils, file_utils
from api.includes.pagination import CustomPagination
from api.apps.finance import models, serializers
from api.apps.finance import filters as finance_filters
from api.apps.finance.libs.reports.payments_report import PaymentsSummaryReportGenerator


class CashbookViewSet(viewsets.ReadOnlyModelViewSet, viewsets.GenericViewSet):
    queryset = models.CashBook.objects.all()
    serializer_class = serializers.CashbookSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    ordering_fields = ("csb_id", "amount", "status", "created_at")
    ordering = "-id"

    @extend_schema(request=None, responses=serializers.CashbookSerializer)
    @action(detail=False, methods=["post"], url_path="open")
    def open_cashbook(self, request):
        """opens cashbook for cashier"""
        user: User = request.user
        if not user.has_perm("finance.add_cashbook"):
            return exceptions.PermissionDenied(
                "Inadequate permissions to create cashbook"
            )
        cashbook = models.CashBook.open(user)
        serializer = serializers.CashbookSerializer(instance=cashbook)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(request=None, responses=[serializers.CashbookSerializer])
    @action(detail=True, methods=["delete"], url_path="close")
    def close_cashbook(self, request, pk=None):
        """close cashbook for cashier"""
        user: User = request.user
        if not user.has_perm("finance.change_cashbook"):
            return exceptions.PermissionDenied(
                "Inadequate permissions to close cashbook"
            )
        cashbook: models.CashBook = self.get_object()
        cashbook.close()  # closes cashbook
        serializer = serializers.CashbookSerializer(instance=cashbook)
        return Response(
            data={
                "message": f"cashbook {cashbook.csb_id} closed",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = (
        models.PaymentMethod.objects.all()
        .exclude(name__iexact="reserve")
        .exclude(name__iexact="refund")
    )
    serializer_class = serializers.PaymentMethodSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = finance_filters.PaymentMethodFilter
    ordering_fields = ("name", "created_at", "updated_at")
    ordering = ("-id",)

    def get_serializer_context(self):
        context = super(PaymentMethodViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context


class PaymentViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = models.Payment.objects.all()
    serializer_class = serializers.PaymentSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = finance_filters.PaymentFilter
    ordering = ("-id",)

    def get_serializer_context(self):
        context = super(PaymentViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context


class PaymentSummaryReportViewset(viewsets.GenericViewSet):
    queryset = models.Payment.objects.all()
    serializer_class = serializers.PaymentSummaryReportsSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = finance_filters.PaymentFilter

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="to_excel",
                location=OpenApiParameter.QUERY,
                description="Print excel",
                type=OpenApiTypes.BOOL,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get summary reports data"""
        queryset = self.filter_queryset(self.get_queryset())
        to_excel: bool = utils.str_to_bool(
            request.query_params.get("to_excel", "false")
        )
        revenue_summary = PaymentsSummaryReportGenerator(payments=queryset)
        data = revenue_summary.to_response_struct()
        if to_excel:
            data = revenue_summary.to_report_struct()
            excel_bytes = file_utils.FileUtils().write_excel_file(data)
            response = HttpResponse(
                excel_bytes, content_type="application/vnd.ms-excel"
            )
            response[
                "Content-Disposition"
            ] = "attachment; filename=summary_payments.xlsx"
            return response
        serializer = self.get_serializer_class()(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data)


class PaymentDetailReportViewset(viewsets.GenericViewSet):
    queryset = models.Payment.objects.all()
    serializer_class = serializers.PaymentDetailedReportSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = finance_filters.PaymentFilter
    ordering = ("-id",)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="to_excel",
                location=OpenApiParameter.QUERY,
                description="Print excel",
                type=OpenApiTypes.BOOL,
            )
        ]
    )
    def list(self, request, *args):
        """Get reports data"""
        queryset = self.filter_queryset(self.get_queryset())
        to_excel: bool = utils.str_to_bool(
            request.query_params.get("to_excel", "false")
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
            if not to_excel:
                return self.get_paginated_response(data)
            else:
                serializer = self.get_serializer(queryset, many=True)
                data = utils.to_report_structure(
                    json.loads(json.dumps(serializer.data, cls=DjangoJSONEncoder))
                )
                excel_bytes = file_utils.FileUtils().write_excel_file(data)
                response = HttpResponse(
                    excel_bytes, content_type="application/vnd.ms-excel"
                )
                response[
                    "Content-Disposition"
                ] = "attachment; filename=detailed_payments.xlsx"
                return response
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            if not to_excel:
                return Response(data)
            else:
                data = utils.to_report_structure(
                    json.loads(json.dumps(serializer.data, cls=DjangoJSONEncoder))
                )
                excel_bytes = file_utils.FileUtils().write_excel_file(data)
                response = HttpResponse(
                    excel_bytes, content_type="application/vnd.ms-excel"
                )
                response[
                    "Content-Disposition"
                ] = "attachment; filename=payment_detailed.xlsx"
                return response
