from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend

from api.includes.pagination import CustomPagination
from api.apps.finance import models, serializers
from api.apps.finance import filters as finance_filters


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

    @extend_schema(request=None, responses=serializers.PayerSchemeCategory(many=True))
    @action(
        methods=["get"],
        detail=False,
        url_path="categories",
        url_name="scheme_categories",
    )
    def get_scheme_categories(self, request):
        categories_data = models.PayerSchemeType.get_response()
        serializer = serializers.PayerSchemeCategory(data=categories_data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
