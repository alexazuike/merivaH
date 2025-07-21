import json
from datetime import datetime
from typing import List
from uuid import uuid4

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import viewsets, filters, permissions, serializers, exceptions
from rest_framework.decorators import api_view, permission_classes, APIView, action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.http import HttpResponse
from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiResponse,
    OpenApiParameter,
)
from drf_spectacular.types import OpenApiTypes

from api.includes import exceptions, utils, file_utils
from api.includes import permissions as app_permissions
from api.apps.users.serializers import UserSerializer
from .models import Clinic, Encounter
from .serializers import (
    ClinicSerializer,
    ClinicResponseSerializer,
    EncounterSerializer,
    EncounterReportsSerializer,
    EncounterChartDTOSerializer,
    EncounterChartSerializer,
    ChartItemSerializer,
    EncounterServicesOrder,
    ItemChartDTOSerializer,
    EncounterSignSerializer,
    OrdersChartSerializer,
)
from .libs.encounter_orders_factory import EncounterChartStruct
from .filters import EncounterFilter, EncounterReportsFilter, ClinicFilter
from api.includes.pagination import CustomPagination


class ClinicViewSet(viewsets.ModelViewSet):
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = ClinicFilter
    ordering_fields = ["name", "department"]
    ordering = ["-id"]

    def get_serializer_context(self):
        context = super(ClinicViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ClinicResponseSerializer
        return super().get_serializer_class()


class EncounterViewSet(viewsets.ModelViewSet):
    queryset = Encounter.objects.all()
    serializer_class = EncounterSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = EncounterFilter
    search_fields = [
        "encounter_id",
        "patient__name",
        "patient__uhid" "clinic__name",
        "clinic__Department__name",
        "provider__provider__name",
    ]
    ordering = ["-id"]

    def get_serializer_context(self):
        context = super(EncounterViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            self.permission_classes = [
                permissions.IsAuthenticated,
            ]
        return super(EncounterViewSet, self).get_permissions()

    @extend_schema(request=EncounterSignSerializer, responses=EncounterSerializer)
    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def sign(self, request, pk=None):
        user: User = request.user
        if not user.has_perm("encounters.sign_encounter"):
            raise exceptions.PermissionDenied(
                "You don't have permission to sign encounter"
            )

        encounter: Encounter = self.get_object()
        if encounter.status.casefold() == "DS".casefold():
            return Response({"message": "Encounter is already signed"}, status=400)

        if encounter.status.casefold() == "cancelled".casefold():
            return Response({"message": "Encounter is already cancelled"}, status=400)

        serializer = EncounterSignSerializer(
            encounter, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        encounter.provider = user_data
        encounter.signed_by = user_data
        encounter.signed_date = datetime.now()
        encounter.status = "DS"
        encounter.save()
        return Response(EncounterSerializer(encounter).data)

    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="acknowledge",
    )
    def acknowledge(self, request, pk=None):
        """Acknowdge an Encounter"""
        user: User = request.user
        encounter: Encounter = self.get_object()

        if not user.has_perm("encounters.acknowledge_encounter"):
            raise exceptions.PermissionDenied(
                "You don't have permission to acknowledge an encounter"
            )
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        encounter.acknowledged_by = user_data
        encounter.provider = user_data
        encounter.acknowledged_at = timezone.now()
        encounter.save()
        return Response(EncounterSerializer(encounter).data)

    @action(
        detail=True,
        methods=["post"],
        url_path="orders",
        serializer_class=EncounterServicesOrder,
    )
    def order_services(self, request, pk=None):
        encounter: Encounter = self.get_object()
        user_data = utils.trim_user_data(utils.model_to_dict(request.user))
        serializer = EncounterServicesOrder(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save(encounter, user_data, request=request)
        return Response(data=data, status=201)


class EncounterChartListCreateView(APIView):
    queryset = Encounter.objects.all()
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    @extend_schema(responses=EncounterChartSerializer)
    def get(self, request, id, format=None):
        """List Encounter Charts"""
        try:
            user: User = request.user
            if not user.has_perm("encounters.view_encounter"):
                raise exceptions.PermissionDenied(
                    "You don't have permission to view encounter"
                )

            encounter = Encounter.objects.get(id=id)
            chart = {"chart": encounter.chart}
            serializer = EncounterChartSerializer(chart)
            return Response(serializer.data)
        except Encounter.DoesNotExist:
            return Response(status=404, data={"message": "Encounter not found"})

    @extend_schema(
        request=EncounterChartDTOSerializer, responses=EncounterChartSerializer
    )
    def post(self, request, id, format=None):
        EncounterChartDTOSerializer(data=request.data).is_valid(raise_exception=True)
        data = request.data
        chart: dict = data["chart"]
        current_date_time = timezone.now()
        user: User = request.user

        if chart.get("vitals"):
            if not (
                user.has_perm("encounters.take_vitals")
                or user.has_perm("encounters.change_encounter")
            ):
                raise exceptions.PermissionDenied(
                    "You don't have permission to take vitals"
                )
        else:
            if not user.has_perm("encounters.change_encounter"):
                raise exceptions.PermissionDenied(
                    "You don't have permission to add charts"
                )

        provider_object = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        }
        try:
            encounter: Encounter = Encounter.objects.get(id=id)
            for key, value in chart.items():
                chart_value = EncounterChartStruct(
                    id=str(uuid4()),
                    value=value,
                    created_by=provider_object,
                    created_at=current_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                ).dict()

                if type(value) == list:
                    chart_value = [
                        EncounterChartStruct(
                            id=str(uuid4()),
                            value=record,
                            created_by=provider_object,
                            created_at=current_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                        ).dict()
                        for record in value
                    ]

                if encounter.chart.get(key):
                    if type(chart_value) == list:
                        encounter.chart[key].extend(chart_value)
                    else:
                        encounter.chart[key].append(chart_value)
                else:
                    if type(chart_value) == list:
                        encounter.chart[key] = chart_value
                    else:
                        encounter.chart[key] = [chart_value]
            encounter.save()
            serializer = EncounterSerializer(encounter)
            return Response(serializer.data.get("chart"))

        except Encounter.DoesNotExist:
            return Response({"message": "Encounter does not exist."}, status=404)


class EncounterChartDetailView(viewsets.ViewSet):
    """API View to get details of a specific Encounter Chart"""

    queryset = Encounter.objects.all()
    permission_classes = [
        permissions.IsAuthenticated,
        app_permissions.AppModelPermissions,
    ]

    @extend_schema(
        responses={
            200: inline_serializer(
                name="get chart value",
                fields={
                    "result": serializers.ListField(child=ChartItemSerializer()),
                },
            ),
            404: OpenApiResponse(
                description="Encounter does not exist.",
                response=OpenApiTypes.OBJECT,
            ),
        }
    )
    def list(self, request, id, chart_type):
        try:
            encounter = Encounter.objects.get(id=id)
            chart = encounter.chart.get(chart_type, [])
            serializer = ChartItemSerializer(chart, many=True)
            if chart_type.casefold() == "orders".casefold():
                serializer = OrdersChartSerializer(chart)
            return Response({"result": serializer.data})
        except Encounter.DoesNotExist:
            return Response({"message": "Encounter does not exist."}, status=404)

    @extend_schema(responses=ChartItemSerializer())
    def retrieve(self, request, id, chart_type, item_id):
        try:
            encounter = Encounter.objects.get(id=id)
            chart = encounter.chart.get(chart_type, [])
            items_search = [item for item in chart if item["id"] == item_id]
            item = items_search[0] if items_search else None
            if item:
                serializer = ChartItemSerializer(item)
                return Response(serializer.data)
            return Response({"message": "Chart item not found."}, status=404)
        except Encounter.DoesNotExist:
            return Response({"message": "Encounter does not exist."}, status=404)

    @extend_schema(request=ItemChartDTOSerializer(), responses=ChartItemSerializer())
    def update(self, request, id, chart_type, item_id):
        try:
            encounter: Encounter = Encounter.objects.get(id=id)
            chart: List = encounter.chart.get(chart_type, [])
            items_search = [item for item in chart if item["id"] == item_id]
            item: dict = items_search[0] if items_search else None

            logged_in_user = request.user
            item_created_by = item.get("created_by", {})

            if item:
                if logged_in_user.id != item_created_by.get("id"):
                    raise exceptions.BadRequest(
                        "You are not authorized to update this item."
                    )

                ItemChartDTOSerializer(data=request.data).is_valid(raise_exception=True)
                update_data = request.data
                for chart_item in encounter.chart[chart_type]:
                    if chart_item["id"] == item_id:
                        chart_item["value"] = update_data["value"]
                        break
                encounter.save()
                return Response(item)
            return Response({"message": "Chart item not found."}, status=404)
        except Encounter.DoesNotExist:
            return Response({"message": "Encounter does not exist."}, status=404)
        except exceptions.BadRequest as e:
            return Response({"message": str(e)}, status=400)


class EncounterReportsViewset(viewsets.GenericViewSet):
    queryset = Encounter.objects.all()
    serializer_class = EncounterReportsSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = EncounterReportsFilter
    permission_classes = [permissions.IsAuthenticated]

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
                    json.loads(json.dumps(serializer.data))
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
                    json.loads(json.dumps(serializer.data))
                )
                excel_bytes = file_utils.FileUtils().write_excel_file(data)
                response = HttpResponse(
                    excel_bytes, content_type="application/vnd.ms-excel"
                )
                response["Content-Disposition"] = "attachment; filename=encounters.xlsx"
                return response


@extend_schema(responses=UserSerializer(many=True))
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_providers(request, group_name):
    users = User.objects.filter(groups__name=group_name)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_all_patients_encounter(request, patient_id):
    paginator = CustomPagination()
    patient_encounters = Encounter.objects.filter(patient__id=patient_id)
    paginated_data = paginator.paginate_queryset(patient_encounters, request)
    serializer = EncounterSerializer(paginated_data, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_encounter_status_count(request, status):
    """Gets count of items in encounter with a given status"""
    encounters = Encounter.objects.filter(status__iexact=status)
    data = {"count": encounters.count()}
    return Response(data)
