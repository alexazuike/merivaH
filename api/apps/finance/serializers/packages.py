from typing import List

from django.db import transaction
from django.db.models.query import QuerySet
from rest_framework import serializers

from api.apps.finance.libs.billing import Billing as BillingFactory
from api.apps.finance.libs.invoice import Invoice as InvoiceFactory
from api.apps.finance import models, utils as fin_utils
from api.apps.patient import models as patient_models
from api.includes import utils as generic_utils, serializers as generic_serializers
from .payment import MakePaymentSerializer


class BillPackageItemSerializer(serializers.Serializer):
    billable_item = generic_serializers.PkToDictRelatedSeriaizerField(
        queryset=models.BillableItem.objects.all()
    )
    quantity = serializers.IntegerField(min_value=1)


class BillPackageRequestSerializer(serializers.ModelSerializer):
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
    billable_items = BillPackageItemSerializer(many=True)

    class Meta:
        model = models.BillPackage
        fields = "__all__"
        read_only_fields = ("package_code", "bill_item_code")

    def _get_user_data(self):
        user = self.context["request"].user
        return generic_utils.model_to_dict(user)

    @transaction.atomic
    def create(self, validated_data: dict):
        validated_data["created_by"] = self._get_user_data()
        bill_price = validated_data.pop("bill_price", None)
        cost_price = validated_data.pop("cost_price", None)
        instance = models.BillPackage(**validated_data)
        instance._bill_price = bill_price
        instance._cost_price = cost_price
        instance._created_by = validated_data["created_by"]
        instance.save()
        return instance

    @transaction.atomic
    def update(self, instance: models.BillPackage, validated_data: dict):
        bill_price = validated_data.pop("bill_price", None)
        cost_price = validated_data.pop("cost_price", None)
        validated_data["updated_by"] = self._get_user_data()
        instance._bill_price = bill_price
        instance._cost_price = cost_price
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class BillPackageResponseSerializer(serializers.ModelSerializer):
    bill_price = serializers.SerializerMethodField(read_only=True)
    cost_price = serializers.SerializerMethodField(read_only=True)
    billable_items = BillPackageItemSerializer(many=True)

    class Meta:
        model = models.BillPackage
        fields = "__all__"

    def get_bill_price(self, obj):
        try:
            bill_item = models.BillableItem.objects.get(item_code=obj.bill_item_code)
            return bill_item.selling_price
        except models.BillableItem.DoesNotExist:
            return None

    def get_cost_price(self, obj):
        try:
            bill_item = models.BillableItem.objects.get(item_code=obj.bill_item_code)
            return bill_item.cost
        except models.BillableItem.DoesNotExist:
            return None


class PatientBillPackageSubRequestSerializer(serializers.ModelSerializer):
    patient = generic_serializers.PkToDictRelatedSeriaizerField(
        queryset=patient_models.Patient.objects.all()
    )
    bill_package = generic_serializers.PkToDictRelatedSeriaizerField(
        queryset=models.BillPackage.objects.all()
    )

    class Meta:
        model = models.PatientBillPackageSubscription
        fields = "__all__"
        read_only_fields = ("bill", "expiration_date")

    def _get_user_data(self):
        user = self.context["request"].user
        return generic_utils.model_to_dict(user)

    def create(self, validated_data):
        validated_data["created_by"] = self._get_user_data()
        bill_package: dict = validated_data["bill_package"]
        package_subscription = models.PatientBillPackageSubscription(**validated_data)
        package_subscription._bill_item_code = bill_package.get("bill_item_code")
        package_subscription._quantity = 1
        package_subscription._name = bill_package.get("name")
        package_subscription.save()
        return package_subscription


class PatientBillPackageSubResponseSerializer(serializers.ModelSerializer):
    bill = serializers.SerializerMethodField()

    class Meta:
        model = models.PatientBillPackageSubscription
        fields = "__all__"

    def get_bill(self, obj):
        bill_obj = models.Bill.objects.get(id=int(obj.bill))
        bill_data = generic_utils.model_to_dict(bill_obj)
        return fin_utils.clean_bill_details(bill_data)


class PatientBillPackageUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PatientBillPackageUsage
        fields = "__all__"
        depth = 1
