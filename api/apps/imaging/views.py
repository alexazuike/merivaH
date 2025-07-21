import json

from django.http import HttpResponse
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import viewsets, filters, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

from api.includes import exceptions, file_utils, utils
from api.includes import pagination
from config import preferences
from . import filters as imaging_filters
from .libs.imaging_report_generator import ImagingReportStruct
from .models import (
    ServiceCenter,
    Modality,
    ImagingObservation,
    ImagingOrder,
    ImagingObservationOrder,
    ImagingObserverOrderAttachments,
)

from .serializers import (
    ImagingObservationOrderReportsSerializer,
    ImagingObservationOrderAttachmentSerializer,
    ServiceCenterSerializer,
    ModalitySerializer,
    ImagingObservationSerializer,
    ImagingObvResponseSerializer,
    ImagingOrderSerializer,
    ImagingObservationOrderSerializer,
    ImagingObvOrderResponseSerializer,
    ImgObvModalityGroup,
)


class ServiceCenterViewSet(viewsets.ModelViewSet):
    queryset = ServiceCenter.objects.all()
    serializer_class = ServiceCenterSerializer
    pagination_class = pagination.CustomPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = imaging_filters.ServiceCenterFilter
    ordering_fields = ["name"]


class ModalityViewSet(viewsets.ModelViewSet):
    queryset = Modality.objects.all()
    serializer_class = ModalitySerializer
    pagination_class = pagination.CustomPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = imaging_filters.ModalityFilter
    ordering_fields = ["name"]


class ImagingObservationViewSet(viewsets.ModelViewSet):
    queryset = ImagingObservation.objects.all()
    serializer_class = ImagingObservationSerializer
    pagination_class = pagination.CustomPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = imaging_filters.ImagingObservationFilter
    ordering_fields = ["name"]
    ordering = ["-id"]

    def get_serializer_context(self):
        context = super(ImagingObservationViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ImagingObvResponseSerializer
        return ImagingObservationSerializer

    @extend_schema(
        responses=ImgObvModalityGroup,
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="modality_group",
    )
    def group_by_modality(self, request):
        """Group Imaging Observation by modality"""
        modalities = list(
            ImagingObservation.objects.order_by("modality")
            .distinct("modality")
            .values_list("modality", flat=True)
        )
        print(modalities)
        modalities = Modality.objects.filter(id__in=modalities)
        response_data = []
        for modality in modalities:
            img_obvs = ImagingObservation.objects.filter(modality=modality)
            img_obvs = ImagingObservationSerializer(img_obvs, many=True).data
            data = {"modality": modality.name, "img_observations": img_obvs}
            response_data.append(data)
        return Response(data=response_data, status=status.HTTP_200_OK)


class ImagingOrderViewSet(viewsets.ModelViewSet):
    queryset = ImagingOrder.objects.all()
    serializer_class = ImagingOrderSerializer
    pagination_class = pagination.CustomPagination
    filter_backends = [
        filters.OrderingFilter,
        DjangoFilterBackend,
        filters.SearchFilter,
    ]
    filterset_class = imaging_filters.ImagingOrderFilter
    search_fields = [
        "patient__name",
        "patient__id",
        "ordered_by__name",
        "ordered_by__id",
    ]
    ordering_fields = ["name"]
    ordering = ["-id"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        return Response(data)

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="reports/download",
    )
    def download_report(self, request, pk=None):
        """
        Download the report for the imaging order
        """
        from . import utils as img_utils

        img_order: ImagingOrder = self.get_object()
        user: User = request.user

        if not user.has_perm("imaging.mail_print_result"):
            raise exceptions.PermissionDenied(
                "Inadequate permission to print imaging order report"
            )

        file_blob = img_utils.generate_img_order_reports(
            img_order=img_order,
            header=preferences.AppPreferences().use_img_report_header,
        )
        response = HttpResponse(file_blob, content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=lab_order.pdf"

        return response

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="reports/mail",
    )
    def mail_report(self, request, pk=None):
        img_order: ImagingOrder = self.get_object()
        user: User = request.user

        if not user.has_perm("imaging.mail_print_result"):
            raise exceptions.PermissionDenied(
                "Inadequate permission to mail imaging order report"
            )

        if not img_order.patient.get("email"):
            raise exceptions.NotFoundException("No patient mail found")

        img_order.mail_report()

        return Response(
            data={"message": "Email is being sent"}, status=status.HTTP_200_OK
        )


class ImagingObservationOrderViewSet(viewsets.ModelViewSet):
    queryset = ImagingObservationOrder.objects.all()
    serializer_class = ImagingObservationOrderSerializer
    pagination_class = pagination.CustomPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = imaging_filters.ImagingObservationOrderFilter
    ordering_fields = ["status"]
    ordering = ["-id"]

    def get_serializer_context(self):
        context = super(ImagingObservationOrderViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ImagingObvOrderResponseSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            self.permission_classes = (permissions.IsAuthenticated,)
        return super(ImagingObservationOrderViewSet, self).get_permissions()

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="reports/download",
    )
    def download_img_obv_order_report(self, request, pk=None):
        """
        Download imaging observation order report
        """
        from . import utils as img_utils

        img_obv_order: ImagingObservationOrder = self.get_object()
        user: User = request.user

        if not user.has_perm("imaging.mail_print_result"):
            raise exceptions.PermissionDenied(
                "Inadequate permission to print imaging observation order report"
            )

        if (
            img_obv_order.status.casefold()
            == str(img_utils.ImagingObservationOrderStatus.APPROVED).casefold()
        ):
            file_blob = img_utils.generate_img_obv_order_reports(
                img_obv_order=img_obv_order,
                header=preferences.AppPreferences().use_img_report_header,
            )
            response = HttpResponse(file_blob, content_type="application/pdf")
            response["Content-Disposition"] = "attachment; filename=lab_order.pdf"

            img_obv_order.is_result_sent = True
            img_obv_order.save()

            return response
        raise exceptions.BadRequest("Imaging observation order is not approved")

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="reports/mail",
    )
    def mail_img_obv_order_report(self, request, pk=None):
        img_obv_order: ImagingObservationOrder = self.get_object()
        user: User = request.user

        if not user.has_perm("imaging.mail_print_result"):
            raise exceptions.PermissionDenied(
                "Inadequate permission to mail imaging observation order report"
            )

        if img_obv_order.status.casefold() != "APPROVED".casefold():
            raise exceptions.BadRequest("Imaging Observation order is not approved")

        if not img_obv_order.patient.get("email"):
            raise exceptions.NotFoundException("No patient mail found")

        img_obv_order.mail_result()
        img_obv_order.is_result_sent = True
        img_obv_order.save()

        return Response(
            data={"message": "Email is being sent"}, status=status.HTTP_200_OK
        )


class ImagingReportsViewset(viewsets.GenericViewSet):
    queryset = ImagingObservationOrder.objects.all()
    serializer_class = ImagingObservationOrderReportsSerializer
    pagination_class = pagination.CustomPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = imaging_filters.ImagingObservationOrderFilter

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
        to_excel: bool = utils.str_to_bool(request.query_params.get("to_excel"))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
            if not to_excel:
                return self.get_paginated_response(data)
            else:
                serializer = self.get_serializer(queryset, many=True)
                data = utils.to_report_structure(
                    data=json.loads(json.dumps(serializer.data, cls=DjangoJSONEncoder))
                )
                excel_bytes = file_utils.FileUtils().write_excel_file(data)
                response = HttpResponse(
                    excel_bytes, content_type="application/vnd.ms-excel"
                )
                response[
                    "Content-Disposition"
                ] = "attachment; filename=imaging reports.xlsx"
                return response
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            if not to_excel:
                return Response(data)
            else:
                data = utils.to_report_structure(
                    json.loads(json.dumps(data, cls=DjangoJSONEncoder))
                )
                excel_bytes = file_utils.FileUtils().write_excel_file(data)
                response = HttpResponse(
                    excel_bytes, content_type="application/vnd.ms-excel"
                )
                response[
                    "Content-Disposition"
                ] = "attachment; filename=imaging_reports.xlsx"
                return response


class ImagingObservationOrderAttachmentsViewSet(viewsets.ModelViewSet):
    serializer_class = ImagingObservationOrderAttachmentSerializer
    pagination_class = pagination.CustomPagination

    def get_queryset(self):
        return ImagingObserverOrderAttachments.objects.filter(
            img_obv_order=self.kwargs["pk"]
        )

    def get_serializer_context(self):
        img_obv_order = get_object_or_404(ImagingObservationOrder, pk=self.kwargs["pk"])
        return {
            "request": self.request,
            "format": self.format_kwarg,
            "view": self,
            "img_obv_order": img_obv_order,
        }
