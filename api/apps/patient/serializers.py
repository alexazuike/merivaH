from functools import reduce
from enum import Enum
from typing import List
import json
import io

from rest_framework import serializers
from django.utils import timezone
from django.core.files.uploadedfile import InMemoryUploadedFile

from api.includes import file_utils, utils
from api.apps.finance import models as finance_models
from api.apps.finance import utils as finance_utils
from api.includes import exceptions
from .models import Patient, PatientFile

MAX_PATIENT_FILE_SIZE: int = 20_000_000


class PatientSchemeRelEnum(str, Enum):
    """Enum for patient scheme relationship"""

    PRINCIPAL = "PRINCIPAL"
    DEPENDANT = "DEPENDANT"

    def __str__(self):
        return self.value

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class PatientPaymentSchemeSerializer(serializers.Serializer):
    payer_scheme = serializers.DictField(required=True)
    enrollee_id = serializers.CharField(max_length=256, required=False, allow_null=True)
    relationship = serializers.ChoiceField(
        required=False, choices=PatientSchemeRelEnum.choices(), allow_null=True
    )
    exp_date = serializers.DateField(required=False, allow_null=True)

    def validate_payer_scheme(self, value):
        if not value.get("id"):
            raise exceptions.BadRequest("Payer scheme id is required")
        payer_scheme = finance_models.PayerScheme.objects.filter(id=value.get("id"))
        if not payer_scheme.exists():
            raise exceptions.BadRequest("Payer scheme does not exist")
        return {
            "id": value.get("id"),
            "name": payer_scheme.first().name,
            "type": payer_scheme.first().type,
        }

    def validate_exp_date(self, value):
        if value and value < timezone.now().date():
            raise exceptions.BadRequest("Expiry date cannot be in the past")
        return value if value is None else str(value)


class PatientSerializer(serializers.ModelSerializer):
    payment_scheme = serializers.ListField(
        required=False,
        child=PatientPaymentSchemeSerializer(),
        allow_empty=True,
    )

    class Meta:
        model = Patient
        fields = "__all__"
        read_only_fields = ("deposit", "reserve")

    def validate_payment_scheme(self, value):
        if not value or value is None:
            return []
        return value


class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    payment_method = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=finance_models.PaymentMethod.objects.all(),
    )


class PatientDepositSerializer(serializers.Serializer):
    deposit = serializers.ListField(child=DepositSerializer(), required=True)

    def validate(self, data):
        deposits = data.get("deposit")
        for deposit in deposits:
            if deposit["payment_method"].name.casefold() == "reserve".casefold():
                raise exceptions.BadRequest("Reserve payment method is not allowed")
            if deposit["payment_method"].name.casefold() == "deposit".casefold():
                raise exceptions.BadRequest("Deposit payment method is not allowed")
        return data

    def save(self, patient: Patient) -> finance_models.PaymentSummary:
        payments = self.validated_data.get("deposit")
        payments_parsed: List[finance_models.PaymentMethodStruct] = [
            finance_models.PaymentMethodStruct(
                amount=payment["amount"],
                payment_method=utils.model_to_dict(payment["payment_method"]),
            )
            for payment in payments
        ]
        total_amount = reduce(lambda x, y: x + y, [d.get("amount") for d in payments])
        patient.add_deposit(total_amount)
        user_details = utils.trim_user_data(utils.model_to_dict(self.context["user"]))
        patient_details = PatientSerializer(patient).data
        finance_utils.add_payments(
            patient_dict=patient_details,
            payment_details=payments_parsed,
            user_details=user_details,
            bills=[],
            payment_type=finance_models.PaymentType.DEPOSIT,
        )
        payment_response = finance_models.PaymentSummary(
            patient=patient_details,
            bills=[],
            payments=payments_parsed,
            total_amount=total_amount,
            user=user_details,
            invoice=None,
        )
        return payment_response


class PatientDepositResponseSerializer(serializers.Serializer):
    patient = PatientSerializer()
    payment_details = serializers.ListField(child=DepositSerializer(), required=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    created_at = serializers.DateTimeField(default=timezone.now())

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data = json.loads(json.dumps(data))
        payment_details = data["payment_details"]
        for value in payment_details:
            value["payment_method"] = utils.model_to_dict(
                finance_models.PaymentMethod.objects.get(id=value["payment_method"])
            )
        data["payment_details"] = payment_details
        return data


class PatientFileSerializer(serializers.ModelSerializer):
    file = serializers.FileField(
        max_length=256, write_only=True, allow_empty_file=False
    )

    class Meta:
        model = PatientFile
        fields = "__all__"
        read_only_fields = ("created_by", "updated_by", "path")

    def create(self, validated_data):
        file_upload: InMemoryUploadedFile = validated_data.get("file")
        document_type = validated_data.get("document_type")
        if document_type:
            document_type = document_type.name
        patient: Patient = validated_data.get("patient")
        title: str = validated_data.get("title")
        user = self.context["request"].user
        user_data = utils.trim_user_data(utils.model_to_dict(user))

        if file_upload.size > MAX_PATIENT_FILE_SIZE:
            raise exceptions.BadRequest("File cannot be larger than 20mb")

        file_content: io.BytesIO = file_upload.read()
        saved_file_path = file_utils.FileUtils().upload_static_file(
            file_utils.StaticFolderType.PATIENT,
            str(patient.id),
            file_upload.name,
            file_content,
            document_type=document_type,
        )

        patient_file_obj = PatientFile.objects.create(
            title=title, patient=patient, path=saved_file_path, created_by=user_data
        )
        return patient_file_obj

    def update(self, instance: PatientFile, validated_data: dict):
        file_upload: InMemoryUploadedFile = validated_data.get("file")
        user = self.context["request"].user
        user_data = utils.trim_user_data(utils.model_to_dict(user))

        # remove former file
        if file_upload:
            file_utils.FileUtils().remove_static_file(instance.path)

            # upload new file
            file_content: io.BytesIO = file_upload.read()
            new_file_path = file_utils.FileUtils().upload_static_file(
                file_utils.StaticFolderType.PATIENT,
                instance.patient.id,
                file_upload.name,
                file_content,
            )
            instance.path = new_file_path
        instance.title = validated_data.get("title", instance.title)
        instance.updated_by = user_data
        instance.save()
        return instance
