from typing import List, Union
from rest_framework import serializers
from django.db import transaction
from django.apps import apps

from api.apps.users.serializers import UserSerializer
from api.apps.patient import models as patient_models
from api.apps.finance.libs import invoice as invoice_lib
from api.config import exceptions
from api.utils import lib
from . import utils
from . import models
from .libs.billing import Billing as BillingLib


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

    class Meta:
        model = models.PayerScheme
        fields = "__all__"
        read_onlY_fields = ("created_at", "updated_at", "created_by", "updated_by")

    def create(self, validated_data):
        user = self.context["request"].user
        user_data = UserSerializer(user).data
        user_data = lib.trim_user_data(user_data)
        validated_data["created_by"] = user_data
        return super(PayerSchemeSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        user_data = UserSerializer(user).data
        user_data = lib.trim_user_data(user_data)
        validated_data["updated_by"] = user_data
        return super(PayerSchemeSerializer, self).update(instance, validated_data)


class PayerSchemeResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PayerScheme
        fields = "__all__"
        depth = 1


class BillableItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BillableItem
        fields = "__all__"
        read_only_fields = (
            "item_code",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )

    def create(self, validated_data):
        user = self.context["request"].user
        user_data = UserSerializer(user).data
        user_data = lib.trim_user_data(user_data)
        validated_data["created_by"] = user_data
        return super(BillableItemSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        user_data = UserSerializer(user).data
        user_data = lib.trim_user_data(user_data)

        instance.item_code = validated_data.get("item_code", instance.item_code)
        instance.cost = validated_data.get("cost", instance.cost)
        instance.selling_price = validated_data.get(
            "selling_price", instance.selling_price
        )
        instance.description = validated_data.get("description", instance.description)
        instance.module = validated_data.get("module", instance.module)
        instance.updated_by = user_data
        instance.save()
        return instance


class CoPaySerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=models.CoPayValueType.choices(), required=True
    )
    value = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)


class PriceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PriceList
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "created_by", "updated_by")

    def create(self, validated_data):
        user = self.context["request"].user
        user_data = UserSerializer(user).data
        user_data = lib.trim_user_data(user_data)
        validated_data["created_by"] = user_data
        price_list = models.PriceList.objects.create(**validated_data)
        return price_list

    def update(self, instance, validated_data):
        user = self.context["request"].user
        user_data = UserSerializer(user).data
        user_data = lib.trim_user_data(user_data)
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.updated_by = user_data
        instance.save()
        return instance


class PriceListItemSerializer(serializers.ModelSerializer):
    co_pay = CoPaySerializer(required=False)
    name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.PriceListItem
        fields = "__all__"
        read_only_fields = (
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "name",
        )

    def get_name(self, obj):
        try:
            billable_item = models.BillableItem.objects.get(
                item_code=obj.bill_item_code
            )
            return billable_item.description
        except models.BillableItem.DoesNotExist:
            return None

    def validate_price_list(self, value):
        if not models.PriceList.objects.filter(name=value).exists():
            raise serializers.ValidationError("Price list does not exist", 400)
        return value

    def validate(self, data):
        bill_item_code = data.get("bill_item_code")
        module = data.get("module")

        if not models.BillableItem.objects.filter(
            item_code=bill_item_code, module=module
        ).exists():
            raise serializers.ValidationError(
                "Billable item code does not exist for selected module", 400
            )
        return data

    def create(self, validated_data):
        user = self.context.get("request").user
        user_data = UserSerializer(user).data
        user_data = lib.trim_user_data(user_data)
        validated_data["created_by"] = user_data
        return super(PriceListItemSerializer, self).create(validated_data)

    def update(self, instance: models.PriceListItem, validated_data: dict):
        user = self.context.get("request").user
        user_data = UserSerializer(user).data
        user_data = lib.trim_user_data(user_data)
        validated_data["updated_by"] = user_data

        instance.selling_price = validated_data.get(
            "selling_price", instance.selling_price
        )
        instance.co_pay = validated_data.get("co_pay", instance.co_pay)
        instance.is_auth_req = validated_data.get("is_auth_req", instance.is_auth_req)
        instance.is_capitated = validated_data.get(
            "is_capitated", instance.is_capitated
        )
        instance.is_exclusive = validated_data.get(
            "is_exclusive", instance.is_exclusive
        )
        instance.post_auth_allowed = validated_data.get(
            "post_auth_allowed", instance.post_auth_allowed
        )
        instance.save()
        return instance


class PriceListItemUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)


class SinglePriceListDetailSerializer(serializers.Serializer):
    bill_item_code = serializers.CharField(required=True)
    selling_price = serializers.DecimalField(
        required=True, max_digits=10, decimal_places=2
    )
    co_pay = serializers.CharField(required=False)
    is_auth_req = serializers.BooleanField(required=False, default=False)
    is_capitated = serializers.BooleanField(required=False, default=False)
    module = serializers.ChoiceField(required=True, choices=lib.Modules.choices())
    is_exclusive = serializers.BooleanField(required=False, default=False)
    post_auth_allowed = serializers.BooleanField(required=False, default=False)


class PriceListItemBulkSerializer(serializers.Serializer):
    items = serializers.ListField(
        child=SinglePriceListDetailSerializer(), required=True
    )


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
    bills = serializers.ListField(
        child=serializers.IntegerField(), required=True, allow_empty=False
    )

    class Meta:
        model = models.Payment
        fields = "__all__"
        read_only_fields = (("audit_log",),)

    def validate(self, data):
        patient: dict = data.get("patient")
        bills: list = data.get("bills")

        try:
            bill_objects: list = [utils.get_uncleared_bill_object(id) for id in bills]
            total_bill_price = sum([bill.selling_price for bill in bill_objects])

            # validate total amount paid
            if data.get("total_amount") < total_bill_price:
                raise serializers.ValidationError(
                    f"total bill price {total_bill_price} is less than total amount",
                    400,
                )

            # validate patient and bills
            for bill in bill_objects:
                if bill.patient.get("id") != patient.get("id"):
                    raise serializers.ValidationError(
                        f"patient id {bill.patient.get('id')} does not match with patient id {patient.get('id')}",
                        400,
                    )
            return data
        except Exception as e:
            raise serializers.ValidationError(str(e), 400)

    def create(self, validated_data):
        with transaction.atomic():
            payment = super(PaymentSerializer, self).create(validated_data)

            # add audit log
            validated_data["total_amount"] = str(validated_data["total_amount"])
            user = self.context["request"].user
            user_data = UserSerializer(user).data
            user_data = lib.trim_user_data(user_data)
            audit_log = lib.AuditLog(
                user=user_data, event=lib.AuditEvent.CREATE, fields=validated_data
            ).dict()
            payment.audit_log.append(audit_log)
            payment.save()

            # clear bills
            bill_objects: list = [
                utils.get_uncleared_bill_object(id)
                for id in validated_data.get("bills")
            ]

            for bill in bill_objects:
                utils.clear_bill(bill)
            return payment


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Bill
        fields = "__all__"
        read_only_fields = ("transaction_date", "patient")


class BillResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Bill
        fields = "__all__"
        read_only_fields = ("transaction_date", "patient")
        depth = 1


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

    def validate(self, data):
        patient: dict = data.get("patient")
        bills: List[models.Bill] = data.get("bills")
        payments: list = data.get("payments")

        # validate patient and bills
        for bill in bills:
            if bill.patient.get("id") != patient.id:
                raise serializers.ValidationError(
                    f"bill {bill.id} is not created for patient {patient.id}",
                    400,
                )
            if str(bill.billed_to_type) != str(models.PayerSchemeType.SELF):
                raise serializers.ValidationError(
                    f"bill {bill.id} is billed to insurace. Cannot pay for insurance bills",
                    400,
                )
            if bill.is_invoiced:
                raise serializers.ValidationError(
                    f"bill {bill.id} is already invoiced", 400
                )

        # validate payments
        total_bills_price = sum(
            [bill.selling_price for bill in bills if not bill.is_reserved]
        )
        total_payments_amount = sum([payment["amount"] for payment in payments])
        if total_bills_price != total_payments_amount:
            raise serializers.ValidationError(
                f"total bills price: {total_bills_price} is not equal to total paid amount: {total_payments_amount}",
                400,
            )
        return data

    def save(self) -> models.Invoice:
        with transaction.atomic():
            payments = self.validated_data.pop("payments")
            bills = self.validated_data.pop("bills")
            patient = self.validated_data.pop("patient")

            user = self.context["request"].user
            user_data = lib.trim_user_data(UserSerializer(user).data)
            payments = [dict(payment) for payment in payments]
            payments_parsed: List[models.PaymentMethodStruct] = [
                models.PaymentMethodStruct(**payment) for payment in payments
            ]

            invoice_util = invoice_lib.Invoice(
                patient=patient,
                user_data=user_data,
                scheme_type=str(models.PayerSchemeType.SELF),
                **self.validated_data,
            )
            invoice_created: models.Invoice = invoice_util.create_invoice(bills=bills)
            invoice_util.invoice = invoice_created
            invoice_obj = invoice_util.add_payments(payments_parsed)
            return invoice_obj


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
        user_data = lib.model_to_dict(self.context["request"].user)

        if str(bill.patient.get("id")) != str(patient.id):
            raise exceptions.BadRequest("Patient does not own the bill")

        billing_lib = BillingLib(
            bill_item_code=self.bill_item_code,
            quantity=self.quantity,
            module_name=self.bill_source,
            patient=lib.model_to_dict(self.patient),
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
            == str(models.PayerSchemeType.SELF).casefold()
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
                payer_scheme = lib.model_to_dict(payer_scheme)
            user = self.context["request"].user
            user_data = lib.trim_user_data(UserSerializer(user).data)

            invoice_util = invoice_lib.Invoice(
                created_by=user_data,
                patient=patient,
                user_data=user_data,
                payer_scheme=payer_scheme,
                scheme_type=scheme_type**validated_data,
            )
            invoice_created: models.Invoice = invoice_util.create_invoice(bills=bills)
            return invoice_created


class InvoiceResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Invoice
        fields = "__all__"
        depth = 1


class InvoicePaymentListSerializer(serializers.Serializer):
    payments = serializers.ListField(child=MakePaymentSerializer(), required=True)

    def save(self, invoice_obj: models.Invoice, user_data: dict):
        with transaction.atomic():
            payments = self.validated_data.get("payments")
            payments = [dict(payment) for payment in payments]
            patient = patient_models.Patient.objects.get(
                id=invoice_obj.patient.get("id")
            )

            payments_parsed: List[models.PaymentMethodStruct] = [
                models.PaymentMethodStruct(**payment) for payment in payments
            ]

            invoice_utils = invoice_lib.Invoice(
                invoice=invoice_obj,
                patient=patient,
                user_data=user_data,
            )
            invoice_obj = invoice_utils.add_payments(payments_parsed)
            return invoice_obj


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
        user_data = lib.trim_user_data(
            UserSerializer(instance=self.context["request"].user)
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
        user_data = lib.trim_user_data(
            UserSerializer(instance=self.context["request"].user)
        )
        bills_data: List[models.Bill] = self.validated_data.get("bills")
        invoice_utils = invoice_lib.Invoice(
            invoice=invoice_obj,
            patient=patient,
            user_data=user_data,
        )
        invoice_obj = invoice_utils.remove_bills(bills_data)
        return invoice_obj
