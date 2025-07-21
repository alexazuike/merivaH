from rest_framework import serializers

from .. import models
from api.includes import utils as generics_utils


class EncounterTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EncounterTemplate
        fields = "__all__"
        read_only_fields = ("created_by", "updated_by")

    def create(self, validated_data: dict):
        user = self.context.get("request").user
        user_data = generics_utils.trim_user_data(generics_utils.model_to_dict(user))
        validated_data["created_by"] = user_data
        return super().create(validated_data)

    def update(self, instance: models.EncounterTemplate, validated_data: dict):
        user = self.context.get("request").user
        user_data = generics_utils.trim_user_data(generics_utils.model_to_dict(user))
        instance.updated_by = user_data
        return super().update(instance, validated_data)
