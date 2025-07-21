import json
import os

from django.core.serializers.json import DjangoJSONEncoder
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema_view,
)
from django.http import HttpResponse
from rest_framework import viewsets, filters, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action


from api.apps.finance import serializers as finance_serializers
from api.includes.pagination import CustomPagination
from api.includes import exceptions
from api.includes import file_utils
from .filters import PatientFilter, PatientReportFilter, PatientFileFilter
from . import models
from . import serializers


class PatientViewSet(viewsets.ModelViewSet):
    queryset = models.Patient.objects.all()
    serializer_class = serializers.PatientSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = PatientFilter
    ordering_fields = ["firstname", "lastname", "uhid", "id"]
    ordering = ["id"]

    # get patient by uhid
    @action(detail=False, methods=["get"], url_path="uhid/(?P<uhid>[^/.]+)")
    def get_by_uhid(self, request, uhid):
        try:
            patient = models.Patient.objects.get(uhid=uhid)
            serializer = serializers.PatientSerializer(patient)
            return Response(serializer.data)
        except models.Patient.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"message": "Patient not found"}
            )

    @action(detail=True, methods=["patch"])
    def profile_picture(self, request, pk=None):
        try:
            patient = models.Patient.objects.get(pk=pk)
            patient.profile_picture = request.data.get("profile_picture")
            patient.save()
            return Response(
                data={"message": "Profile picture uploaded successfully"},
                status=status.HTTP_200_OK,
            )

        except models.Patient.DoesNotExist:
            return Response(
                data={"message": "Patient does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @extend_schema(
        request=serializers.PatientDepositSerializer,
        responses=finance_serializers.PaymentSummarySerializer,
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="deposit",
        permission_classes=[permissions.IsAuthenticated],
    )
    def handle_deposit(self, request, pk=None):
        with transaction.atomic():
            try:
                user = request.user
                if not (
                    user.has_perm("patient.add_deposit")
                    or user.has_perm("patient.change_patient")
                ):
                    raise exceptions.PermissionDenied(
                        "You do not have permission to add deposit"
                    )

                patient = models.Patient.objects.get(pk=pk)
                deposit_serializer = serializers.PatientDepositSerializer(
                    data=request.data, context={"user": request.user}
                )
                deposit_serializer.is_valid(raise_exception=True)
                payment_summary = deposit_serializer.save(patient=patient)
                response = finance_serializers.PaymentSummarySerializer(
                    data=payment_summary.dict()
                )
                response.is_valid(raise_exception=True)
                return Response(
                    data=response.data,
                    status=status.HTTP_202_ACCEPTED,
                )
            except models.Patient.DoesNotExist:
                raise exceptions.NotFoundException("Patient not found")


class PatientsReportsViewSet(viewsets.GenericViewSet):
    queryset = models.Patient.objects.all()
    serializer_class = serializers.PatientSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = PatientReportFilter
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
                data = json.loads(json.dumps(data, cls=DjangoJSONEncoder))
                excel_bytes = file_utils.FileUtils().write_excel_file(data)
                response = HttpResponse(
                    excel_bytes, content_type="application/vnd.ms-excel"
                )
                response["Content-Disposition"] = "attachment; filename=patients.xlsx"
                return response
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            if not to_excel:
                return Response(data)
            else:
                data = json.loads(json.dumps(data, cls=DjangoJSONEncoder))
                excel_bytes = file_utils.FileUtils().write_excel_file(data)
                response = HttpResponse(
                    excel_bytes, content_type="application/vnd.ms-excel"
                )
                response["Content-Disposition"] = "attachment; filename=patients.xlsx"
                return response


@extend_schema_view(
    create=extend_schema(
        request={"multipart/form-data": serializers.PatientFileSerializer}
    )
)
class PatientFileViewset(viewsets.ModelViewSet):
    queryset = models.PatientFile.objects.all()
    serializer_class = serializers.PatientFileSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = PatientFileFilter

    def destroy(self, request, *args, **kwargs):
        instance: models.PatientFile = self.get_object()
        file_utils.FileUtils().remove_static_file(instance.path)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        instance: models.PatientFile = self.get_object()
        file_content = file_utils.FileUtils().get_static_file(instance.path)
        file_name = str(instance.path()).split(os.sep)[-1]
        response = HttpResponse(file_content)
        response["Content-Disposition"] = f"attachment; filename={file_name}"
        return response
