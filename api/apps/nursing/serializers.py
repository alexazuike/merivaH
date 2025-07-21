import json

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from datetime import datetime

from . import models
from api.apps.inventory import models as inv_models
from api.apps.finance import models as fin_models
from api.includes import utils
from api.includes import serializers as generic_serializers


class NursingStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NursingStation
        fields = "__all__"
        read_only_fields = ("created_by", "updated_by")

    def create(self, validated_data: dict):
        user_data = utils.trim_user_data(
            utils.model_to_dict(self.context["request"].user)
        )
        validated_data["created_by"] = user_data
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user_data = utils.trim_user_data(
            utils.model_to_dict(self.context["request"].user)
        )
        instance.updated_by = user_data
        return super().update(instance, validated_data)


class NursingServiceRequestSerializer(serializers.ModelSerializer):
    bill_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        allow_null=True,
        write_only=True,
    )

    cost_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        allow_null=True,
        write_only=True,
    )

    class Meta:
        model = models.NursingService
        exclude = ["audit_log"]
        read_only_fields = ("bill_item_code", "created_by", "updated_by")

    def create(self, validated_data):
        user = self.context["request"].user
        user_data = utils.model_to_dict(user)

        bill_price = validated_data.pop("bill_price", None)
        cost_price = validated_data.pop("cost_price", None)
        validated_data["audit_log"] = [
            utils.AuditLog(
                user=utils.trim_user_data(user_data),
                event=utils.AuditEvent.CREATE,
                fields=self.context["request"].data,
            ).dict()
        ]
        validated_data["created_by"] = user_data
        with transaction.atomic():
            nursing_service = models.NursingService(**validated_data)
            nursing_service._created_by = user_data
            nursing_service._bill_price = bill_price
            nursing_service._cost_price = cost_price
            nursing_service.save()
            return nursing_service

    def update(self, instance: models.NursingService, validated_data: dict):
        fields = self.context["request"].data
        bill_price = validated_data.pop("bill_price", None)
        cost_price = validated_data.pop("cost_price", None)
        user = self.context["request"].user
        user_data = utils.model_to_dict(user)

        instance.audit_log.append(
            utils.AuditLog(
                user=utils.trim_user_data(user_data),
                event=utils.AuditEvent.UPDATE,
                fields=fields,
            ).dict()
        )
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.updated_by = user_data
        instance._bill_price = bill_price
        instance._cost_price = cost_price
        instance.save()
        return instance


class NursingServiceResponseSerializer(serializers.ModelSerializer):
    bill_price = serializers.SerializerMethodField(read_only=True)
    cost_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.NursingService
        exclude = ["audit_log"]

    def get_bill_price(self, obj):
        try:
            bill_item = fin_models.BillableItem.objects.get(
                item_code=obj.bill_item_code
            )
            return bill_item.selling_price
        except fin_models.BillableItem.DoesNotExist:
            return None

    def get_cost_price(self, obj):
        try:
            bill_item = fin_models.BillableItem.objects.get(
                item_code=obj.bill_item_code
            )
            return bill_item.cost
        except fin_models.BillableItem.DoesNotExist:
            return None


class TaskInventorySerializer(serializers.Serializer):
    product = generic_serializers.PkToDictRelatedSeriaizerField(
        required=True, queryset=inv_models.Product.objects.all(), allow_null=False
    )
    store = generic_serializers.PkToDictRelatedSeriaizerField(
        required=True, queryset=inv_models.Product.objects.all(), allow_null=False
    )


class NursingTaskSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    inventory = serializers.ListField(
        allow_empty=True, child=TaskInventorySerializer(), default=[]
    )
    nursing_services = serializers.ListField(
        allow_empty=True,
        child=generic_serializers.PkToDictRelatedSeriaizerField(
            queryset=models.NursingService.objects.all()
        ),
    )
    status = serializers.ChoiceField(
        choices=models.NursingTaskStatus.choices, read_only=True
    )
    type = serializers.ChoiceField(
        choices=models.NursingTaskType.choices, required=True
    )
    bills = serializers.ListField(
        allow_empty=True, read_only=True, child=serializers.IntegerField()
    )
    notes = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    created_by = serializers.JSONField(default=dict, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    scheduled_by = serializers.JSONField(default=dict, read_only=True)
    scheduled_at = serializers.DateTimeField(allow_null=True, required=False)
    closed_by = serializers.JSONField(default=dict, read_only=True)
    closed_at = serializers.DateTimeField(allow_null=True, read_only=True)
    disposition = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )

    def validate(self, attrs: dict):
        user = self.context["request"].user
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        attrs["created_by"] = attrs.get("created_by", user_data)
        attrs = json.loads(
            models.NursingTaskSchema(**attrs).json()
        )  # injects generated id
        return attrs

    def to_representation(self, instance: dict):
        return utils.to_response_struct(instance)


class NursingOrderSerializer(serializers.ModelSerializer):
    tasks = serializers.ListField(
        read_only=True, allow_empty=True, child=NursingTaskSerializer()
    )
    station = generic_serializers.PkToDictRelatedSeriaizerField(
        queryset=models.NursingStation.objects.all()
    )

    class Meta:
        model = models.NursingOrder
        fields = "__all__"
        read_only_fields = (
            "tasks",
            "status",
            "created_by",
            "updated_by",
            "order_id",
            "completed_by",
            "completed_at",
            "cancelled_by",
            "cancelled_at",
        )

    def create(self, validated_data: dict):
        user_data = utils.trim_user_data(
            utils.model_to_dict(self.context["request"].user)
        )
        validated_data["created_by"] = user_data
        return models.NursingOrder.objects.create(**validated_data)

    def update(self, instance: models.NursingOrder, validated_data: dict):
        user_data = utils.trim_user_data(
            utils.model_to_dict(self.context["request"].user)
        )
        instance.updated_by = user_data
        return super().update(instance, validated_data)


class NursingTaskCloseSerializer(serializers.Serializer):
    disposition = serializers.CharField(
        required=True, allow_null=True, allow_blank=True
    )
    nursing_services = serializers.ListField(
        allow_empty=True,
        child=generic_serializers.PkToDictRelatedSeriaizerField(
            queryset=models.NursingService.objects.all()
        ),
    )


class NursingTaskCancelSerializer(serializers.Serializer):
    disposition = serializers.CharField(
        required=True, allow_null=True, allow_blank=True
    )
