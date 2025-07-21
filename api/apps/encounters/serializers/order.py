from datetime import datetime
from django.db import transaction
from rest_framework import serializers
from rest_framework.request import Request

from .. import models
from ..libs.encounter_orders_factory import EncounterServicesOrderFactory
from api.includes import serializers as generic_serializers
from api.apps.laboratory import serializers as lab_serializers
from api.apps.imaging import serializers as img_serializers
from api.apps.pharmacy import serializers as pharm_serializers
from api.apps.nursing import serializers as nursing_serializers


class OrderItemSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False)
    type = serializers.ChoiceField(choices=models.EncounterOrderChoices.choices)
    value = generic_serializers.DictCharSerializerField()
    created_at = serializers.DateTimeField()
    created_by = serializers.DictField()

    def to_representation(self, instance):
        if not instance:
            return None
        instance["created_at"] = datetime.fromisoformat(instance["created_at"])
        return instance


class EncounterServicesOrderSerializer(serializers.Serializer):
    laboratory = lab_serializers.LabOrderSerializer(allow_null=True)
    imaging = img_serializers.ImagingOrderSerializer(allow_null=True)
    prescription = pharm_serializers.PrescriptionSerializer(allow_null=True)
    nursing = nursing_serializers.NursingOrderSerializer(allow_null=True)

    def save(self, encounter: models.Encounter, request: Request):
        with transaction.atomic():
            lab_order: lab_serializers.LabOrderSerializer = self.validated_data.get(
                "laboratory"
            )
            img_order: img_serializers.ImagingOrderSerializer = self.validated_data.get(
                "imaging"
            )
            presc_order: pharm_serializers.PrescriptionSerializer = (
                self.validated_data.get("prescription")
            )
            nursing_order: nursing_serializers.NursingOrderSerializer(
                self.validated_data.get("nursing")
            )
            enc_factory = EncounterServicesOrderFactory(
                encounter=encounter,
                request=request,
                lab_order_data=lab_order,
                img_order_data=img_order,
                presc_order_data=presc_order,
                nursing_order_data=nursing_order,
            )
            orders = enc_factory.order_services()
            return orders
