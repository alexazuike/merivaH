from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db.models import Subquery
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from api.includes import exceptions
from api.includes.pagination import CustomPagination
from api.apps.users import serializers as user_serializers
from api.apps.patient import models as patient_models
from api.includes import utils
from api.apps.finance.libs import price_list as price_list_lib
from api.apps.finance.libs import billable_item as billable_item_lib
from api.apps.finance import models, serializers
from api.apps.finance import filters as finance_filters


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
        user_data = utils.trim_user_data(utils.model_to_dict(user))
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
        user_data = utils.trim_user_data(utils.model_to_dict(request.user))
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
        user_data = utils.trim_user_data(utils.model_to_dict(request.user))
        billable_item_util = billable_item_lib.BillableItemLib(user_data)
        module = request.query_params.get("module", None)
        excel_file_bytes = billable_item_util.get_price_list_excel(module)
        response = HttpResponse(
            excel_file_bytes,
            content_type="application/vnd.ms-excel",
        )
        response["Content-Disposition"] = "attachment; filename=price_list_items.xlsx"
        return response

    @extend_schema(
        request=None,
        responses={200: serializers.PayerSchemeResponseSerializer(many=True)},
    )
    @action(
        methods=["GET"],
        detail=True,
        url_path=r"patients/(?P<patient_id>\w+)/insurance-schemes",
        permission_classes=[
            permissions.IsAuthenticated,
        ],
    )
    def get_patient_bill_item_insurances(
        self, request, patient_id: str, *args, **kwargs
    ):
        """Get Patient Insurance packages covering billable item"""
        billable_item: models.BillableItem = self.get_object()
        patient = patient_models.Patient.objects.filter(pk=patient_id)
        if not patient.exists():
            raise exceptions.NotFoundException("Patient details not found")
        patient = patient.first()
        schemes = [
            scheme
            for scheme in patient.payment_scheme
            if scheme.get("payer_scheme", {}).get("type")
            in (
                models.PayerSchemeType.CORPORATE.value,
                models.PayerSchemeType.INSURANCE.value,
            )
        ]
        if not schemes:
            raise exceptions.NotFoundException(
                "Patient has no insurance coverage for billable item"
            )

        price_list_items = models.PriceListItem.objects.filter(
            bill_item_code=billable_item.item_code
        )
        payer_schemes = models.PayerScheme.objects.select_related("price_list").filter(
            pk__in=[scheme.get("payer_scheme", {}).get("id") for scheme in schemes],
            price_list__pricelistitem__in=Subquery(price_list_items.values("pk")),
        )
        if not payer_schemes.exists():
            raise exceptions.NotFoundException(
                "Patient has no insurance coverage for billable item"
            )
        serializer = serializers.PayerSchemeResponseSerializer(
            instance=payer_schemes, many=True
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)


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
        user_data = utils.trim_user_data(utils.model_to_dict(user))
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
        user_data = utils.trim_user_data(utils.model_to_dict(user))
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
