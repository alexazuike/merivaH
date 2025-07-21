from rest_framework import viewsets, filters, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User

from api.includes import exceptions
from api.includes.pagination import CustomPagination
from api.apps.patient import models as patient_models
from api.includes import utils
from api.apps.finance import models, serializers
from api.apps.finance import filters as finance_filters


class BillViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = models.Bill.objects.all()
    serializer_class = serializers.BillSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = finance_filters.BillFilter
    ordering = ("-id",)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return serializers.BillResponseSerializer
        return super().get_serializer_class()

    def destroy(self, request, *args, **kwargs):
        instance: models.Bill = self.get_object()
        if instance.is_invoiced:
            raise exceptions.BadRequest("Cannot delete invoiced bill")

        if instance.is_reserved:
            patient = patient_models.Patient.objects.filter(
                id=instance.patient.get("id")
            )
            if patient.exists():
                patient_obj: patient_models.Patient = patient.first()
                patient_obj.add_deposit(instance.selling_price)
                patient_obj.pay_from_reserve(instance.selling_price)
                patient.save()

        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        filters=None,
        request=serializers.BillsPaymentSerializer,
        responses={200: serializers.PaymentSummarySerializer},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="pay",
        permission_classes=[permissions.IsAuthenticated],
    )
    def pay(self, request, *args, **kwargs):
        """Pay bills"""
        user: User = request.user
        if not user.has_perm("finance.accept_payment"):
            raise exceptions.PermissionDenied(
                "Permission to accept payment for bills not granted"
            )
        serializer = serializers.BillsPaymentSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        payments_summary = serializer.save()
        serializer = serializers.PaymentSummarySerializer(data=payments_summary.dict())
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @action(
        detail=False,
        methods=["PUT"],
        url_path="authorize",
        serializer_class=serializers.InsuranceBillsAuthSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def authorize(self, request, *args, **kwargs):
        """Endpoint authorizes insurance bills"""
        user: User = request.user
        if not user.has_perm("finance.authorize_bills"):
            raise exceptions.PermissionDenied(
                "You do not have permission to authorize insurance bills"
            )
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        serializer = serializers.InsuranceBillsAuthSerializer(
            data=request.data, context={"user": user_data}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data={
                "message": "Insurance bills authorized and cleared",
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(responses=serializers.BillResponseSerializer)
    @action(
        detail=True,
        methods=["patch"],
        url_path="unreserve",
    )
    def unreserve_bills(self, request, pk=None):
        """Unreserve bills that has been reserved"""
        bill: models.Bill = self.get_object()
        user: User = request.user
        if not user.has_perm("finance.unreserve_bill"):
            raise exceptions.PermissionDenied(
                "Permission to unreserve bill not granted"
            )
        bill = bill.unreserve()
        serializer = serializers.BillResponseSerializer(instance=bill)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses=serializers.BillResponseSerializer)
    @action(
        detail=True,
        methods=["patch"],
        url_path="reserve",
    )
    def reserve_bills(self, request, pk=None):
        """Reserve bill that is not reserved"""
        bill: models.Bill = self.get_object()
        user: User = request.user
        if not user.has_perm("finance.reserve_bill"):
            raise exceptions.PermissionDenied("Permission to reserve bill not granted")
        bill = bill.reserve()
        serializer = serializers.BillResponseSerializer(instance=bill)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=serializers.BillTransferSerializer,
        responses=serializers.BillResponseSerializer,
    )
    @action(detail=True, methods=["patch"], url_path="transfer")
    def transfer_bill(self, request, pk=None):
        """Transfer bills from one scheme"""
        bill: models.Bill = self.get_object()
        user: User = request.user
        if not user.has_perm("finance.transfer_bill"):
            raise exceptions.PermissionDenied("Permission to transfer bill not granted")
        request_serializer = serializers.BillTransferSerializer(
            data=request.data, context={"request": request}
        )
        request_serializer.is_valid(raise_exception=True)
        bill = request_serializer.save(bill)
        response_serializer = serializers.BillResponseSerializer(instance=bill)
        return Response(data=response_serializer.data, status=status.HTTP_200_OK)
