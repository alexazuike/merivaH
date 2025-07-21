from typing import List

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema

from . import models
from . import serializers
from .filters.prescription import PrescriptionFilter
from .filters.templates import TemplateFilter
from api.includes import exceptions


class DoseViewSet(viewsets.ModelViewSet):
    queryset = models.Dose.objects.all()
    serializer_class = serializers.DoseSerializers


class UnitViewSet(viewsets.ModelViewSet):
    queryset = models.Unit.objects.all()
    serializer_class = serializers.UnitSerializers


class RouteViewSet(viewsets.ModelViewSet):
    queryset = models.Route.objects.all()
    serializer_class = serializers.RouteSerializer


class FrequencyViewSet(viewsets.ModelViewSet):
    queryset = models.Frequency.objects.all()
    serializer_class = serializers.FrequencySerializer


class DirectionViewSet(viewsets.ModelViewSet):
    queryset = models.Direction.objects.all()
    serializer_class = serializers.DirectionSerializer


class DurationViewSet(viewsets.ModelViewSet):
    queryset = models.Duration.objects.all()
    serializer_class = serializers.DurationSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return serializers.CategoryResponseSerializer
        return serializers.CategoryRequestSerializer


class GenericDrugViewSet(viewsets.ModelViewSet):
    queryset = models.GenericDrug.objects.all()
    serializer_class = serializers.GenericDrugSerializer


class TemplateViewSet(viewsets.ModelViewSet):
    queryset = models.Template.objects.all()
    serializer_class = serializers.TemplateSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TemplateFilter


class StoreViewSet(viewsets.ModelViewSet):
    queryset = models.PharmacyStore.objects.all()
    serializer_class = serializers.PharmacyStoreSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    ordering = "-id"


class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = models.Prescription.objects.all()
    serializer_class = serializers.PrescriptionSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = PrescriptionFilter
    ordering_fields = ("prc_id", "patient__name", "patient__uhid", "status")
    ordering = "-id"

    @extend_schema(request=None, responses={200: serializers.PrescriptionSerializer})
    @action(
        methods=[
            "patch",
        ],
        url_name="confirm_prescription",
        url_path="confirm",
        detail=True,
    )
    def confirm_prescription(self, request, pk=None):
        """Completes a prescription"""
        user = request.user
        prescription: models.Prescription = self.get_object()
        prescription.confirm(user)
        serializer = serializers.PrescriptionSerializer(prescription)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=None, responses={200: serializers.PrescriptionSerializer})
    @action(
        methods=[
            "patch",
        ],
        url_name="cancel_prescription",
        url_path="cancel",
        detail=True,
    )
    def cancel_prescription(self, request, pk=None):
        """Cancels a prescription"""
        user = request.user
        prescription: models.Prescription = self.get_object()
        prescription.cancel(user)
        serializer = serializers.PrescriptionSerializer(prescription)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="download")
    def download_prescription(self, request, pk=None):
        """Creates prescription pdf file for client"""
        user: User = request.user
        prescription: models.Prescription = self.get_object()
        pdf_file = prescription.to_pdf(user)
        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=prescription.pdf"
        return response

    @action(detail=True, methods=["get"], url_path="mail")
    def mail_prescription(self, request, pk=None):
        user: User = request.user
        prescription: models.Prescription = self.get_object()
        prescription.mail_pdf(user)
        return Response(
            data={"message": "Email is being sent"}, status=status.HTTP_200_OK
        )


class PrescriptionDetailViewset(
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    This view helps in the CRUD of each prescription line
    """

    serializer_class = serializers.PrescriptionDetailSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_queryset(self):
        return super().get_queryset()

    def get_object(self) -> dict:
        instance: models.Prescription = get_object_or_404(
            models.Prescription, pk=self.kwargs["pk"]
        )
        prescription_detail = next(
            (
                detail
                for detail in instance.details
                if detail["id"] == self.kwargs["detail_pk"]
            ),
            None,
        )
        if prescription_detail:
            return prescription_detail
        raise exceptions.NotFoundException("Prescription detail does not exist")

    def list(self, request, *args, **kwargs):
        prescription: models.Prescription = get_object_or_404(
            models.Prescription, pk=self.kwargs["pk"]
        )
        page = self.paginate_queryset(prescription.details)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(prescription.details, many=True)
        return Response(serializer.data)

    def put(self, request, pk: int, *args, **kwargs):
        prescription: models.Prescription = get_object_or_404(
            models.Prescription, pk=self.kwargs["pk"]
        )
        detail = self.get_object()
        serializer = serializers.PrescriptionDetailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prescription.details[prescription.details.index(detail)] = detail.update(
            serializer.data
        )
        prescription.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk: int, *args, **kwargs):
        prescription: models.Prescription = get_object_or_404(
            models.Prescription, pk=self.kwargs["pk"]
        )
        detail = self.get_object()
        detail.update(request.data)
        serializer = serializers.PrescriptionDetailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prescription.details[prescription.details.index(detail)] = detail.update(
            serializer.data
        )
        prescription.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk: int, *args, **kwargs):
        prescription: models.Prescription = get_object_or_404(
            models.Prescription, pk=self.kwargs["pk"]
        )
        detail = self.get_object()
        prescription.details.remove(detail)
        prescription.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
