from typing import Type
from rest_framework import viewsets, serializers as dj_serializer, status
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from drf_spectacular.utils import extend_schema

from .. import models, serializers, permissions as enc_permissions
from api.includes import exceptions, utils as generic_utils


class EncounterVitalsViewset(viewsets.GenericViewSet):
    permission_classes = [enc_permissions.EncounterVitalsPermission]

    def get_serializer_class(self) -> Type[dj_serializer.Serializer]:
        if self.action == "create":
            return serializers.EncounterObservationRequestSerializer
        if self.action in ["list", "retrieve"]:
            return serializers.EncounterObservationSerializer

    def get_object(self):
        encounter: models.Encounter = get_object_or_404(
            models.Encounter, pk=self.kwargs["encounter_pk"]
        )
        vital: dict = next(
            (vital for vitals in encounter.vitals if vitals["id"] == self.kwargs["pk"]),
            None,
        )
        if vital:
            return encounter, vital
        raise exceptions.NotFoundException("Encounter vitals does not exist")

    def list(self, request, *args, **kwargs):
        encounter: models.Encounter = get_object_or_404(
            models.Encounter, pk=self.kwargs["encounter_pk"]
        )
        page = self.paginate_queryset(encounter.vitals)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(encounter.orders, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        _, vital = self.get_object()
        serializer = self.get_serializer(data=vital)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data)

    @extend_schema(
        request=serializers.EncounterObservationRequestSerializer,
        responses=serializers.EncounterObservationSerializer,
    )
    def create(self, request, *args, **kwargs):
        encounter: models.Encounter = get_object_or_404(
            models.Encounter, pk=self.kwargs["encounter_pk"]
        )
        user_data = generic_utils.trim_user_data(
            generic_utils.model_to_dict(request.user)
        )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enc_data = models.EncounterObservation(
            value=serializer.validated_data["value"],
            created_by=user_data,
        )
        encounter.vitals.append(enc_data.dict())
        encounter.save()
        return Response(data=enc_data.dict(), status=status.HTTP_201_CREATED)
