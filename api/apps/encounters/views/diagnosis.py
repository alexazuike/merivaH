from typing import Type
from rest_framework import viewsets, serializers as dj_serializer, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from drf_spectacular.utils import extend_schema

from .. import models, serializers, permissions as enc_permissions
from api.includes import exceptions, utils as generic_utils


class EncounterDiagnosisViewset(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.DiagnosisValueSerializer
        if self.action in ["list", "retrieve"]:
            return serializers.DiagnosisSerializer

    def get_object(self):
        encounter: models.Encounter = get_object_or_404(
            models.Encounter, pk=self.kwargs["encounter_pk"]
        )
        diagnosis: dict = next(
            (
                diagnosis
                for diagnosis in encounter.diagnosis
                if diagnosis["id"] == self.kwargs["pk"]
            ),
            None,
        )
        if diagnosis:
            return encounter, diagnosis
        raise exceptions.NotFoundException("Encounter disgnosis does not exist")

    def list(self, request, *args, **kwargs):
        encounter: models.Encounter = get_object_or_404(
            models.Encounter, pk=self.kwargs["encounter_pk"]
        )
        page = self.paginate_queryset(encounter.diagnosis)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(encounter.diagnosis, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        _, diagnosis = self.get_object()
        serializer = self.get_serializer(data=diagnosis)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data)

    @extend_schema(
        request=serializers.DiagnosisValueSerializer,
        responses=serializers.DiagnosisSerializer,
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
            value=serializer.validated_data,
            created_by=user_data,
        )
        encounter.diagnosis.append(enc_data.dict())
        encounter.save()
        return Response(data=enc_data.dict(), status=status.HTTP_201_CREATED)

    @extend_schema(request=None, responses=serializers.DiagnosisSerializer)
    @action(
        detail=True, methods=["PATCH"], url_name="confirm_diagnosis", url_path="confirm"
    )
    def confirm_diagnosis(self, request, *args, **kwargs):
        encounter, diagnosis = self.get_object()
        if diagnosis.get("value", {}).get("status") == models.DiagnosisStatus.CONFIRMED:
            raise exceptions.BadRequest("diangosis is already confirmed")
        index = encounter.diagnosis.index(diagnosis)
        diagnosis_update = diagnosis.copy()
        diagnosis_update["value"]["status"] = models.DiagnosisStatus.CONFIRMED
        encounter.diagnosis[index] = diagnosis_update
        encounter.save()
        return Response(data=diagnosis_update, status=status.HTTP_200_OK)
