from django.db import transaction
from rest_framework import serializers

from .. import models
from api.apps.facilities import models as facility_models
from api.apps.finance import models as finance_models
from api.includes import utils as generics_utils


class ClinicSerializer(serializers.ModelSerializer):
    bill_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, write_only=True, allow_null=True, default=0
    )

    cost_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, write_only=True, allow_null=True, default=0
    )

    department = serializers.PrimaryKeyRelatedField(
        required=True, queryset=facility_models.Department.objects.all()
    )

    class Meta:
        model = models.Clinic
        fields = "__all__"
        read_only_fields = [
            "bill_item_code",
        ]

    @transaction.atomic
    def create(self, validated_data: dict):
        bill_price = validated_data.pop("bill_price", None)
        cost_price = validated_data.pop("cost_price", None)
        template_data = validated_data.pop("templates",None)
        user = self.context["request"].user
        user_data = generics_utils.trim_user_data(generics_utils.model_to_dict(user))

        clinic: models.Clinic = models.Clinic.objects.create(**validated_data)
        clinic._created_by = user_data
        clinic._bill_price = bill_price
        clinic._cost_price = cost_price
        clinic.save()
        clinic.templates.set(template_data)
        return clinic

    @transaction.atomic
    def update(self, instance: models.Clinic, validated_data: dict):
        bill_price = validated_data.pop("bill_price", None)
        cost_price = validated_data.pop("cost_price", None)
        template_data = validated_data.pop("templates",None)

        instance.name = validated_data.get("name", instance.name)
        instance.department = validated_data.get("department", instance.department)
        instance._bill_price = bill_price
        instance._cost_price = cost_price
        instance.save()
        instance.templates.set(template_data)
        return instance


class ClinicResponseSerializer(serializers.ModelSerializer):
    bill_price = serializers.SerializerMethodField(read_only=True)
    cost_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Clinic
        fields = "__all__"
        depth = 1
        read_only_fields = [
            "bill_item_code",
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
