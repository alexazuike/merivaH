from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend

from api.includes import exceptions
from . import serializers
from . import models
from .filters.store import StoreFilter
from .filters.products import ProductFilter


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return serializers.CategoryResponseSerializer
        return serializers.CategoryRequestSerializer


class StoreViewset(viewsets.ModelViewSet):
    queryset = models.Store.objects.all()
    serializer_class = serializers.StoreSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = StoreFilter
    ordering_fields = ("name", "type")
    ordering = "-id"

    @action(methods=["GET"], detail=False, url_path="types")
    def get_store_types(self, request, *args, **kwargs):
        store_types = models.StoreTypes.values
        stores = list(enumerate(store_types))
        stores = {store[0]: store[1] for store in stores}
        return Response(stores)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = ProductFilter
    ordering_fields = ("code", "sec_id")
    ordering = "-id"


class StockViewSet(viewsets.ModelViewSet):
    queryset = models.Stock.objects.all()
    serializer_class = serializers.StockSerializer


class StockMovementLineViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.DestroyModelMixin,
):
    serializer_class = serializers.StockMovementLineSerializer

    def get_queryset(self):
        try:
            stock_movement = models.StockMovement.objects.get(
                id=self.kwargs["movement_pk"]
            )
            return models.StockMovementLine.objects.filter(
                move_id=stock_movement.move_id
            )
        except models.StockMovement.DoesNotExist:
            return exceptions.NotFoundException("Stock Movement is not found")


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = models.StockMovement.objects.all()
    serializer_class = serializers.StockMovementSerializer

    @action(
        detail=True, methods=["patch"], url_path="approve", url_name="approve_movement"
    )
    def approve(self, request, pk=None):
        stock_movement: models.StockMovement = self.get_object()
        user: User = request.user
        if not user.has_perm("inventory.approve_stock_movement"):
            raise exceptions.PermissionDenied(
                "Inadequate permissions to approve stock movement"
            )
        stock_movement.approve(user)
        serializer = serializers.StockMovementSerializer(stock_movement)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True, methods=["delete"], url_path="cancel", url_name="cancel_movement"
    )
    def cancel(self, request, pk=None):
        stock_movement: models.StockMovement = self.get_object()
        user: User = request.user
        if not user.has_perm("inventory.cancel_stock_movement"):
            raise exceptions.PermissionDenied(
                "Inadequate permissions to cancel stock movement"
            )
        stock_movement.cancel(user)
        serializer = serializers.StockMovementSerializer(stock_movement)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="move", url_name="move_stock")
    def move_stock(self, request, pk=None):
        stock_movement: models.StockMovement = self.get_object()
        user: User = request.user
        if not user.has_perm("inventory.move_stock"):
            raise exceptions.PermissionDenied("Inadequate permissions to move stock")
        with transaction.atomic():
            stock_movement.move(user)
        serializer = serializers.StockMovementSerializer(stock_movement)
        return Response(serializer.data, status=status.HTTP_200_OK)
