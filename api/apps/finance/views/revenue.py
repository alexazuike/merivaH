from rest_framework import viewsets, permissions, filters
from rest_framework.request import Request
from rest_framework.response import Response
from django.http import HttpResponse
from drf_spectacular.utils import OpenApiParameter, extend_schema
from drf_spectacular.types import OpenApiTypes
from django_filters.rest_framework import DjangoFilterBackend

from api.apps.finance.models.bills import Bill
from api.apps.finance.serializers.revenue import (
    RevenueSummarySerializer,
    RevenueDetailSerializer,
)
from api.apps.finance.libs.reports.revenue_reports import (
    RevenueSummaryReportGenerator,
    RevenueDetailReportGenerator,
)
from api.apps.finance.filters import RevenueFilter
from api.includes.pagination import CustomPagination
from api.includes import file_utils, utils


class RevenueSummaryViewSet(viewsets.mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Bill.objects.all()
    serializer_class = RevenueSummarySerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.AllowAny]
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = RevenueFilter

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="to_excel",
                location=OpenApiParameter.QUERY,
                description="Print excel",
                type=OpenApiTypes.BOOL,
                default=False,
            ),
            OpenApiParameter(
                name="is_earned",
                location=OpenApiParameter.QUERY,
                description="Is revenue earned",
                type=OpenApiTypes.BOOL,
                default=True,
            ),
        ]
    )
    def list(self, request: Request, *args, **kwargs):
        """Get summary reports data"""
        queryset = self.filter_queryset(self.get_queryset())
        to_excel: bool = utils.str_to_bool(
            request.query_params.get("to_excel", "false")
        )
        is_earned: bool = utils.str_to_bool(request.query_params.get("is_earned"))
        revenue_summary = RevenueSummaryReportGenerator(
            bills=queryset, is_invoiced=is_earned
        )
        data = revenue_summary.to_response_struct()
        if to_excel:
            data = revenue_summary.to_report_struct()
            excel_bytes = file_utils.FileUtils().write_excel_file(data)
            response = HttpResponse(
                excel_bytes, content_type="application/vnd.ms-excel"
            )
            response[
                "Content-Disposition"
            ] = "attachment; filename=summary_revenue.xlsx"
            return response
        serializer = RevenueSummarySerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data)


class RevenueDetailedViewSet(viewsets.mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Bill.objects.filter(is_invoiced=True)
    serializer_class = RevenueDetailSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = RevenueFilter

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="to_excel",
                location=OpenApiParameter.QUERY,
                description="Print excel",
                type=OpenApiTypes.BOOL,
            ),
            OpenApiParameter(
                name="is_earned",
                location=OpenApiParameter.QUERY,
                description="Is revenue earned",
                type=OpenApiTypes.BOOL,
                default=True,
            ),
        ]
    )
    def list(self, request: Request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        to_excel: bool = utils.str_to_bool(
            request.query_params.get("to_excel", "false")
        )
        is_earned: bool = utils.str_to_bool(request.query_params.get("is_earned"))
        revenue_detail = RevenueDetailReportGenerator(
            bills=queryset, is_invoiced=is_earned
        )
        data_set = revenue_detail.to_response_struct()
        if to_excel:
            data = revenue_detail.to_report_struct()
            excel_bytes = file_utils.FileUtils().write_excel_file(data)
            response = HttpResponse(
                excel_bytes, content_type="application/vnd.ms-excel"
            )
            response["Content-Disposition"] = "attachment; filename=encounters.xlsx"
            return response

        page = self.paginate_queryset(data_set)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(data_set, many=True)
        return Response(serializer.data)
