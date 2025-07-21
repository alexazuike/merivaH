from datetime import datetime
import logging
from typing import List

from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from api.includes import exceptions, utils
from api.includes.pagination import CustomPagination
from api.apps.users.serializers import UserSerializer
from .. import models, serializers, filters as enc_filters
from ..libs.encounter_orders_factory import EncounterServicesOrderFactory


# Get an instance of a logger
logger = logging.getLogger(__name__)


class EncounterViewSet(viewsets.ModelViewSet):
    queryset = models.Encounter.objects.all()
    serializer_class = serializers.EncounterSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = enc_filters.EncounterFilter
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

    @extend_schema(
        request=serializers.EncounterSignSerializer,
        responses=serializers.EncounterSerializer,
    )
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

        encounter: models.Encounter = self.get_object()
        if encounter.status.casefold() == "DS".casefold():
            return Response({"message": "Encounter is already signed"}, status=400)

        if encounter.status.casefold() == "cancelled".casefold():
            return Response({"message": "Encounter is already cancelled"}, status=400)

        serializer = serializers.EncounterSignSerializer(
            encounter, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        encounter.provider = user_data
        encounter.signed_by = user_data
        encounter.signed_date = datetime.now()
        encounter.status = "DS"
        encounter.save()
        return Response(serializers.EncounterSerializer(encounter).data)

    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="acknowledge",
    )
    def acknowledge(self, request, pk=None):
        """Acknowdge an Encounter"""
        user: User = request.user
        encounter: models.Encounter = self.get_object()

        if not user.has_perm("encounters.acknowledge_encounter"):
            raise exceptions.PermissionDenied(
                "You don't have permission to acknowledge an encounter"
            )
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        encounter.acknowledged_by = user_data
        encounter.provider = user_data
        encounter.acknowledged_at = timezone.now()
        encounter.save()
        return Response(serializers.EncounterSerializer(encounter).data)


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
    patient_encounters = models.Encounter.objects.filter(patient__id=patient_id)
    paginated_data = paginator.paginate_queryset(patient_encounters, request)
    serializer = serializers.EncounterSerializer(paginated_data, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_encounter_status_count(request, status):
    """Gets count of items in encounter with a given status"""
    encounters = models.Encounter.objects.filter(status__iexact=status)
    data = {"count": encounters.count()}
    return Response(data)
