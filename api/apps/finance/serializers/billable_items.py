from rest_framework import serializers

from api.apps.finance import models
from api.includes import utils


class BillableItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BillableItem
        fields = "__all__"
        read_only_fields = (
            "item_code",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )

    def create(self, validated_data):
        user = self.context["request"].user
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        validated_data["created_by"] = user_data
        return super(BillableItemSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        instance.item_code = validated_data.get("item_code", instance.item_code)
        instance.cost = validated_data.get("cost", instance.cost)
        instance.selling_price = validated_data.get(
            "selling_price", instance.selling_price
        )
        instance.description = validated_data.get("description", instance.description)
        instance.module = validated_data.get("module", instance.module)
        instance.updated_by = user_data
        instance.save()
        return instance


class CoPaySerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=models.CoPayValueType.choices(), required=True
    )
    value = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)

    def validate_value(self, data):
        return float(data)


class PriceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PriceList
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "created_by", "updated_by")

    def create(self, validated_data):
        user = self.context["request"].user
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        validated_data["created_by"] = user_data
        price_list = models.PriceList.objects.create(**validated_data)
        return price_list

    def update(self, instance, validated_data):
        user = self.context["request"].user
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.updated_by = user_data
        instance.save()
        return instance


class PriceListItemSerializer(serializers.ModelSerializer):
    co_pay = CoPaySerializer(required=False)
    name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.PriceListItem
        fields = "__all__"
        read_only_fields = (
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "name",
        )

    def get_name(self, obj):
        try:
            billable_item = models.BillableItem.objects.get(
                item_code=obj.bill_item_code
            )
            return billable_item.description
        except models.BillableItem.DoesNotExist:
            return None

    def validate_price_list(self, value):
        if not models.PriceList.objects.filter(name=value).exists():
            raise serializers.ValidationError("Price list does not exist", 400)
        return value

    # def validate(self, data):
    #     bill_item_code = data.get("bill_item_code")
    #     module = data.get("module")

    #     if not models.BillableItem.objects.filter(
    #         item_code=bill_item_code
    #     ).exists():
    #         raise serializers.ValidationError(
    #             "Billable item code does not exist for selected module", 400
    #         )
    #     return data

    def create(self, validated_data):
        user = self.context.get("request").user
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        validated_data["created_by"] = user_data
        return super(PriceListItemSerializer, self).create(validated_data)

    def update(self, instance: models.PriceListItem, validated_data: dict):
        user = self.context.get("request").user
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        validated_data["updated_by"] = user_data
        return super(PriceListItemSerializer, self).update(instance, validated_data)


class PriceListItemUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)


class SinglePriceListDetailSerializer(serializers.Serializer):
    bill_item_code = serializers.CharField(required=True)
    selling_price = serializers.DecimalField(
        required=True, max_digits=10, decimal_places=2
    )
    co_pay = serializers.CharField(required=False)
    is_auth_req = serializers.BooleanField(required=False, default=False)
    is_capitated = serializers.BooleanField(required=False, default=False)
    module = serializers.ChoiceField(required=True, choices=utils.Modules.choices())
    is_exclusive = serializers.BooleanField(required=False, default=False)
    post_auth_allowed = serializers.BooleanField(required=False, default=False)


class PriceListItemBulkSerializer(serializers.Serializer):
    items = serializers.ListField(
        child=SinglePriceListDetailSerializer(), required=True
    )
