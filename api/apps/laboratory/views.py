import json

from rest_framework import viewsets, filters, permissions, status
from rest_framework.viewsets import mixins
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.decorators import action
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder

from api.includes import file_utils
from api.includes.pagination import CustomPagination
from api.includes import exceptions, utils
from config import preferences
from . import filters as lab_filters
from . import utils as lab_utils
from . import models
from . import serializers
from api.apps.laboratory.libs import LabResultGenerator


class ServiceCenterViewSet(viewsets.ModelViewSet):
    queryset = models.ServiceCenter.objects.all()
    serializer_class = serializers.ServiceCenterSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = lab_filters.ServiceCenterFilter
    ordering_fields = ["name"]
    ordering = ["-id"]


class LabUnitViewSet(viewsets.ModelViewSet):
    queryset = models.LabUnit.objects.all()
    serializer_class = serializers.LabUnitSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = lab_filters.LabUnitFilter
    ordering_fields = ["order_no", "name", "id"]
    ordering = ["-id"]


class LabObservationViewSet(viewsets.ModelViewSet):
    queryset = models.LabObservation.objects.all()
    serializer_class = serializers.LabObservationSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = lab_filters.LabObservationFilter
    ordering_fields = ["name", "uom", "id"]
    ordering = ["-id"]


class LabSpecimenTypeViewSet(viewsets.ModelViewSet):
    queryset = models.LabSpecimenType.objects.all()
    serializer_class = serializers.LabSpecimenTypeSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = lab_filters.LabSpecimenTypeFilter
    ordering_fields = ["name", "color", "id"]
    ordering = ["-id"]


class LabSpecimenViewSet(viewsets.ModelViewSet):
    queryset = models.LabSpecimen.objects.all()
    serializer_class = serializers.LabSpecimenSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = lab_filters.LabSpecimenFilter
    ordering = ["-id"]

    def get_serializer_context(self):
        context = super(LabSpecimenViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context


class LabPanelViewSet(viewsets.ModelViewSet):
    queryset = models.LabPanel.objects.all()
    serializer_class = serializers.LabPanelSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = lab_filters.LabPanelFilter
    ordering_fields = ["name", "active", "id"]
    ordering = ["-id"]

    def get_serializer_context(self):
        context = super(LabPanelViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return serializers.LabPanelResponseSerializer
        return serializers.LabPanelSerializer

    @extend_schema(responses=serializers.LabPanelUnitGroup)
    @action(
        detail=False,
        methods=["get"],
        url_path="unit_group",
    )
    def group_by_unit(self, request):
        """Group lab panels using units"""
        lab_units = list(
            models.LabPanel.objects.order_by("lab_unit")
            .distinct("lab_unit")
            .values_list("lab_unit", flat=True)
        )
        lab_units = models.LabUnit.objects.filter(id__in=lab_units)

        response_data = []
        for unit in lab_units:
            lab_panels = models.LabPanel.objects.filter(lab_unit=unit)
            lab_panels = serializers.LabPanelSerializer(lab_panels, many=True).data
            data = {"lab_unit": unit.name, "lab_panels": lab_panels}

            response_data.append(data)
        return Response(data=response_data, status=status.HTTP_200_OK)


class LabOrderViewSet(viewsets.ModelViewSet):
    queryset = models.LabOrder.objects.all()
    serializer_class = serializers.LabOrderSerializer
    pagination_class = CustomPagination
    filter_backends = [
        filters.OrderingFilter,
        DjangoFilterBackend,
        filters.SearchFilter,
    ]
    filterset_class = lab_filters.LabOrderFilter
    ordering_fields = ["asn", "stat", "ordered_datetime", "id"]
    ordering = ["-id"]
    search_fields = ["patient__name", "service_center__name"]

    def get_serializer_class(self):
        if self.action not in ("download_lab_order_report", "mail_lab_order_report"):
            return self.serializer_class

    def get_serializer_context(self):
        context = super(LabOrderViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[permissions.AllowAny],
        url_path="reports/download",
    )
    def download_lab_order_report(self, request, pk=None):
        """Gets lab order, and make it available for printing"""
        user: User = request.user
        if not user.has_perm("laboratory.send_print_result"):
            raise exceptions.PermissionDenied(
                "Inadequate permission to print lab order report"
            )
        lab_order: models.LabOrder = self.get_object()
        result_generator = LabResultGenerator(
            lab_order=lab_order,
            header=preferences.AppPreferences().use_lab_report_header,
        )
        pdf_file_object = result_generator.render_template_to_pdf()
        response = HttpResponse(pdf_file_object, content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=lab_order.pdf"
        return response

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="reports/mail",
    )
    def mail_lab_order_report(self, request, pk=None):
        """Sends lab order report"""
        user: User = request.user
        if not user.has_perm("laboratory.send_print_result"):
            raise exceptions.PermissionDenied(
                "Inadequate permission to mail lab order report"
            )
        lab_order: models.LabOrder = self.get_object()
        if not lab_order.patient.get("email"):
            raise exceptions.NotFoundException("No patient mail found")
        lab_order.mail_lab_result()
        return Response(
            data={"message": "Email is being sent"}, status=status.HTTP_200_OK
        )


class LabPanelOrderViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = models.LabPanelOrder.objects.all()
    serializer_class = serializers.LabPanelOrderSerializer
    pagination_class = CustomPagination
    filter_backends = [
        filters.OrderingFilter,
        DjangoFilterBackend,
        filters.SearchFilter,
    ]
    filterset_class = lab_filters.LabPanelOrderFilter
    ordering_fields = ["lab_order_id", "status", "id"]
    ordering = ["-id"]
    search_fields = ["patient__name", "patient__uhid"]

    def get_serializer_class(self):
        if self.action not in (
            "download_lab_panel_order_report",
            "mail_lab_panel_order_report",
            "update_lab_panel_order_obv",
        ):
            return self.serializer_class

    def get_permissions(self):
        if self.action in ("partial_update", "update", "update_lab_panel_order_obv"):
            self.permission_classes = [
                permissions.IsAuthenticated,
            ]
        return super(LabPanelOrderViewSet, self).get_permissions()

    def get_serializer_context(self):
        context = super(LabPanelOrderViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        return Response(data)

    @action(
        detail=True,
        methods=["get"],
        url_path="reports/download",
    )
    def download_lab_panel_order_report(self, request, pk=None):
        """Gets lab order, and make it available for printing"""

        user: User = request.user
        if not user.has_perm("laboratory.send_print_result"):
            raise exceptions.PermissionDenied(
                "Inadequate permission to print lab panel order report"
            )

        lab_panel_order: "models.LabPanelOrder" = self.get_object()
        if (
            lab_panel_order.status.casefold()
            == str(lab_utils.LabPanelOrderStatus.APPROVED).casefold()
        ):
            result_generator = LabResultGenerator(
                lab_order=lab_panel_order.lab_order,
                lab_panel_orders=(lab_panel_order,),
                header=preferences.AppPreferences().use_lab_report_header,
            )
            file_blob = result_generator.render_template_to_pdf()
            response = HttpResponse(file_blob, content_type="application/pdf")
            response["Content-Disposition"] = "attachment; filename=lab_order.pdf"
            lab_panel_order.is_result_sent = True
            lab_panel_order.save()

            return response
        raise exceptions.BadRequest("Lab panel order is not approved")

    @action(
        detail=True,
        methods=["get"],
        url_path="reports/mail",
    )
    def mail_lab_panel_order_report(self, request, pk=None):
        """Gets lab order, create pdf if it doesn't exist and send to user mail"""
        user: User = request.user
        if not user.has_perm("laboratory.send_print_result"):
            raise exceptions.PermissionDenied(
                "Inadequate permission to mail lab panel order report"
            )

        lab_panel_order: "models.LabPanelOrder" = self.get_object()
        if (
            lab_panel_order.status.casefold()
            != str(lab_utils.LabPanelOrderStatus.APPROVED).casefold()
        ):
            raise exceptions.BadRequest("Lab panel order is not approved")

        if not lab_panel_order.patient.get("email"):
            raise exceptions.NotFoundException("No Patient mail found")

        lab_panel_order.mail_lab_result()
        lab_panel_order.is_result_sent = True
        lab_panel_order.save()
        return Response(
            data={"message": "Email is being sent"}, status=status.HTTP_200_OK
        )

    @extend_schema(
        request=serializers.LabPanelOrderObservationUpdateSerializer,
        responses=serializers.LabPanelOrderSerializer,
    )
    @action(
        detail=True,
        methods=["put"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="panel",
    )
    @permission_classes([permissions.IsAuthenticated])
    def update_lab_panel_order_obv(self, request, pk=None):
        """Updates lab panel order comments"""
        user: User = request.user
        if not (
            user.has_perm("laboratory.change_labpanelorder")
            or user.has_perm("laboratory.fill_result")
        ):
            raise PermissionDenied(
                "You don't have permission to update lab panel order"
            )

        lab_panel_order: "models.LabPanelOrder" = self.get_object()
        serializers.LabPanelOrderObservationUpdateSerializer(
            data=request.data
        ).is_valid(raise_exception=True)

        comments = request.data.get("comments", None)
        obv = request.data.get("obv")

        lab_panel_order.panel["obv"] = obv
        lab_panel_order.panel["comments"] = (
            comments if comments else lab_panel_order.panel.get("comments", None)
        )

        user_data = utils.trim_user_data(utils.model_to_dict(user))
        audit_log = utils.AuditLog(
            user=user_data, event=utils.AuditEvent.UPDATE, fields=request.data
        ).dict()

        lab_panel_order.audit_log.append(audit_log)
        lab_panel_order.save()

        if lab_panel_order.status.casefold() == "approved".casefold():
            lab_panel_order.mail_lab_result()

        lab_panel_data = serializers.LabPanelOrderSerializer(lab_panel_order).data
        return Response(lab_panel_data)


class LabReportsViewset(viewsets.GenericViewSet):
    queryset = models.LabPanelOrder.objects.all()
    serializer_class = serializers.LabPanelOrderReportsSerializer
    pagination_class = CustomPagination
    filter_backends = [
        filters.OrderingFilter,
        DjangoFilterBackend,
        filters.SearchFilter,
    ]
    filterset_class = lab_filters.LabReportsFilter
    ordering = ["-id"]
    permission_classes = [permissions.AllowAny]

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
        to_excel: bool = request.query_params.get("to_excel")

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
                ] = "attachment; filename=lab_reports.xlsx"
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
                ] = "attachment; filename=lab_reports.xlsx"
                return response
