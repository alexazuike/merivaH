from datetime import datetime
from enum import Enum
from typing import Union
from dataclasses import dataclass
import re
from functools import reduce

from django.db import models
from django.contrib.auth.models import User
from pydantic import BaseModel

from api.utils import lib
from api.config.app_config import AppConfig
from api.apps.patient.models import Patient
from api.config import exceptions


####################### custom id generators #########################


def generate_item_code(prefix: str):
    """
    Generates a unique item code for billable item

    Args:
        prefix: prefix for item code

    Returns:
        str: item code
    """
    CURRENT_YEAR = str(datetime.utcnow().year)
    CURRENT_MONTH = str(datetime.utcnow().month).zfill(2)
    serial_no = 1
    if lib.is_table_exist("finance_billableitem"):
        if BillableItem.objects.count() > 0:

            billable_items = BillableItem.objects.filter(
                item_code__contains=f"{CURRENT_YEAR}{CURRENT_MONTH}"
            )
            if billable_items.count() > 0:
                last_billable_item = billable_items.latest("id")
                serial_no = int(last_billable_item.item_code[-6:]) + 1

    serial_no = str(serial_no).zfill(6)
    unique_id = f"{prefix}{CURRENT_YEAR}{CURRENT_MONTH}{serial_no}"
    return unique_id


######################## Enums And Schemas ########################


class BillStatus(str, Enum):
    CLEARED = "CLEARED"
    UNCLEARED = "UNCLEARED"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

    def __str__(self):
        return self.value


class CoPayValueType(str, Enum):
    PERCENTAGE = "PERCENTAGE"
    AMOUNT = "AMOUNT"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

    def __str__(self):
        return self.value


class CoPaySchema(BaseModel):
    value: Union[int, float]
    type: CoPayValueType


class PayerSchemeType(str, Enum):
    SELF = "SELF"
    INSURANCE = "INSURANCE"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

    def __str__(self):
        return self.value


class InvoiceStatus(str, Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    PARTIAL_PAY = "PARTIAL_PAY"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

    def __str__(self):
        return self.value


class PaymentType(str, Enum):
    DEPOSIT = "DEPOSIT"
    INVOICE = "INVOICE"
    RESERVE = "RESERVE"
    REFUND = "REFUND"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

    def __str__(self):
        return self.value


class CashBookStatus(str, Enum):
    """
    Holds enum details of different cashbook status
    """

    OPEN = "OPEN"
    CLOSED = "CLOSED"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

    def __str__(self):
        return self.value


@dataclass
class PaymentMethodStruct:
    payment_method: "PaymentMethod"
    amount: float

    def dict(self):
        return {
            "payment_method": lib.model_to_dict(self.payment_method),
            "amount": self.amount,
        }


class EncounterInvoiceType(str, Enum):
    IN_PATIENT = "IN PATIENT"
    OUT_PATIENT = "OUT PATIENT"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

    def __str__(self):
        return self.value


################################ Models ###############################


class BillableItem(models.Model):
    item_code = models.CharField(max_length=256, unique=True, editable=False)
    description = models.CharField(max_length=256, blank=True, null=True)
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, default=0.0
    )
    selling_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, default=0.0
    )
    module = models.CharField(max_length=256, choices=lib.Modules.choices())
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.JSONField(default=dict)
    updated_by = models.JSONField(default=dict)

    class Meta:
        verbose_name_plural = "Billable Items"

    def __str__(self):
        return self.item_code

    def save(self, *args, **kwargs):
        if self.id is None:
            module_prefix = str(lib.Modules.get_module(self.module).value)
            self.item_code = generate_item_code(module_prefix)
        super(BillableItem, self).save(*args, **kwargs)

    def update_module_bill_details(
        self,
        bill_price: float = None,
        cost_price: float = None,
        description: str = None,
    ):
        """Function updates bill details for app module"""
        self.selling_price = bill_price or self.selling_price
        self.cost = cost_price or self.cost
        self.description = description or self.description
        self.save()


class PriceList(models.Model):
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=256, blank=True, null=True)
    created_by = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)
    meta = models.JSONField(default=dict)

    class Meta:
        verbose_name_plural = "Price Lists"

    def __str__(self):
        return self.name


class PriceListItem(models.Model):
    bill_item_code = models.CharField(max_length=256, null=False, blank=False)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_list = models.ForeignKey(PriceList, on_delete=models.CASCADE)
    co_pay = models.JSONField(default=dict)
    is_auth_req = models.BooleanField(default=False)
    is_capitated = models.BooleanField(default=False)
    module = models.CharField(max_length=256, choices=lib.Modules.choices(), null=True)
    is_exclusive = models.BooleanField(default=False)
    post_auth_allowed = models.BooleanField(default=False)
    created_by = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Price List Items"

    def __str__(self):
        return self.bill_item_code


class Payer(models.Model):
    name = models.CharField(max_length=256)
    address = models.CharField(max_length=256, blank=True, null=True)
    mobile_number = models.CharField(max_length=256, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Payers"

    def __str__(self):
        return self.name


class PayerScheme(models.Model):
    name = models.CharField(max_length=256)
    price_list = models.ForeignKey(
        PriceList,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    payer = models.ForeignKey(Payer, on_delete=models.PROTECT)
    type = models.CharField(
        max_length=256,
        choices=PayerSchemeType.choices(),
        default=PayerSchemeType.SELF.value,
    )
    created_by = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Payer Schemes"

    def __str__(self):
        return self.name


class Bill(models.Model):
    """serves a representation of all bills passing through
    the system.
    """

    bill_item_code = models.CharField(max_length=256, null=False, blank=False)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    cleared_status = models.CharField(max_length=256, choices=BillStatus.choices())
    quantity = models.IntegerField(default=1)
    bill_source = models.CharField(max_length=256, choices=lib.Modules.choices())
    billed_to_type = models.CharField(max_length=256, choices=PayerSchemeType.choices())
    billed_to = models.ForeignKey(
        PayerScheme, on_delete=models.PROTECT, blank=True, null=True
    )
    co_pay = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    service_center = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    is_service_rendered = models.BooleanField(default=False)
    serviced_rendered_at = models.DateTimeField(default=None, null=True, blank=True)
    is_invoiced = models.BooleanField(default=False)
    invoice = models.ForeignKey(
        "Invoice", on_delete=models.PROTECT, blank=True, null=True
    )
    is_capitated = models.BooleanField(default=False)
    is_reserved = models.BooleanField(default=False)
    is_auth_req = models.BooleanField(default=False)
    post_auth_allowed = models.BooleanField(default=False)
    auth_code = models.CharField(max_length=256, blank=True, null=True)
    patient = models.JSONField(default=dict)
    transaction_date = models.DateTimeField(auto_now_add=True)
    updated_by = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)
    # TODOs: add audit trail for bills

    def __str__(self):
        return self.bill_item_code

    class Meta:
        verbose_name_plural = "Bills"
        permissions = (
            ("authorize_bills", "Can authorize insurance bills"),
            ("pay_bills", "Can accept payment for bills"),
            ("transfer_bill", "Can transfer bill to different schemes"),
            ("reserve_bill", "Can reserve bill"),
            ("unreserve_bill", "Can unreserve bill"),
        )

    def unreserve(self) -> "Bill":
        """unreserve bill"""
        patient: Patient = Patient.objects.get(id=self.patient.get("id"))

        if not self.is_reserved:
            raise exceptions.BadRequest("Cannot unreserve bill that is not reserved")
        if self.is_invoiced:
            raise exceptions.BadRequest("Cannot unreserve bill that has been invoiced")
        if self.is_service_rendered:
            raise exceptions.BadRequest(
                "Cannot transfer bills whose that service has been rendered"
            )
        if (
            str(self.billed_to_type).casefold()
            == str(PayerSchemeType.INSURANCE).casefold()
        ):
            raise exceptions.BadRequest(
                "Cannot unreserve bills that are billed to Insurance"
            )

        patient.pay_from_reserve(self.selling_price)
        patient.add_deposit(self.selling_price)
        self.is_reserved = False
        self.cleared_status = str(BillStatus.UNCLEARED)
        self.save()
        return self

    def reserve(self) -> "Bill":
        """reserve bill"""
        patient: Patient = Patient.objects.get(id=self.patient.get("id"))

        if self.is_reserved:
            raise exceptions.BadRequest("Cannot reserve bill that is reserved")
        if self.is_invoiced:
            raise exceptions.BadRequest("Cannot reserve bill that has been invoiced")
        if self.is_service_rendered:
            raise exceptions.BadRequest(
                "Cannot transfer bills whose that service has been rendered"
            )
        if (
            str(self.billed_to_type).casefold()
            == str(PayerSchemeType.INSURANCE).casefold()
        ):
            raise exceptions.BadRequest(
                "Cannot reserve bills that are billed to Insurance"
            )
        if patient.deposit < self.selling_price:
            raise exceptions.BadRequest("Not enough deposit to reserve bill")

        # set fields
        self.is_reserved = True
        self.cleared_status = str(BillStatus.CLEARED)
        patient.send_to_reserve()
        self.save()
        return self


class CashBook(models.Model):
    """Model serves as cashbook for cashiers"""

    csb_id = models.CharField(max_length=256, null=False, blank=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=256,
        choices=CashBookStatus.choices(),
        default=CashBookStatus.OPEN,
        null=False,
        blank=False,
    )
    created_by = models.JSONField(
        default=dict,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Cashbooks"

    def __str__(self):
        return self.csb_id

    def save(self, *args, **kwargs):
        if not self.id:
            self.csb_id
        super(CashBook, self).save(*args, **kwargs)

    @classmethod
    def validate_created_by(cls, user_id) -> bool:
        user_cashbook = cls.objects.filter(
            created_by__id=user_id, status=CashBookStatus.OPEN
        )
        return user_cashbook.exists()

    @classmethod
    def open(cls, user: User):
        """Opens a cashbook for an existing user"""
        if cls.validate_created_by(user.id):
            raise exceptions.BadRequest("User already have an open cashbook")
        cashbook = cls.objects.create(
            status=CashBookStatus.OPEN,
            created_by=lib.trim_user_data(lib.model_to_dict(user)),
        )
        return cashbook

    def close(self):
        """Closes cashbook"""
        self.status = CashBookStatus.CLOSED
        self.save()
        return self

    def set_csb_id(self):
        """
        Generates a unique invoice item
        Invoice id should only be generated when invoice is confirmed

        Returns:
            str: inv_id
        """
        if self.csb_id:
            return self.csb_id

        PREFIX = AppConfig().cashbook_id_prefix
        CURRENT_YEAR = str(datetime.utcnow().year)
        CURRENT_MONTH = str(datetime.utcnow().month).zfill(2)
        pattern_string = f"{CURRENT_YEAR}{CURRENT_MONTH}"
        re_pattern = re.compile(f"{pattern_string}(.*)")
        serial_no = 1
        cashbooks = CashBook.objects.filter(csb_id__isnull=False).filter(
            csb_id__contains=pattern_string
        )
        if cashbooks.count() > 0:
            latest_cashbook = reduce(
                lambda csb1, csb2: csb1 if csb1.created_at > csb2.created_at else csb2,
                cashbooks,
            )
            serial_no = int(re_pattern.findall(latest_cashbook.csb_id)[-1]) + 1

        unique_id = f"{PREFIX}{CURRENT_YEAR}{CURRENT_MONTH}{serial_no}"
        self.csb_id = unique_id
        self.save()
        return self.csb_id


class PaymentMethod(models.Model):
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=256, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Payment Methods"

    def __str__(self):
        return self.name


class Payment(models.Model):
    bills = models.JSONField(default=list)
    patient = models.JSONField(default=dict)
    payment_method = models.JSONField(default=dict)
    payment_type = models.CharField(
        max_length=256, choices=PaymentType.choices(), default=str(PaymentType.DEPOSIT)
    )
    invoice = models.ForeignKey(
        "Invoice",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    audit_log = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Payments"

    def __str__(self):
        return str(self.id)


class Invoice(models.Model):
    inv_id = models.CharField(null=True, blank=True, max_length=256)
    memo = models.TextField(null=True, blank=True)
    encounter = models.IntegerField(null=True, blank=True)
    encounter_type = models.CharField(
        choices=EncounterInvoiceType.choices(), max_length=256, null=True, blank=True
    )
    patient = models.JSONField(default=dict)
    bill_lines = models.JSONField(default=list)
    payment_lines = models.JSONField(default=list)
    total_charge = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=256, choices=InvoiceStatus.choices(), default=InvoiceStatus.DRAFT
    )
    payer_scheme = models.ForeignKey(PayerScheme, null=True, on_delete=models.PROTECT)
    scheme_type = models.CharField(
        max_length=256, choices=PayerSchemeType.choices(), default=PayerSchemeType.SELF
    )
    due_date = models.DateTimeField(null=True, blank=True)
    confirmed_by = models.JSONField(default=dict)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.JSONField(default=dict)
    updated_by = models.JSONField(default=dict)

    class Meta:
        verbose_name_plural = "Invoices"
        permissions = (("add_bill", "Can add bill"), ("remove_bill", "Can remove bill"))

    def __str__(self):
        return str(self.id)

    def set_invoice_id(self):
        """
        Generates a unique invoice item
        Invoice id should only be generated when invoice is confirmed

        Returns:
            str: inv_id
        """
        if self.inv_id:
            return self.inv_id

        if str(self.status).casefold() == InvoiceStatus.DRAFT.casefold():
            self.inv_id.status = None
            self.save()
            return None

        PREFIX = AppConfig().invoice_id_prefix
        CURRENT_YEAR = str(datetime.utcnow().year)
        CURRENT_MONTH = str(datetime.utcnow().month).zfill(2)
        pattern_string = f"{CURRENT_YEAR}{CURRENT_MONTH}"
        re_pattern = re.compile(f"{pattern_string}(.*)")
        serial_no = 1
        invoices = (
            Invoice.objects.filter(inv_id__isnull=False)
            .exclude(status=str(InvoiceStatus.DRAFT))
            .filter(inv_id__contains=pattern_string)
        )
        if invoices.count() > 0:
            latest_invoice = reduce(
                lambda x, y: x if x.confirmed_at > y.confirmed_at else y, invoices
            )
            serial_no = int(re_pattern.findall(latest_invoice.inv_id)[-1]) + 1

        unique_id = f"{PREFIX}{CURRENT_YEAR}{CURRENT_MONTH}{serial_no}"
        self.inv_id = unique_id
        self.save()
        return self.inv_id
