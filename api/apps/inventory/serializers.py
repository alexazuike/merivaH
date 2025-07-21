import json
from typing import List

from django.db import transaction
from django.db.models import F
from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from . import models
from .libs.stock_movement_factory import StockMovementFactory
from api.includes import utils, exceptions
from api.includes import serializers as generic_serializers


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


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Store
        fields = "__all__"
        read_only_fields = ("created_by", "updated_by")

    def create(self, validated_data):
        user = self.context["request"].user
        user_data = utils.model_to_dict(user)
        validated_data["created_by"] = user_data
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        user_data = utils.model_to_dict(user)
        validated_data["updated_by"] = user_data
        return super().update(instance, validated_data)


class ProductSerializer(serializers.ModelSerializer):
    category = generic_serializers.PkToDictRelatedSeriaizerField(
        queryset=models.Category.objects.all(), allow_null=False, required=True
    )
    generic_drug = generic_serializers.PkToDictRelatedSeriaizerField(
        queryset=models.Category.objects.all(), allow_null=False, required=True
    )
    bill_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        allow_null=True,
        write_only=True,
    )

    class Meta:
        model = models.Product
        fields = "__all__"
        read_only_fields = [
            "code",
            "sec_id",
            "created_by",
            "updated_by",
            "bill_item_code",
        ]

    @transaction.atomic
    def create(self, validated_data: dict):
        user = self.context["request"].user
        user_data = utils.model_to_dict(user)
        validated_data["category"] = json.loads(
            json.dumps(validated_data.pop("category", {}))
        )
        validated_data["generic_drug"] = json.loads(
            json.dumps(validated_data.pop("generic_drug", {}))
        )
        validated_data["created_by"] = user_data
        bill_price = validated_data.pop("bill_price")
        product = models.Product(**validated_data)
        product._created_by = user_data
        product._bill_price = bill_price
        product._cost_price = validated_data.get("cost")
        product.save()
        return product

    @transaction.atomic
    def update(self, instance: models.Product, validated_data: dict):
        user = self.context["request"].user
        user_data = utils.model_to_dict(user)
        instance.updated_by = user_data
        instance.generic_drug = json.loads(
            json.dumps(validated_data.pop("generic_drug", instance.generic_drug))
        )
        instance.category = json.loads(
            json.dumps(validated_data.pop("category", instance.category))
        )
        instance.code = validated_data.get("code", instance.code)
        instance.name = validated_data.get("name", instance.name)
        instance.uom = validated_data.get("uom", instance.uom)
        instance.cost = validated_data.get("cost", instance.cost)
        instance.divider = validated_data.get("divider", instance.divider)
        instance.description = validated_data.get("description", instance.description)
        instance.is_drug = validated_data.get("is_drug", instance.is_drug)
        instance._bill_price = validated_data.get("bill_price")
        instance._cost_price = validated_data.get("cost")
        instance.save()
        return instance


class StockSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=1, allow_null=False)
    product = generic_serializers.PkToDictRelatedSeriaizerField(
        required=True, queryset=models.Product.objects.all(), allow_null=False
    )
    store = generic_serializers.PkToDictRelatedSeriaizerField(
        required=True, queryset=models.Product.objects.all(), allow_null=False
    )

    class Meta:
        model = models.Store
        fields = "__all__"

    def create(self, validated_data: dict):
        validated_data["product"] = utils.copy_dict(
            validated_data.get("product"), ["id", "name"]
        )
        validated_data["store"] = utils.copy_dict(
            validated_data.get("store"), ["id", "name", "type"]
        )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data["product"] = utils.copy_dict(
            utils.model_to_dict(validated_data.get("product")), ["id", "name"]
        )
        validated_data["store"] = utils.copy_dict(
            utils.model_to_dict(validated_data.get("store")), ["id", "name", "type"]
        )
        return super().update(instance, validated_data)


class StockProductLineSerializer(serializers.Serializer):
    product = generic_serializers.PkToDictRelatedSeriaizerField(
        required=True, queryset=models.Store.objects.all(), allow_null=False
    )
    quantity = serializers.IntegerField(required=True, min_value=1, allow_null=False)


class StockMovementLineSerializer(serializers.ModelSerializer):
    product = generic_serializers.PkToDictRelatedSeriaizerField(
        required=True, queryset=models.Store.objects.all(), allow_null=False
    )

    class Meta:
        model = models.StockMovementLine
        fields = "__all__"
        read_only_fields = [
            "source_location",
            "destination_location",
            "approved_by",
            "approved_at",
            "cancelled_by",
            "cancelled_at",
            "updated_by",
            "move_id",
            "status",
        ]

    def update(self, instance: models.StockMovementLine, validated_data: dict):
        instance.updated_by = utils.model_to_dict(self.context["request"].user)
        instance.product = validated_data.get("product", instance.product)
        instance.quantity = validated_data.get("quantity", instance.quantity)
        instance.save()
        return instance


class StockMovementSerializer(serializers.ModelSerializer):
    source_location = generic_serializers.PkToDictRelatedSeriaizerField(
        required=False, queryset=models.Store.objects.all()
    )
    destination_location = generic_serializers.PkToDictRelatedSeriaizerField(
        required=False, queryset=models.Store.objects.all()
    )
    products = serializers.ListField(
        required=True,
        child=StockProductLineSerializer(),
        allow_empty=False,
        write_only=True,
    )
    lines = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.StockMovement
        fields = "__all__"
        read_only_fields = [
            "status",
            "approved_by",
            "approved_at",
            "cancelled_at",
            "cancelled_by",
            "move_id",
        ]

    def get_lines(self, obj: models.StockMovement):
        lines = models.StockMovementLine.objects.filter(move_id=obj.move_id)
        line_objs = [utils.model_to_dict(line) for line in lines]
        return line_objs

    @transaction.atomic
    def create(self, validated_data: dict):
        stock_movevment_factory = StockMovementFactory(
            type=validated_data.get("type"),
            source_location=validated_data.get("source_location"),
            destination_location=validated_data.get("destination_location"),
            products=validated_data.get("products"),
            user=self.context["request"].user,
        )
        stock_movement = stock_movevment_factory.create()
        return stock_movement

    @transaction.atomic
    def update(self, instance: models.StockMovement, validated_data: dict):
        if instance.status != models.StockMovementStatus.DRAFT:
            raise exceptions.BadRequest("Cannot update non-draft stock movements")

        validated_data.pop("products", None)
        instance.source_location = utils.copy_dict(
            validated_data.get("source_location", instance.source_location),
            ["id, name", "type"],
        )
        instance.destination_location = utils.copy_dict(
            validated_data.get("destination_location", instance.destination_location),
            ["id, name", "type"],
        )
        instance.type = validated_data.get("type", instance.type)
        instance.save()
        stock_movement_lines = models.StockMovementLine.objects.filter(
            move_id=instance.move_id
        )
        stock_movement_lines.update(
            destination_location=self._get_store_stock(
                instance.destination_location, F("product")
            ),
            source_location=self._get_store_stock(
                instance.source_location, F("product")
            ),
        )
        return instance
