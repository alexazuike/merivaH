from typing import List

from rest_framework import viewsets, filters, permissions, status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from . import models
from . import serializers
from . import filters as nursing_filters
from .permissions.mursing_task import NursingTaskPermission
from api.includes import exceptions, utils


class NursingStationViewset(viewsets.ModelViewSet):
    queryset = models.NursingStation.objects.all()
    serializer_class = serializers.NursingStationSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering = ["-id"]


class NursingServiceViewSet(viewsets.ModelViewSet):
    queryset = models.NursingService.objects.all()
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ["name"]
    ordering = ["-id"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return serializers.NursingServiceResponseSerializer
        return serializers.NursingServiceRequestSerializer


class NursingOrderViewSet(viewsets.ModelViewSet):
    queryset = models.NursingOrder.objects.all()
    serializer_class = serializers.NursingOrderSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = nursing_filters.NursingOrderFilter
    ordering = ["-id"]

    @extend_schema(
        request=serializers.NursingTaskCancelSerializer,
        responses=serializers.NursingOrderSerializer,
    )
    @action(methods=["PATCH"], detail=True, url_name="complete_order", url_path="close")
    def close_order(self, request, *args, **kwargs):
        nursing_order: models.NursingOrder = self.get_object()
        serializer = serializers.NursingTaskCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        disposition = serializer.validated_data.get("disposition")
        nursing_order.close(user=request.user, disposition=disposition)
        serializer = serializers.NursingOrderSerializer(instance=nursing_order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=serializers.NursingTaskCancelSerializer,
        responses=serializers.NursingOrderSerializer,
    )
    @action(methods=["PATCH"], detail=True, url_name="cancel_prder", url_path="cancel")
    def cancel_order(self, request: Request, *args, **kwargs):
        nursing_order: models.NursingOrder = self.get_object()
        serializer = serializers.NursingTaskCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        disposition = serializer.validated_data.get("disposition")
        nursing_order.cancel(user=request.user, disposition=disposition)
        serializer = serializers.NursingOrderSerializer(instance=nursing_order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request: Request, *args, **kwargs):
        instance: models.NursingOrder = self.get_object()
        if instance.status != models.NursingOrderStatus.OPEN:
            raise exceptions.BadRequest("Cannot delete nursing order")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        request=None, responses={200: serializers.NursingTaskSerializer(many=True)}
    )
    @action(methods=["GET"], detail=False, url_path="tasks", url_name="orders_tasks")
    def get_orders_tasks(self, request: Request, *args, **kwargs):
        """Get all tasks present in all unclosed orders"""
        orders: List[models.NursingOrder] = models.NursingOrder.objects.exclude(
            Q(status=models.NursingOrderStatus.CLOSED)
            | Q(status=models.NursingOrderStatus.CANCELLED)
        )
        tasks = []
        for order in orders:
            active_tasks = order.active_tasks
            for task in active_tasks:
                task["order_id"] = order.pk
                tasks.append(task)
        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = serializers.NursingTaskSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.NursingTaskSerializer(tasks, many=True)
        return Response(serializer.data)


class NursingTaskViewSet(
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = serializers.NursingTaskSerializer
    permission_classes = [NursingTaskPermission]

    def get_object(self):
        instance: models.NursingOrder = get_object_or_404(
            models.NursingOrder, pk=self.kwargs["order_pk"]
        )
        nursing_task: dict = next(
            (task for task in instance.tasks if task["id"] == self.kwargs["pk"]),
            None,
        )
        if nursing_task:
            return instance, nursing_task
        raise exceptions.NotFoundException("Nursing activity does not exist")

    def _get_user_data(self, request):
        return utils.trim_user_data(utils.model_to_dict(request.user))

    def _validate_nursing_order(self, nursing_order: models.NursingOrder):
        if nursing_order.status == models.NursingOrderStatus.CLOSED:
            raise exceptions.BadRequest("Nursing order is already closed")
        if nursing_order.status == models.NursingOrderStatus.CANCELLED:
            raise exceptions.BadRequest("Nursing order is already cancelled")

    def _validate_nursing_task(self, nursing_task: dict):
        if nursing_task.get("status") == models.NursingTaskStatus.CLOSED:
            raise exceptions.BadRequest("Nursing task is already closed")
        if nursing_task.get("status") == models.NursingTaskStatus.CANCELLED:
            raise exceptions.BadRequest("Nursing task is already cancelled")

    def list(self, request, *args, **kwargs):
        nursing_order: models.NursingOrder = get_object_or_404(
            models.NursingOrder, pk=self.kwargs["order_pk"]
        )
        page = self.paginate_queryset(nursing_order.tasks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(nursing_order.tasks, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        _, nursing_task = self.get_object()
        serializer = serializers.NursingTaskSerializer(
            data=nursing_task, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        nursing_order: models.NursingOrder = get_object_or_404(
            models.NursingOrder, pk=self.kwargs["order_pk"]
        )
        serializer = serializers.NursingTaskSerializer(
            data=request.data, context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        nursing_order.tasks.append(serializer.validated_data)
        nursing_order.status = models.NursingOrderStatus.SCHEDULED
        nursing_order.save(update_fields=["tasks", "status"])
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=serializers.NursingTaskSerializer(many=True),
        responses={201: serializers.NursingTaskSerializer(many=True)},
    )
    @action(methods=["post"], detail=False, url_path="bulk", url_name="bulk_create")
    @transaction.atomic
    def bulk_create(self, request, *args, **kwargs):
        """Bulk creation of nursing tasks"""
        nursing_order: models.NursingOrder = get_object_or_404(
            models.NursingOrder, pk=self.kwargs["order_pk"]
        )
        serializer = serializers.NursingTaskSerializer(
            data=request.data, context={"request": request}, many=True
        )
        serializer.is_valid(raise_exception=True)
        nursing_order.tasks.extend(serializer.validated_data)
        nursing_order.status = models.NursingOrderStatus.SCHEDULED
        nursing_order.save(update_fields=["tasks", "status"])
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk: int, *args, **kwargs):
        nursing_order, nursing_task = self.get_object()
        self._validate_nursing_order(nursing_order)
        self._validate_nursing_task(nursing_task)
        nursing_order.tasks.remove(nursing_task)
        nursing_order.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        request=serializers.NursingTaskCloseSerializer,
        responses=serializers.NursingTaskSerializer,
    )
    @action(detail=True, methods=["patch"], url_name="close_task", url_path="close")
    @transaction.atomic
    def close_task(self, request, *args, **kwargs):
        nursing_order, nursing_task = self.get_object()
        self._validate_nursing_order(nursing_order)
        self._validate_nursing_task(nursing_task)
        serializer = serializers.NursingTaskCloseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        disposition = serializer.validated_data.get("disposition")
        services = serializer.validated_data.get("nursing_services")
        nursing_task_update = nursing_task.copy()
        nursing_task_update["status"] = models.NursingTaskStatus.CLOSED
        nursing_task_update["closed_by"] = self._get_user_data(request)
        nursing_task_update["closed_at"] = timezone.now().isoformat()
        nursing_task_update["disposition"] = disposition
        nursing_task_update["nursing_services"] = [
            models.NursingServiceSchema(**service).dict() for service in services
        ]
        nursing_order.tasks[
            nursing_order.tasks.index(nursing_task)
        ] = nursing_task_update
        nursing_order.save(update_fields=["tasks"])
        return Response(data=nursing_task_update)

    @extend_schema(
        request=serializers.NursingTaskCancelSerializer,
        responses={status.HTTP_200_OK: serializers.NursingTaskSerializer},
    )
    @action(detail=True, methods=["patch"], url_name="cancel_task", url_path="cancel")
    def cancel_task(self, request, *args, **kwargs):
        nursing_order, nursing_task = self.get_object()
        self._validate_nursing_order(nursing_order)
        self._validate_nursing_task(nursing_task)
        serializer = serializers.NursingTaskCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        disposition = serializer.validated_data.get("disposition")
        nursing_task_update = nursing_task.copy()
        nursing_task_update["status"] = models.NursingTaskStatus.CLOSED
        nursing_task_update["cancelled_by"] = self._get_user_data(request)
        nursing_task_update["cancelled_at"] = timezone.now().isoformat()
        nursing_task_update["disposition"] = disposition
        nursing_order.tasks[
            nursing_order.tasks.index(nursing_task)
        ] = nursing_task_update
        nursing_order.save(update_fields=["tasks"])
        return Response(data=nursing_task_update)
