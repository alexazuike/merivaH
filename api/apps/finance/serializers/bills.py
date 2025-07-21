import uuid
from rest_framework import serializers

from api.apps.finance import models
from api.apps.finance.libs.billing import Billing as BillingLib
from api.apps.patient import models as patient_models
from api.includes import exceptions
from api.includes import utils


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Bill
        fields = "__all__"
        read_only_fields = (
            "transaction_date",
            "patient",
            "updated_by",
            "is_invoiced",
            "is_service_rendered",
            "is_invoiced",
            "is_capitated",
            "is_reserved",
            "is_auth_req",
            "post_auth_allowed",
            "invoice",
            "billed_to",
            "co_pay",
        )


class SummaryBillSerializer(serializers.Serializer):
    _id = serializers.UUIDField(required=False, default=uuid.uuid4)
    bill_source = serializers.CharField(allow_null=False, allow_blank=False)
    billed_to_type = serializers.CharField(allow_null=False, allow_blank=False)
    cleared_status = serializers.ChoiceField(
        default="CLEARED", choices=models.BillStatus.choices()
    )
    cost_price = serializers.DecimalField(max_digits=11, decimal_places=2, default=0.00)
    selling_price = serializers.DecimalField(max_digits=11, decimal_places=2)
    quantity = serializers.IntegerField(required=True)
    bill_item_code = serializers.CharField(
        required=False, allow_null=True, default=None
    )
    transaction_date = serializers.DateTimeField(required=False)
    description = serializers.CharField(
        required=True, allow_null=False, allow_blank=False
    )

    def validate_bill_source(self, value):
        if not utils.Modules.get_module(value) and not utils.Modules.get_module_value(
            value
        ):
            raise exceptions.BadRequest("Invalid bill source")
        return value

    def validate_billed_to_type(self, value):
        if not models.PayerSchemeType.get_scheme_type(value):
            raise exceptions.BadRequest("Invalid bill type")
        return value


class BillResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Bill
        fields = "__all__"
        read_only_fields = ("transaction_date", "patient")
        depth = 1


class BillTransferSerializer(serializers.Serializer):
    scheme_type = serializers.ChoiceField(
        choices=models.PayerSchemeType.choices(), required=True, allow_null=False
    )
    payer_scheme = serializers.PrimaryKeyRelatedField(
        queryset=models.PayerScheme.objects.all(), required=False, allow_null=True
    )
    patient = serializers.PrimaryKeyRelatedField(
        queryset=patient_models.Patient.objects.all(), required=True, allow_null=False
    )

    def save(self, bill: models.Bill) -> models.Bill:
        patient = self.validated_data.get("patient")
        payer_scheme = self.validated_data.get("payer_scheme", None)
        scheme_type = self.vaalidated_data.get("scheme_type")
        user_data = utils.model_to_dict(self.context["request"].user)

        if str(bill.patient.get("id")) != str(patient.id):
            raise exceptions.BadRequest("Patient does not own the bill")

        billing_lib = BillingLib(
            bill_item_code=self.bill_item_code,
            quantity=self.quantity,
            module_name=self.bill_source,
            patient=utils.model_to_dict(self.patient),
            description=self.description,
            billed_to=payer_scheme,
            bill=self,
        )
        bill = billing_lib.transfer(scheme_type)
        bill.updated_by = user_data
        bill.save()
        return bill


class InsuranceBillsAuthSerializer(serializers.Serializer):
    bills = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=models.Bill.objects.all(), required=True
        ),
        allow_empty=False,
    )
    auth_code = serializers.CharField(
        required=True, allow_blank=False, allow_null=False
    )

    def validate(self, data: dict):
        bills = data.get("bills")

        # get bills not for insurance
        self_bills = [
            bill
            for bill in bills
            if str(bill.billed_to_type).casefold()
            in [
                str(models.PayerSchemeType.SELF_POSTPAID).casefold(),
                str(models.PayerSchemeType.SELF_PREPAID.casefold()),
            ]
        ]

        if len(self_bills) > 0:
            raise serializers.ValidationError(
                f"Cannot authoraize bills that are billed to self"
            )

        # get bills whose auth req is false
        unauth_req_bills = [bill for bill in bills if not bill.is_auth_req]
        if len(unauth_req_bills) > 0:
            raise serializers.ValidationError(
                f"The following bills do not require authorization {[bill.id for bill in unauth_req_bills]}"
            )

        # get authorised and cleared bills
        auth_cleared_bills = [
            bill
            for bill in bills
            if bill.auth_code
            and str(bill.cleared_status).casefold()
            == str(models.BillStatus.CLEARED).casefold()
        ]
        if len(auth_cleared_bills) > 0:
            raise serializers.ValidationError(
                f"The following bills have been authorised and cleared earlier {[bill.id for bill in auth_cleared_bills]}"
            )

        return data

    def save(self):
        bills = self.validated_data.get("bills")
        auth_code = self.validated_data.get("auth_code")

        for bill in bills:
            bill.auth_code = auth_code
            bill.cleared_status = str(models.BillStatus.CLEARED)
            bill.updated_by = self.context.get("user")

        models.Bill.objects.bulk_update(
            bills, ["auth_code", "cleared_status", "updated_by"]
        )
        return bills
