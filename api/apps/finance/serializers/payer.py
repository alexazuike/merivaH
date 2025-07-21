from rest_framework import serializers

from api.apps.finance import models
from api.includes import exceptions
from api.includes import utils


class PayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Payer
        fields = "__all__"


class PayerSchemeSerializer(serializers.ModelSerializer):
    payer = serializers.PrimaryKeyRelatedField(
        queryset=models.Payer.objects.all(), required=True
    )

    price_list = serializers.PrimaryKeyRelatedField(
        queryset=models.PriceList.objects.all(), required=False, allow_null=True
    )
    type = serializers.CharField(required=True)

    class Meta:
        model = models.PayerScheme
        fields = "__all__"
        read_onlY_fields = ("created_at", "updated_at", "created_by", "updated_by")

    def validate_type(self, value):
        value = models.PayerSchemeType.get_scheme_type(value)
        if not value:
            raise exceptions.BadRequest("Not a valid scheme type choice")
        return value

    def create(self, validated_data: dict):
        user = self.context["request"].user
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        validated_data["created_by"] = user_data
        return super(PayerSchemeSerializer, self).create(validated_data)

    def update(self, instance: models.PayerScheme, validated_data):
        user = self.context["request"].user
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        validated_data["updated_by"] = user_data
        return super(PayerSchemeSerializer, self).update(instance, validated_data)


class PayerSchemeResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PayerScheme
        fields = "__all__"
        depth = 1


class PayerSchemeCategory(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    category = serializers.CharField(required=True)
