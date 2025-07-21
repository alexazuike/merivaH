from django.http import HttpResponse
from rest_framework import viewsets, filters, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User

from api.config import exceptions
from api.config.pagination import CustomPagination
from api.apps.users import serializers as user_serializers
from api.apps.patient import models as patient_models
from api.utils import lib
from api.apps.finance.libs import invoice as invoice_lib
from api.apps.finance.libs import price_list as price_list_lib
from api.apps.finance.libs import billable_item as billable_item_lib
from . import models
from . import serializers
from . import filters as finance_filters


class PayerViewSet(viewsets.ModelViewSet):
    queryset = models.Payer.objects.all()
    serializer_class = serializers.PayerSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = finance_filters.PayerFilter
    ordering_fields = ("name",)


class PayerSchemeViewSet(viewsets.ModelViewSet):
    queryset = models.PayerScheme.objects.all()
    serializer_class = serializers.PayerSchemeSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = finance_filters.PayerSchemeFilter
    ordering_fields = ("name", "created_at", "updated_at")

    def get_serializer_context(self):
        context = super(PayerSchemeViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return serializers.PayerSchemeResponseSerializer
        return serializers.PayerSchemeSerializer


class BillableItemViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = models.BillableItem.objects.all()
    serializer_class = serializers.BillableItemSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = finance_filters.BillableItemFilter
    ordering_fields = ("item_code", "cost")
    ordering = ("-id",)

    def get_serializer_context(self):
        context = super(BillableItemViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="module",
                location=OpenApiParameter.QUERY,
                description="Module",
                type=OpenApiTypes.STR,
            )
        ]
    )
    @action(
        methods=["get"],
        detail=False,
        url_path="spreadsheet_download",
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_sheet(self, request):
        """
        Returns a sheet download of the billable items
        """
        user = request.user
        user_data = lib.trim_user_data(user_serializers.UserSerializer(user).data)
        module = request.query_params.get("module", None)
        billable_util = billable_item_lib.BillableItemLib(user_data)
        excel_file_bytes = billable_util.get_billable_item_excel(module=module)
        response = HttpResponse(
            excel_file_bytes,
            content_type="application/vnd.ms-excel",
        )
        response["Content-Disposition"] = "attachment; filename=billable_items.xlsx"
        return response

    @extend_schema(
        operation_id="upload_file",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {"file": {"type": "string", "format": "binary"}},
            }
        },
    )
    @action(
        methods=["post"],
        detail=False,
        url_path="spreadsheet_upload",
        parser_classes=(MultiPartParser,),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def upload_sheet(self, request):
        """
        Uploads a sheet of billable items
        """
        user = request.user
        user_data = lib.trim_user_data(user_serializers.UserSerializer(user).data)
        billable_util = billable_item_lib.BillableItemLib(user_data)
        excel_file = request.FILES["file"]
        if not excel_file:
            raise exceptions.BadRequest("No file uploaded")
        results = billable_util.upload_billable_items_excel(excel_file)
        results = list(filter(lambda item: item is not None, results))
        return Response(
            {
                "success": "Billable items uploaded successfully",
                "failed_items": results,
            }
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="module",
                location=OpenApiParameter.QUERY,
                description="Module",
                type=OpenApiTypes.STR,
            )
        ]
    )
    @action(
        methods=["get"],
        detail=False,
        url_path="price_lists/spreadsheet_template",
        permission_classes=(permissions.IsAuthenticated,),
    )
    def get_billable_items_by_payer_scheme(self, request):
        """
        Returns a list of billable items for a given payer scheme
        """
        user_data = lib.trim_user_data(
            user_serializers.UserSerializer(request.user).data
        )
        billable_item_util = billable_item_lib.BillableItemLib(user_data)
        module = request.query_params.get("module", None)
        excel_file_bytes = billable_item_util.get_price_list_excel(module)
        response = HttpResponse(
            excel_file_bytes,
            content_type="application/vnd.ms-excel",
        )
        response["Content-Disposition"] = "attachment; filename=price_list_items.xlsx"
        return response


class PriceListViewSet(viewsets.ModelViewSet):
    queryset = models.PriceList.objects.all()
    serializer_class = serializers.PriceListSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ("name",)
    ordering_fields = ("name", "created_at", "updated_at")
    ordering = ("-id",)

    def get_serializer_context(self):
        context = super(PriceListViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_serializer_class(self):
        if self.action == "upload_excel":
            return serializers.PriceListItemUploadSerializer
        return super().get_serializer_class()

    @extend_schema(
        operation_id="upload_file",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {"file": {"type": "string", "format": "binary"}},
            }
        },
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="price_list_items/spreadsheet_upload",
        parser_classes=(MultiPartParser,),
        permission_classes=[permissions.IsAuthenticated],
    )
    def upload_excel(self, request, pk=None):
        price_list = self.get_object()
        file = request.FILES["file"]
        user = request.user
        user_data = lib.trim_user_data(user_serializers.UserSerializer(user).data)
        price_list_uploader = price_list_lib.PriceListLib(
            price_list, user_data, excel_file=file
        )
        failed_item_codes = price_list_uploader.upload()
        failed_item_codes = list(
            filter(lambda item: item is not None, failed_item_codes)
        )
        return Response(
            {
                "message": "File uploaded successfully",
                "failed_item_codes": failed_item_codes,
            },
            status=201,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="price_list_items/bulk_create",
        serializer_class=serializers.PriceListItemBulkSerializer,
    )
    def bulk_create(self, request, pk=None):
        price_list = self.get_object()
        user = request.user
        user_data = lib.trim_user_data(user_serializers.UserSerializer(user).data)
        serializers.PriceListItemBulkSerializer(
            data=request.data,
        ).is_valid(raise_exception=True)
        price_list_items = request.data["items"]
        price_list_item_uploader = price_list_lib.PriceListLib(
            price_list, user_data, price_list_items=price_list_items
        )
        faied_item_codes = price_list_item_uploader.upload()
        return Response(
            {
                "message": "Price list items created successfully",
                "failed_item_codes": faied_item_codes,
            },
            status=201,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="module",
                location=OpenApiParameter.QUERY,
                description="Module",
                type=OpenApiTypes.STR,
            )
        ]
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="price_list_items/spreadsheet_download",
        permission_classes=[permissions.IsAuthenticated],
    )
    def download_excel(self, request, pk=None):
        price_list = self.get_object()
        module = request.query_params.get("module", None)
        excel_bytes = price_list_lib.PriceListLib(price_list, request.user).download(
            module
        )
        response = HttpResponse(excel_bytes, content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = "attachment; filename=price_list.xlsx"
        return response


class PriceListItemViewSet(viewsets.ModelViewSet):
    queryset = models.PriceListItem.objects.all()
    serializer_class = serializers.PriceListItemSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = finance_filters.PriceListItemFilter
    ordering = ("-id",)

    def get_serializer_context(self):
        context = super(PriceListItemViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context


class BillViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
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
        request=serializers.BillsPaymentSerializer,
        responses={200: serializers.InvoiceSerializer},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="pay",
        serializer_class=serializers.BillsPaymentSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def pay(self, request):
        user: User = request.user
        if not user.has_perm("finance.pay_bills"):
            raise exceptions.PermissionDenied("Permission to pay bills not granted")
        serializer = serializers.BillsPaymentSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        invoice_created = serializer.save()
        invoice_data = serializers.InvoiceSerializer(invoice_created).data
        return Response(invoice_data, status=201)

    @action(
        detail=False,
        methods=["put"],
        url_path="authorize",
        serializer_class=serializers.InsuranceBillsAuthSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def authorize(self, request):
        """Endpoint authorizes insurance bills"""
        user: User = request.user
        if not user.has_perm("finance.authorize_bills"):
            raise exceptions.PermissionDenied(
                "You do not have permission to authorize insurance bills"
            )
        user_data = lib.trim_user_data(lib.model_to_dict(user))
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


class CashbookViewSet(viewsets.ReadOnlyModelViewSet, viewsets.GenericViewSet):
    queryset = models.CashBook.objects.all()
    serializer_class = serializers.CashbookSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    ordering_fields = ("csb_id", "amount", "status", "created_at")
    ordering = "-id"

    def get_serializer_class(self):
        if self.action in ["list"]:
            return serializers.CashbookSerializer

    @extend_schema(responses=serializers.CashbookSerializer)
    @action(detail=False, methods=["post"], url_path="open")
    def open_cashbook(self, request):
        """opens cashbook for cashier"""
        user: User = request.user
        if not user.has_perm("finance.add_cashbook"):
            return exceptions.PermissionDenied(
                "Inadequate permissions to create cashbook"
            )
        cashbook = models.CashBook.open(user)
        serializer = serializers.CashbookSerializer(instance=cashbook)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(responses=[serializers.CashbookSerializer])
    @action(detail=True, methods=["delete"], url_path="close")
    def close_cashbook(self, request, pk=None):
        """close cashbook for cashier"""
        user: User = request.user
        if not user.has_perm("finance.change_cashbook"):
            return exceptions.PermissionDenied(
                "Inadequate permissions to close cashbook"
            )
        cashbook: models.CashBook = self.get_object()
        cashbook.close()  # closes cashbook
        serializer = serializers.CashbookSerializer(instance=cashbook)
        return Response(
            data={
                "message": f"cashbook {cashbook.csb_id} closed",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = (
        models.PaymentMethod.objects.all()
        .exclude(name__iexact="reserve")
        .exclude(name__iexact="refund")
    )
    serializer_class = serializers.PaymentMethodSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ("name",)
    ordering_fields = ("name", "created_at", "updated_at")
    ordering = ("-id",)

    def get_serializer_context(self):
        context = super(PaymentMethodViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = models.Payment.objects.all()
    serializer_class = serializers.PaymentSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = finance_filters.PaymentFilter
    ordering = ("-id",)

    def get_serializer_context(self):
        context = super(PaymentViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context


class InvoiceViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = models.Invoice.objects.all()
    serializer_class = serializers.InvoiceSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = finance_filters.InvoiceFilter
    ordering = ("-id",)

    def get_serializer_context(self):
        context = super(InvoiceViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return serializers.InvoiceResponseSerializer
        if self.action == "pay_invoice":
            return serializers.InvoicePaymentListSerializer
        return super().get_serializer_class()

    @action(
        detail=True,
        methods=["patch"],
        url_path="confirm",
        permission_classes=[permissions.IsAuthenticated],
    )
    def confirm(self, request, pk=None):
        invoice: models.Invoice = self.get_object()
        user_data = lib.trim_user_data(
            user_serializers.UserSerializer(request.user).data
        )
        patient = patient_models.Patient.objects.get(id=invoice.patient["id"])
        invoice_util = invoice_lib.Invoice(
            patient=patient, invoice=invoice, user_data=user_data
        )
        invoice_util.confirm_invoice()
        return Response({"message": "Invoice confirmed successfully"}, status=200)

    @action(
        detail=True,
        methods=["put"],
        url_path="pay",
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=serializers.InvoicePaymentListSerializer,
    )
    def pay_invoice(self, request, pk=None):
        invoice: models.Invoice = self.get_object()
        serializer = serializers.InvoicePaymentListSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save(invoice=invoice)
        return Response(
            serializers.InvoiceResponseSerializer(invoice).data,
            status=status.HTTP_202_ACCEPTED,
        )

    @extend_schema(
        request=serializers.InvoiceBillsSerializer,
        responses={200: serializers.InvoiceSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="bills",
        permission_classes=[permissions.IsAuthenticated],
    )
    def add_bills(self, request, pk=None):
        """add bills to invoice"""
        invoice: models.Invoice = self.get_object()
        user: User = request.user
        if not user.has_perm("finance.add_bill"):
            raise exceptions.PermissionDenied("You do not have permission to add bills")
        serializer = serializers.InvoiceBillsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice = serializer.add_bills(invoice=invoice)
        return Response(serializers.InvoiceResponseSerializer(invoice).data, status=200)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="bills",
                location=OpenApiParameter.QUERY,
                description="Bill id",
                type={"type": "array", "items": {"type": "number"}},
                explode=True,
            )
        ],
        responses={200: serializers.InvoiceSerializer},
    )
    @add_bills.mapping.delete
    def remove_bills(self, request, pk=None):
        """remove bills from invoice"""
        invoice: models.Invoice = self.get_object()
        user: User = request.user
        if not user.has_perm("finance.remove_bill"):
            raise exceptions.PermissionDenied("You do not have permission to add bills")
        serializer = serializers.InvoiceBillsSerializer(data=dict(request.query_params))
        serializer.is_valid(raise_exception=True)
        invoice = serializer.remove_bills(invoice=invoice)
        return Response(serializers.InvoiceResponseSerializer(invoice).data, status=200)
