from rest_framework import serializers

from . import models
from api.includes import utils


class SalutationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Salutation
        fields = ["salutations"]


class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Gender
        fields = "__all__"


class LGASerializers(serializers.ModelSerializer):
    class Meta:
        model = models.LGA
        fields = ["lga"]


class DistrictSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.District
        fields = ["district"]


class StateSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.State
        fields = ["state", "country"]
        depth = 1

    def to_representation(self, instance):
        """return just state and the country"""
        ret = super().to_representation(instance)
        context = {"state": ret["state"], "country": ret["country"]["country"]}
        return context


class CountrySerializers(serializers.ModelSerializer):
    class Meta:
        model = models.Country
        fields = ["id", "country"]
        depth = 1


class OccupationSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.Occupation
        fields = "__all__"


class MaritalStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MaritalStatus
        fields = "__all__"


class ReligionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Religion
        fields = "__all__"


class IdentitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Identity
        fields = ["name"]


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Template
        fields = "__all__"

    def create(self, validated_data):
        user = self.context["request"].user
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        validated_data["created_by"] = user_data
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        validated_data["created_by"] = user_data
        return super().update(instance, validated_data)


class DiagosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Diagnosis
        fields = "__all__"


class ServiceArmSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ServiceArm
        fields = "__all__"


class AppPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AppPreferences
        fields = "__all__"


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DocumentType
        fields = "__all__"
