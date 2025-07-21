from typing import Union, List

from rest_framework import serializers
from django.db import models, transaction
from django.apps import apps

from api.apps.finance import models
from api.apps.finance.libs import invoice as invoice_lib
from api.apps.patient import models as patient_models
from api.includes import utils


class InvoiceSerializer(serializers.ModelSerializer):
    bills = serializers.PrimaryKeyRelatedField(
        many=True, queryset=models.Bill.objects.all(), write_only=True, required=True
    )
    payer_scheme = serializers.PrimaryKeyRelatedField(
        queryset=models.PayerScheme.objects.all(), required=False
    )

    patient = serializers.PrimaryKeyRelatedField(
        queryset=patient_models.Patient.objects.all(), required=True
    )

    class Meta:
        model = models.Invoice
        fields = "__all__"
        read_only_fields = (
            "inv_id",
            "invoice_lines",
            "total_charge",
            "paid_amount",
            "balance",
            "status",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "confirmed_by",
            "confirmed_at",
        )

    def validate(self, data: dict):
        encounter_id = data.get("encounter")
        encounter_model = apps.get_model("encounters", "Encounter")
        payer_scheme = data.get("payer_scheme")
        scheme_type = (
            str(models.PayerSchemeType.SELF)
            if not payer_scheme
            else str(payer_scheme.type)
        )
        bills = data.get("bills")

        # validate bills and payer_scheme matches
        for bill in bills:
            if str(bill.billed_to_type) != scheme_type:
                raise serializers.ValidationError(
                    f"Expected {scheme_type} for bill {bill.id}, but got {bill.billed_to_type}",
                    400,
                )
            if bill.billed_to != payer_scheme:
                raise serializers.ValidationError(
                    f"bill {bill.id} does not match required payer scheme type "
                )

        # validate encounters
        if not encounter_model.objects.filter(id=encounter_id).exists():
            raise serializers.ValidationError("Encounter does not exist", 400)
        return data

    def create(self, validated_data: dict):
        with transaction.atomic():
            bills = validated_data.pop("bills")
            patient = validated_data.pop("patient")
            payer_scheme: Union[models.PayerScheme, None] = validated_data.pop(
                "payer_scheme", None
            )
            scheme_type = str(models.PayerSchemeType.SELF)
            if payer_scheme:
                scheme_type = str(payer_scheme.type)
                payer_scheme = utils.model_to_dict(payer_scheme)
            user = self.context["request"].user
            user_data = utils.trim_user_data(utils.model_to_dict(user))

            invoice_util = invoice_lib.Invoice(
                created_by=user_data,
                patient=patient,
                user_data=user_data,
                payer_scheme=payer_scheme,
                scheme_type=scheme_type,
                **validated_data,
            )
            invoice_created: models.Invoice = invoice_util.create_invoice(bills=bills)
            return invoice_created


class InvoiceResponseSerializer(serializers.ModelSerializer):
    reserved_amount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Invoice
        fields = "__all__"
        depth = 1

    def get_reserved_amount(self, obj: models.Invoice):
        reserved_bills_amount = sum(
            [
                float(bill["selling_price"])
                for bill in obj.bill_lines
                if bill.get("is_reserved")
            ]
        )
        return reserved_bills_amount


class InvoiceBillsSerializer(serializers.Serializer):
    bills = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=models.Bill.objects.all(), required=True, allow_empty=False
        )
    )

    def add_bills(self, invoice_obj: models.Invoice):
        patient: patient_models.Patient = patient_models.Patient.objects.get(
            id=invoice_obj.patient.get("id")
        )
        user_data = utils.trim_user_data(
            utils.model_to_dict(instance=self.context["request"].user)
        )
        bills_data: List[models.Bill] = self.validated_data.get("bills")
        invoice_utils = invoice_lib.Invoice(
            invoice=invoice_obj,
            patient=patient,
            user_data=user_data,
        )
        invoice_obj = invoice_utils.add_bills(bills_data)
        return invoice_obj

    def remove_bills(self, invoice_obj: models.Invoice):
        patient: patient_models.Patient = patient_models.Patient.objects.get(
            id=invoice_obj.patient.get("id")
        )
        user_data = utils.trim_user_data(
            utils.model_to_dict(instance=self.context["request"].user)
        )
        bills_data: List[models.Bill] = self.validated_data.get("bills")
        invoice_utils = invoice_lib.Invoice(
            invoice=invoice_obj,
            patient=patient,
            user_data=user_data,
        )
        invoice_obj = invoice_utils.remove_bills(bills_data)
        return invoice_obj
