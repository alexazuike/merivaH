from django.db import transaction
from rest_framework import serializers

from .. import models
from api.apps.finance import models as finance_models
from api.includes import utils as generic_utils


class MessageRequestServiceSerializer(serializers.ModelSerializer):
    bill_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, write_only=True, allow_null=True, default=0
    )

    cost_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, write_only=True, allow_null=True, default=0
    )

    class Meta:
        model = models.MessageService
        fields = "__all__"
        read_only_fields = [
            "bill_item_code",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]

    @transaction.atomic
    def create(self, validated_data: dict):
        bill_price = validated_data.pop("bill_price", None)
        cost_price = validated_data.pop("cost_price", None)
        user = self.context["request"].user
        user_data = generic_utils.trim_user_data(generic_utils.model_to_dict(user))
        validated_data["created_by"] = user_data

        message_service = models.MessageService = models.MessageService(
            **validated_data
        )
        message_service._created_by = user_data
        message_service._bill_price = bill_price
        message_service._cost_price = cost_price
        message_service.save()
        return message_service

    @transaction.atomic
    def update(self, instance: models.MessageService, validated_data: dict):
        bill_price = validated_data.pop("bill_price", None)
        cost_price = validated_data.pop("cost_price", None)

        instance.name = validated_data.get("name", instance.name)
        instance.type = validated_data.get("type", instance.type)
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance._bill_price = bill_price
        instance._cost_price = cost_price
        instance.save()
        return instance


class MessageResponseServiceSerializer(serializers.ModelSerializer):
    bill_price = serializers.SerializerMethodField(read_only=True)
    cost_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.MessageService
        fields = "__all__"
        read_only_fields = [
            "bill_item_code",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]

    def get_bill_price(self, obj):
        try:
            bill_item = finance_models.BillableItem.objects.get(
                item_code=obj.bill_item_code
            )
            return bill_item.selling_price
        except finance_models.BillableItem.DoesNotExist:
            return None

    def get_cost_price(self, obj):
        try:
            bill_item = finance_models.BillableItem.objects.get(
                item_code=obj.bill_item_code
            )
            return bill_item.cost
        except finance_models.BillableItem.DoesNotExist:
            return None
