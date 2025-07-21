import re
from enum import Enum
from functools import reduce
from typing import List, Optional

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from pydantic import BaseModel

from config import preferences
from api.includes import exceptions, utils

################## SCHEMAS ##########################


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


class PaymentMethodStruct(BaseModel):
    payment_method: dict
    amount: float


class PaymentSummary(BaseModel):
    patient: dict
    bills: List[dict]
    payments: List[PaymentMethodStruct]
    total_amount: float
    invoice: Optional[dict]
    user: dict


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


########################## MODELS ########################


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
    created_by = models.JSONField(default=dict)

    class Meta:
        verbose_name_plural = "Payments"
        permissions = (("accept_payment", "Can accept payments"),)

    def __str__(self):
        return str(self.id)


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
            created_by=utils.trim_user_data(utils.model_to_dict(user)),
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

        PREFIX = preferences.AppPreferences().cashbook_id_prefix_code
        CURRENT_YEAR = str(timezone.now().year)
        CURRENT_MONTH = str(timezone.now().month).zfill(2)
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
