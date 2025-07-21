from typing import Type

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, filters, status, serializers as rest_serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action

from api.apps.finance import models, serializers


class BillPackageViewset(viewsets.ModelViewSet):
    queryset = models.BillPackage.objects.all()
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return serializers.BillPackageResponseSerializer
        return serializers.BillPackageRequestSerializer


class PatientBillPackageSubViewset(
    viewsets.ReadOnlyModelViewSet, viewsets.GenericViewSet
):
    queryset = models.PatientBillPackageSubscription.objects.all()
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return serializers.PatientBillPackageSubResponseSerializer
        return serializers.PatientBillPackageSubRequestSerializer

    @extend_schema(
        request=serializers.PatientBillPackageSubRequestSerializer,
        responses={201: serializers.PatientBillPackageSubResponseSerializer},
    )
    @action(
        methods=["POST"],
        detail=False,
        url_name="bill_package_subscribe",
        url_path="subscribe",
    )
    def subscribe(self, request: Request, *args, **kwargs):
        serializer: Type[rest_serializers.Serializer] = self.get_serializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        patient_subscribe = serializer.save()
        serializer = serializers.PatientBillPackageSubResponseSerializer(
            instance=patient_subscribe
        )
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class PatientBillPackageUsageViewset(
    viewsets.ReadOnlyModelViewSet, viewsets.GenericViewSet
):
    queryset = models.PatientBillPackageUsage.objects.all().select_related(
        "package_subscription"
    )
    serializer_class = serializers.PatientBillPackageUsageSerializer

    def get_queryset(self):
        subscription_id = self.kwargs.get("subscription_pk")
        subscription = get_object_or_404(
            models.PatientBillPackageSubscription, pk=subscription_id
        )
        return self.queryset.filter(package_subscription=subscription)
