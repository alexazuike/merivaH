import json

from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.response import Response
from rest_framework import viewsets, filters, permissions, serializers

from .. import filters as enc_filters
from .. import models
from .. import serializers
from api.includes import utils, file_utils


class EncounterReportsViewset(viewsets.GenericViewSet):
    queryset = models.Encounter.objects.all()
    serializer_class = serializers.EncounterReportsSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = enc_filters.EncounterReportsFilter

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
                ] = "attachment; filename=ecounter_reports.xlsx"
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
                response["Content-Disposition"] = "attachment; filename=encounters.xlsx"
                return response
