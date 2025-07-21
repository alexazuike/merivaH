from decimal import Decimal
from typing import List, Dict

from rest_framework import serializers
from django.db import transaction
from django.utils import timezone

from api.apps.finance import models
from api.apps.finance import utils as fin_utils
from api.apps.finance.libs import invoice as invoice_lib
from api.apps.finance.libs.reports.payments_report import PaymentDetailReportGenerator
from api.apps.patient import models as patient_models
from api.includes import utils as generic_utils
from api.includes import exceptions


class CashbookSerializer(serializers.Serializer):
    class Meta:
        model = models.CashBook
        fields = "__all__"


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PaymentMethod
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class MakePaymentSerializer(serializers.Serializer):
    payment_method = serializers.PrimaryKeyRelatedField(
        queryset=models.PaymentMethod.objects.all(), required=True
    )
    amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)

    def validate_payment_method(self, value: models.PaymentMethod):
        if value:
            if (value.name.casefold() == "reserve".casefold()) or (
                value.name.casefold() == "refund".casefold()
            ):
                raise serializers.ValidationError(
                    "Reserve payment method is not allowed"
                )
        return value


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Payment
        fields = "__all__"
        read_only_fields = ("audit_log", "created_by")

    def create(self, validated_data: dict):
        validated_data["created_by"] = generic_utils.trim_user_data(
            generic_utils.model_to_dict(self.context["request"].user)
        )
        return super().create(validated_data)


class PaymentSummarySerializer(serializers.Serializer):
    patient = serializers.DictField(required=True)
    bills = serializers.ListField(
        required=False, child=serializers.DictField(), allow_null=True
    )
    payments = serializers.ListField(required=False, child=serializers.DictField())
    total_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=True
    )
    invoice = serializers.DictField(required=False, allow_null=True)
    user = serializers.DictField(required=True, allow_null=False)
    created_at = serializers.DateTimeField(required=False, default=timezone.now())


class BillsPaymentSerializer(serializers.Serializer):
    payments = serializers.ListField(child=MakePaymentSerializer(), required=True)
    bills = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=models.Bill.objects.all(), required=True, allow_empty=False
        )
    )
    patient = serializers.PrimaryKeyRelatedField(
        queryset=patient_models.Patient.objects.all(), required=True
    )

    def __validate_deposit_payment_method(
        self, patient: patient_models.Patient, payments: List[dict]
    ):
        # get all deposit payment method
        total_deposit_amount: float = sum(
            [
                payment["amount"]
                for payment in payments
                if str(payment["payment_method"].name).casefold()
                == "deposit".casefold()
            ]
        )
        if total_deposit_amount > patient.deposit:
            raise serializers.ValidationError(
                "total deposit payment method amount is greater than patient deposit balance"
            )

    def __validate_patient_bills(
        self, patient: patient_models.Patient, bills: List[models.Bill]
    ):
        for bill in bills:
            if bill.patient.get("id") != patient.id:
                raise serializers.ValidationError(
                    f"bill {bill.id} is not created for patient {patient.id}",
                    400,
                )
            if bill.cleared_status == models.BillStatus.CLEARED:
                raise serializers.ValidationError(f"bill {bill.id} is already cleared")
            if str(bill.billed_to_type) not in (
                str(models.PayerSchemeType.SELF_PREPAID),
                str(models.PayerSchemeType.SELF_POSTPAID),
            ):
                raise serializers.ValidationError(
                    f"bill {bill.id} is billed to insurace. Cannot pay for insurance or corporate bills",
                    400,
                )
            if bill.is_invoiced:
                raise serializers.ValidationError(
                    f"bill {bill.id} is already invoiced", 400
                )

    def __validate_payment_not_less_than_bills_amount(
        self, bills: List[models.Bill], payments: List[dict]
    ):
        total_bills_price = sum(
            [bill.selling_price for bill in bills if not bill.is_reserved]
        )
        total_payments_amount = sum([payment["amount"] for payment in payments])
        if total_bills_price != total_payments_amount:
            raise serializers.ValidationError(
                f"total bills price: {total_bills_price} is not equal to total paid amount: {total_payments_amount}",
                400,
            )

    def validate(self, data):
        patient: dict = data.get("patient")
        bills: List[models.Bill] = data.get("bills")
        payments: list = data.get("payments")

        # check validations
        self.__validate_patient_bills(patient=patient, bills=bills)
        self.__validate_deposit_payment_method(patient=patient, payments=payments)
        self.__validate_payment_not_less_than_bills_amount(
            bills=bills, payments=payments
        )
        return data

    def save(self) -> models.PaymentSummary:
        with transaction.atomic():
            payments = self.validated_data.pop("payments")
            bills: List[models.Bill] = self.validated_data.pop("bills")
            patient: patient_models.Patient = self.validated_data.pop("patient")

            total_payments_amount = sum([payment["amount"] for payment in payments])
            total_deposit_amount: float = sum(
                [
                    payment["amount"]
                    for payment in payments
                    if str(payment["payment_method"].name).casefold()
                    == "deposit".casefold()
                ]
            )
            total_viable_amount = float(total_payments_amount) - float(
                total_deposit_amount
            )
            bills_data = [
                generic_utils.model_to_dict(
                    instance=bill, exclude_fields={"invoice", "patient"}
                )
                for bill in bills
            ]
            patient_dict = generic_utils.model_to_dict(patient)
            user = self.context["request"].user
            user_data = generic_utils.trim_user_data(generic_utils.model_to_dict(user))
            payments = [dict(payment) for payment in payments]
            payments_parsed: List[models.PaymentMethodStruct] = [
                models.PaymentMethodStruct(
                    amount=payment["amount"],
                    payment_method=generic_utils.model_to_dict(
                        payment["payment_method"]
                    ),
                )
                for payment in payments
            ]
            fin_utils.add_payments(
                patient_dict=patient_dict,
                payment_details=payments_parsed,
                user_details=user_data,
                bills=bills_data,
                payment_type=models.PaymentType.DEPOSIT,
            )
            patient.add_deposit(Decimal(total_viable_amount))
            [bill.reserve() for bill in bills]  # reserve bills
            payment_summary = models.PaymentSummary(
                patient=patient_dict,
                bills=bills_data,
                payments=payments_parsed,
                total_amount=float(total_payments_amount),
                user=user_data,
                invoice=None,
            )
            return payment_summary


class InvoicePaymentSerializer(serializers.Serializer):
    payments = serializers.ListField(child=MakePaymentSerializer(), required=True)
    patient = patient = serializers.PrimaryKeyRelatedField(
        queryset=patient_models.Patient.objects.all(), required=True
    )

    def __validate_deposit_payment_method(
        self, patient: patient_models.Patient, payments: List[dict]
    ):
        # get all deposit payment method
        total_deposit_amount: float = sum(
            [
                payment["amount"]
                for payment in payments
                if str(payment["payment_method"].name).casefold()
                == "deposit".casefold()
            ]
        )
        if total_deposit_amount > patient.deposit:
            raise serializers.ValidationError(
                "total deposit payment method amount is greater than patient deposit balance"
            )

    def __validate_not_more_than_balance(
        self, invoice: models.Invoice, payments: List[dict]
    ):
        total_amount: float = float(sum([payment["amount"] for payment in payments]))
        if total_amount > float(invoice.balance):
            raise serializers.ValidationError(
                "total amount is greater than balance left"
            )

    def validate(self, data):
        patient: dict = data.get("patient")
        payments: list = data.get("payments")

        # check validations
        self.__validate_deposit_payment_method(patient=patient, payments=payments)
        return data

    def save(self, invoice_obj: models.Invoice, user_data: dict):
        with transaction.atomic():
            if invoice_obj.status == models.InvoiceStatus.DRAFT:
                raise exceptions.BadRequest(
                    "Cannot pay for invoice in draft. Invoice must be confirmed"
                )
            if invoice_obj.status == models.InvoiceStatus.PAID:
                raise exceptions.BadRequest(
                    "Cannot pay for invoice. Invoice is already fully paid"
                )

            payments = self.validated_data.get("payments")
            payments = [dict(payment) for payment in payments]
            patient = patient_models.Patient.objects.get(
                id=invoice_obj.patient.get("id")
            )

            payments_parsed: List[models.PaymentMethodStruct] = [
                models.PaymentMethodStruct(
                    amount=payment["amount"],
                    payment_method=generic_utils.model_to_dict(
                        payment["payment_method"]
                    ),
                )
                for payment in payments
            ]
            self.__validate_not_more_than_balance(invoice_obj, payments)
            invoice_utils = invoice_lib.Invoice(
                invoice=invoice_obj,
                patient=patient,
                user_data=user_data,
            )
            invoice_obj = invoice_utils.add_payments(payments_parsed)
            return invoice_obj


class PaymentSummaryReportsSerializer(serializers.Serializer):
    payment_method = serializers.CharField(required=True)
    total_amount = serializers.DecimalField(max_digits=125, decimal_places=2)
    cashier = serializers.CharField(required=True, allow_blank=True)


class PaymentDetailedReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Payment
        fields = "__all__"

    def to_representation(self, instance):
        report_struct = PaymentDetailReportGenerator.initialize(instance)
        return report_struct.to_response_struct()
