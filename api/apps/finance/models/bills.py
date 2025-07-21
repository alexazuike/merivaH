from enum import Enum
from typing import Union

from django.db import models
from pydantic import BaseModel

from api.includes import utils, exceptions
from api.apps.patient.models import Patient
from .payer import PayerScheme, PayerSchemeType

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


################################ Models ###############################


class Bill(models.Model):
    """serves a representation of all bills passing through
    the system.
    """

    bill_item_code = models.CharField(max_length=256, null=False, blank=False)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    cleared_status = models.CharField(max_length=256, choices=BillStatus.choices())
    quantity = models.IntegerField(default=1)
    bill_source = models.CharField(max_length=256, choices=utils.Modules.choices())
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
            ("transfer_bill", "Can transfer bill to different schemes"),
            ("reserve_bill", "Can reserve bill"),
            ("unreserve_bill", "Can unreserve bill"),
        )

    @property
    def is_cleared(self):
        return self.cleared_status == BillStatus.CLEARED

    def run_post_payment_action(self):
        """
        Runs actions after payment is made
        Actions are based  on payment bill source
        each payment bill source defines it's own bill action
        """

        from .. import utils as fin_utils

        bill_source_class = fin_utils.MODULE_TO_BILL_MODEL_MAPPING[self.bill_source]
        bill_source_instance_filter = bill_source_class.objects.filter(
            bill=str(self.id)
        )
        if bill_source_instance_filter.exists():
            bill_source_instance = bill_source_instance_filter.first()
            bill_source_instance.post_paymet_action(self)

    def unreserve(self) -> "Bill":
        """unreserve bill"""
        patient: Patient = Patient.objects.get(id=self.patient.get("id"))

        if not self.is_reserved:
            raise exceptions.BadRequest("Cannot unreserve bill that is not reserved")
        if self.is_invoiced:
            raise exceptions.BadRequest("Cannot unreserve bill that has been invoiced")
        if self.is_service_rendered:
            raise exceptions.BadRequest(
                "Cannot unreserve bills whose that service has been rendered"
            )
        if str(self.billed_to_type).casefold() not in (
            str(PayerSchemeType.SELF_PREPAID).casefold(),
            str(PayerSchemeType.SELF_POSTPAID).casefold(),
        ):
            raise exceptions.BadRequest(
                "Cannot unreserve bills that are not billed to self"
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
            raise exceptions.BadRequest("Cannot reserve bill that is already reserved")
        if self.is_invoiced:
            raise exceptions.BadRequest("Cannot reserve bill that has been invoiced")
        if self.is_service_rendered:
            raise exceptions.BadRequest(
                "Cannot reserve bills whose that service has been rendered"
            )
        if str(self.billed_to_type).casefold() not in (
            str(PayerSchemeType.SELF_PREPAID).casefold(),
            str(PayerSchemeType.SELF_POSTPAID).casefold(),
        ):
            raise exceptions.BadRequest(
                "Cannot reserve bills that are not billed to self"
            )
        if patient.deposit < self.selling_price:
            raise exceptions.BadRequest("Not enough deposit to reserve bill")

        # set fields
        self.is_reserved = True
        self.cleared_status = str(BillStatus.CLEARED)
        patient.send_to_reserve(self.selling_price)
        self.save()
        return self
