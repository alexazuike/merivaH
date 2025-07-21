from datetime import datetime
from typing import Union
import uuid

from django.db import transaction
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from .. import models
from .. import utils as enc_utils
from .diagnosis import DiagnosisValueSerializer
from api.apps.finance import models as finance_models
from api.apps.finance import utils as finance_utils
from api.apps.laboratory import serializers as lab_serializers
from api.apps.imaging import serializers as img_serializers
from api.apps.pharmacy import serializers as pharm_serializers
from api.includes import serializers as generic_serializers
from api.includes import utils as generics_utils


class EncounterSerializer(serializers.ModelSerializer):
    payment_scheme = serializers.IntegerField(required=False, write_only=True)
    bill = serializers.SerializerMethodField()

    class Meta:
        model = models.Encounter
        fields = "__all__"
        read_only_fields = (
            "encounter_id",
            "bill",
            "acknowledged_by",
            "acknowledged_at",
        )

    def get_bill(self, obj):
        if obj.bill:
            bill_obj = finance_models.Bill.objects.get(id=int(obj.bill))
            data = generics_utils.model_to_dict(bill_obj)
            return finance_utils.clean_bill_details(data)
        return {"cleared_status": "CLEARED"}

    def create(self, validated_data):
        try:
            with transaction.atomic():
                payment_scheme = validated_data.pop("payment_scheme", None)
                if payment_scheme:
                    payment_scheme = finance_models.PayerScheme.objects.get(
                        id=payment_scheme
                    )

                encounter = models.Encounter(**validated_data)
                clinic = models.Clinic.objects.get(id=encounter.clinic.get("id"))
                encounter._payment_scheme = payment_scheme
                encounter._bill_item_code = clinic.bill_item_code
                encounter._quantity = 1
                encounter._name = clinic.name

                user = generics_utils.trim_user_data(
                    generics_utils.model_to_dict(self.context["request"].user)
                )
                audit_log = generics_utils.AuditLog(
                    user=user, event=generics_utils.AuditEvent.CREATE, fields={}
                ).dict()
                encounter.audit_log = [
                    audit_log,
                ]
                encounter.save()
                return encounter
        except Exception as e:
            raise serializers.ValidationError(detail=str(e), code=400)

    def update(self, instance: models.Encounter, validated_data: dict):
        with transaction.atomic():
            audit_log = {}
            if validated_data.get("status"):
                user = self.context["request"].user
                status = validated_data.get("status")
                if not enc_utils.has_encounter_status_perm(user, status):
                    raise PermissionDenied(
                        "You do not have permission to change this status"
                    )
                audit_log = generics_utils.AuditLog(
                    user=generics_utils.trim_user_data(
                        generics_utils.model_to_dict(user)
                    ),
                    event=generics_utils.AuditEvent.UPDATE,
                    fields=validated_data,
                ).dict()
            instance = super().update(instance, validated_data)
            if audit_log:
                instance.audit_log.append(audit_log)
                instance.save()
            return instance


class EncounterSignSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128, required=True)

    def validate_password(self, value):
        user: User = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Invalid password", code=401)
        return value


class EncounterObservationSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False)
    value = generic_serializers.DictCharSerializerField()
    created_at = serializers.DateTimeField()
    created_by = serializers.DictField()

    def to_representation(self, instance):
        if not instance:
            return None
        instance["created_at"] = datetime.fromisoformat(instance["created_at"])
        return instance


class EncounterObservationRequestSerializer(serializers.Serializer):
    value = generic_serializers.DictCharSerializerField()


class EncounterOrdersSerializer(serializers.Serializer):
    laboratory = lab_serializers.LabOrderSerializer(required=False, allow_null=True)
    imaging = img_serializers.ImagingOrderSerializer(required=False, allow_null=True)
    prescription = pharm_serializers.PrescriptionSerializer(
        required=False, allow_null=True
    )


class EncounterChartValueSerializer(serializers.Serializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    content = serializers.ListField(required=True)
    orders = EncounterOrdersSerializer()
    diagnosis = DiagnosisValueSerializer(many=True, allow_null=True, allow_empty=True)
    is_active = serializers.BooleanField(default=False)


class EncounterChartSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False)
    chart = serializers.DictField(required=True)
    created_at = serializers.DateTimeField()
    created_by = serializers.DictField()

    def to_representation(self, instance):
        if not instance:
            return None
        if type(instance["created_at"]) is str:
            instance["created_at"] = datetime.fromisoformat(instance["created_at"])
        return instance
