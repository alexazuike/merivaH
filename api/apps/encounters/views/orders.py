from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from drf_spectacular.utils import extend_schema

from .. import models, serializers
from api.includes import exceptions, utils as generic_utils


class EncounterOrderViewset(viewsets.GenericViewSet):

    serializer_class = serializers.EncounterServicesOrderSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return serializers.OrderItemSerializer
        if self.action in ["create"]:
            return serializers.EncounterServicesOrderSerializer

    def get_object(self):
        encounter: models.Encounter = get_object_or_404(
            models.Encounter, pk=self.kwargs["encounter_pk"]
        )
        order: dict = next(
            (order for order in encounter.orders if order["id"] == self.kwargs["pk"]),
            None,
        )
        if order:
            return encounter, order
        raise exceptions.NotFoundException("Encounter order does not exist")

    def list(self, request, *args, **kwargs):
        encounter: models.Encounter = get_object_or_404(
            models.Encounter, pk=self.kwargs["encounter_pk"]
        )
        page = self.paginate_queryset(encounter.orders)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(encounter.orders, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        _, order = self.get_object()
        serializer = self.get_serializer(data=order)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data)

    @extend_schema(
        request=serializers.EncounterServicesOrderSerializer,
        responses=serializers.EncounterServicesOrderSerializer,
    )
    def create(self, request, *args, **kwargs):
        encounter: models.Encounter = get_object_or_404(
            models.Encounter, pk=self.kwargs["encounter_pk"]
        )
        user_data = generic_utils.trim_user_data(
            generic_utils.model_to_dict(request.user)
        )
        serializer = serializers.EncounterServicesOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        orders = serializer.save(encounter, user_data, request=request)
        return Response(data=orders, status=201)
