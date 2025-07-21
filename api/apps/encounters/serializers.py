from datetime import datetime

from rest_framework import serializers
from django.db import transaction
from django.contrib.auth.models import User
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request

from . import models
from . import utils as enc_utils
from .libs.encounter_report_generator import EncounterReportStruct
from .libs.encounter_orders_factory import EncounterServicesFactory
from api.apps.finance import models as finance_models
from api.apps.facilities import models as facility_models
from api.apps.finance import utils as finance_utils
from api.apps.laboratory import serializers as lab_serializers
from api.apps.imaging import serializers as img_serializers
from api.apps.pharmacy import serializers as pharm_serializers
from api.includes import serializers as generic_serializers
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
        depth = 1
        read_only_fields = [
            "bill_item_code",
        ]

    def create(self, validated_data):
        bill_price = validated_data.pop("bill_price", None)
        cost_price = validated_data.pop("cost_price", None)
        user = self.context["request"].user
        user_data = generics_utils.trim_user_data(generics_utils.model_to_dict(user))

        with transaction.atomic():
            clinic: models.Clinic = models.Clinic(**validated_data)
            clinic._created_by = user_data
            clinic._bill_price = bill_price
            clinic._cost_price = cost_price
            clinic.save()
            return clinic

    def update(self, instance: models.Clinic, validated_data: dict):
        with transaction.atomic():
            bill_price = validated_data.pop("bill_price", None)
            cost_price = validated_data.pop("cost_price", None)

            with transaction.atomic():
                instance.name = validated_data.get("name", instance.name)
                instance.department = validated_data.get(
                    "department", instance.department
                )
                instance._bill_price = bill_price
                instance._cost_price = cost_price
                instance.save()
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


class ChartItemSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False)
    value = generic_serializers.DictCharSerializerField()
    created_at = serializers.DateTimeField()
    created_by = serializers.DictField()

    def to_representation(self, instance):
        if not instance:
            return None
        instance["created_at"] = datetime.fromisoformat(instance["created_at"])
        return instance


class OrdersChartSerializer(serializers.Serializer):
    laboratory = ChartItemSerializer(many=True, allow_empty=True, allow_null=True)
    imaging = serializers.ListField(
        child=ChartItemSerializer(), allow_empty=True, allow_null=True
    )
    prescription = serializers.ListField(
        child=ChartItemSerializer(), allow_empty=True, allow_null=True
    )


class EncounterChartSerializer(serializers.Serializer):
    chart = serializers.DictField(
        child=serializers.ListField(child=ChartItemSerializer())
    )


class EncounterChartDTOSerializer(serializers.Serializer):
    chart = serializers.DictField(
        child=generic_serializers.ListDictCharSerializerField()
    )


class ItemChartDTOSerializer(serializers.Serializer):
    value = generic_serializers.DictCharSerializerField()


class EncounterServicesOrder(serializers.Serializer):
    laboratory = lab_serializers.LabOrderSerializer(allow_null=True)
    imaging = img_serializers.ImagingOrderSerializer(allow_null=True)
    prescription = pharm_serializers.PrescriptionSerializer(allow_null=True)

    def save(self, encounter: models.Encounter, created_by: dict, request: Request):
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
            enc_factory = EncounterServicesFactory(
                encounter=encounter,
                request=request,
                lab_order_data=lab_order,
                img_order_data=img_order,
                presc_order_data=presc_order,
            )
            encounter = enc_factory.order_services()
            return encounter.chart["orders"]


class EncounterReportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Encounter
        fields = "__all__"
        read_only_fields = (
            "encounter_id",
            "bill",
            "acknowledged_by",
            "acknowledged_at",
        )

    def to_representation(self, instance):
        report_struct = EncounterReportStruct.initialize(instance)
        return report_struct.to_response_struct()
