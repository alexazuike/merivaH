import json
import math
from typing import List

from pydantic import ValidationError
from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from api.includes import utils, exceptions
from api.includes import serializers as generic_serializers
from api.apps.inventory import models as inv_models
from api.apps.inventory import models as inventory_models
from . import models


class DoseSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.Dose
        fields = "__all__"


class UnitSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.Unit
        fields = "__all__"


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Route
        fields = "__all__"


class FrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Frequency
        fields = "__all__"


class DirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Direction
        fields = "__all__"


class DurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Duration
        fields = "__all__"


class CategoryRequestSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        required=False, queryset=models.Category.objects.all(), allow_null=True
    )

    class Meta:
        model = models.Category
        fields = "__all__"


class CategoryResponseSerializer(serializers.ModelSerializer):
    parent = RecursiveField(allow_null=True)

    class Meta:
        model = models.Category
        fields = "__all__"


class GenericDrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GenericDrug
        fields = "__all__"


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Template
        fields = "__all__"
        read_only_fields = ("created_by", "created_at", "updated_by", "updated_at")

    def create(self, validated_data):
        user = self.context["request"].user
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        validated_data["created_by"] = user_data
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        instance.updated_by = user_data
        return super().update(instance, validated_data)


class PharmacyStoreSerializer(serializers.ModelSerializer):
    inv_store = serializers.PrimaryKeyRelatedField(
        queryset=inv_models.Store.objects.filter(is_pharmacy=True), required=True
    )

    class Meta:
        model = models.PharmacyStore
        fields = "__all__"
        read_only_fields = ("created_by", "created_at", "updated_by", "updated_at")

    def create(self, validated_data):
        user = self.context["request"].user
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        validated_data["created_by"] = user_data
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        instance.updated_by = user_data
        return super().update(instance, validated_data)


class PrescriptionDetailSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    generic_drug = generic_serializers.PkToDictRelatedSeriaizerField(
        required=True, queryset=models.GenericDrug.objects.all(), allow_null=False
    )
    product = generic_serializers.PkToDictRelatedSeriaizerField(
        required=True, queryset=inventory_models.Product.objects.all(), allow_null=True
    )
    dose = generic_serializers.PkToDictRelatedSeriaizerField(
        required=True, queryset=models.Dose.objects.all(), allow_null=False
    )
    unit = generic_serializers.PkToDictRelatedSeriaizerField(
        required=True, queryset=models.Unit.objects.all(), allow_null=False
    )
    route = generic_serializers.PkToDictRelatedSeriaizerField(
        required=True, queryset=models.Route.objects.all(), allow_null=False
    )
    frequency = generic_serializers.PkToDictRelatedSeriaizerField(
        required=True, queryset=models.Frequency.objects.all(), allow_null=False
    )
    direction = generic_serializers.PkToDictRelatedSeriaizerField(
        required=True, queryset=models.Direction.objects.all(), allow_null=False
    )
    duration = generic_serializers.PkToDictRelatedSeriaizerField(
        required=True, queryset=models.Duration.objects.all(), allow_null=False
    )
    dispense_quantity = serializers.IntegerField(
        required=True, allow_null=False, min_value=1
    )
    status = serializers.ChoiceField(
        allow_null=False,
        allow_blank=False,
        choices=models.PrescriptionDetailStatus.choices,
    )
    note = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def _calc_dispsense_quantity(
        self, dose: dict, frequency: dict, duration: dict, product: dict
    ) -> int:
        """Calculates dispense quantity"""
        dispense_quantity = 1
        if not product:
            return dispense_quantity
        dispense_quantity = math.ceil(
            (
                dose.get("multiplier")
                * frequency.get("multiplier")
                * duration.get("multiplier")
            )
            / product.get("divider")
        )
        return dispense_quantity

    def validate(self, attrs: dict):
        product, generic_drug = attrs.get("product"), attrs.get("generic_drug")
        dose, frequency, duration = (
            attrs.get("dose"),
            attrs.get("frequency"),
            attrs.get("duration"),
        )
        dispense_qty = attrs.get("dispense_quantity")

        # computed_dispense_qty = self._calc_dispsense_quantity(
        #     dose, frequency, duration, product
        # )
        # if computed_dispense_qty != dispense_qty:
        #     raise exceptions.BadRequest("Incorrect Dispense Quantity")

        if product:
            if not product.get("is_drug"):
                raise serializers.ValidationError("Product must be a drug")
            if product.get("generic_drug", {}).get("id") != generic_drug.get("id"):
                raise serializers.ValidationError(
                    detail="Product dooesn't match generic drug specified"
                )
        return super().validate(attrs)


class PrescriptionSerializer(serializers.ModelSerializer):
    details = PrescriptionDetailSerializer(required=True, many=True)
    store = generic_serializers.PkToDictRelatedSeriaizerField(
        required=True, queryset=inventory_models.Store.objects.all(), allow_null=True
    )

    class Meta:
        model = models.Prescription
        fields = "__all__"
        read_only_fields = (
            "created_by",
            "updated_by",
            "prc_id",
            "status",
            "fulfilled_at",
            "fulfilled_by",
            "cancelled_at",
            "cancelled_by",
        )

    def validate_details(self, data):
        data: List[dict] = json.loads(json.dumps(data))
        try:
            data = [models.PrescriptionDetailSchema(**detail).dict() for detail in data]
        except ValidationError as e:
            raise exceptions.BadRequest(str(e))
        return data

    def create(self, validated_data: dict):
        created_by = utils.trim_user_data(
            utils.model_to_dict(instance=self.context["request"].user)
        )
        validated_data["created_by"] = created_by
        validated_data["prescribing_physician"] = validated_data.get(
            "prescribing_physican", created_by
        )
        prescription = models.Prescription.objects.create(**validated_data)
        return prescription

    def update(self, instance, validated_data: dict):
        updated_by = utils.trim_user_data(
            utils.model_to_dict(instance=self.context["request"].user)
        )
        validated_data["updated_by"] = updated_by
        return super().update(instance, validated_data)
