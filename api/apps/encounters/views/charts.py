import logging
from typing import List

from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from drf_spectacular.utils import extend_schema

from .. import models, serializers
from ..libs.encounter_orders_factory import EncounterServicesOrderFactory
from api.includes import exceptions, utils as generic_utils


logger = logging.getLogger(__name__)


class EncounterChartsViewset(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.EncounterChartValueSerializer
        if self.action in ["list", "retrieve"]:
            return serializers.EncounterChartSerializer

    def get_object(self):
        encounter: models.Encounter = get_object_or_404(
            models.Encounter, pk=self.kwargs["encounter_pk"]
        )
        chart: dict = next(
            (chart for chart in encounter.chart if chart["id"] == self.kwargs["pk"]),
            None,
        )
        if chart:
            return encounter, chart
        raise exceptions.NotFoundException("Encounter chart does not exist")

    @extend_schema(responses=serializers.EncounterChartSerializer)
    def list(self, request, *args, **kwargs):
        """List Encounter Charts"""
        user: User = request.user
        if not user.has_perm("encounters.view_encounter"):
            raise exceptions.PermissionDenied(
                "You don't have permission to view encounter"
            )

        encounter = get_object_or_404(models.Encounter, pk=self.kwargs["encounter_pk"])
        serializer = serializers.EncounterChartSerializer(encounter.chart, many=True)
        # paginate records
        charts = serializer.data[::-1]
        page = self.paginate_queryset(charts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(encounter.diagnosis, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=serializers.EncounterChartValueSerializer,
        responses=serializers.EncounterChartSerializer(many=True),
    )
    def create(self, request, *args, **kwargs):
        encounter: models.Encounter = get_object_or_404(
            models.Encounter, id=self.kwargs["encounter_pk"]
        )
        serializer = serializers.EncounterChartValueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chart_data: dict = request.data

        user: User = request.user
        if not user.has_perm("encounters.change_encounter"):
            raise exceptions.PermissionDenied("You don't have permission to add charts")

        # get embedded orders and make orders
        orders = chart_data.get("orders", {})
        if (
            bool(orders.get("laboratory"))
            or bool(orders.get("imaging"))
            or bool(orders.get("prescription"))
            or bool(orders.get("nursing"))
        ):
            order_factory = EncounterServicesOrderFactory(
                encounter=encounter,
                request=request,
                lab_order_data=orders.get("laboratory"),
                img_order_data=orders.get("imaging"),
                presc_order_data=orders.get("prescription"),
                nursing_order_data=orders.get("nursing"),
            )
            orders.update(order_factory.order_services())

        diagnosis: List = chart_data.get("diagnosis", [])
        if diagnosis:
            diagnosis = [
                models.EncounterObservation(
                    value=value,
                    created_by=generic_utils.trim_user_data(
                        generic_utils.model_to_dict(user)
                    ),
                ).dict()
                for value in diagnosis
            ]
            encounter.diagnosis.extend(diagnosis)

        chart_data["orders"] = orders
        chart_data["diagnosis"] = diagnosis
        enc_chart = models.EncounterChart(
            chart=chart_data,
            created_by=generic_utils.trim_user_data(generic_utils.model_to_dict(user)),
        )
        encounter.chart.append(enc_chart.dict())
        encounter.save()
        serializer = serializers.EncounterSerializer(encounter)
        return Response(serializer.data.get("chart"))

    @extend_schema(
        request=None,
        responses=serializers.EncounterChartSerializer,
    )
    def retrieve(self, request, *args, **kwargs):
        _, chart = self.get_object()
        serializer = self.get_serializer(data=chart)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data)

    @extend_schema(
        request=serializers.EncounterChartValueSerializer,
        responses=serializers.EncounterChartSerializer,
    )
    def update(self, request, *args, **kwargs):
        """
        updates encounter chart
        """
        encounter, chart = self.get_object()
        user = request.user
        if chart["created_by"].get("id") != user.id:
            raise exceptions.PermissionDenied("Inadequate permissions to update chart")
        # serializer = serializers.EncounterChartValueSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        chart_data: dict = request.data
        chart_index = encounter.chart.index(chart)
        chart_update = chart.copy()
        chart_update["chart"].update(chart_data)
        encounter.chart[chart_index] = chart_update
        encounter.save()
        return Response(chart_update)
