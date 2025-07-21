import re
from enum import Enum
from functools import reduce
from datetime import datetime
from django.db import models

from .payer import PayerScheme, PayerSchemeType
from config import preferences


class InvoiceStatus(str, Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

    def __str__(self):
        return self.value


class EncounterInvoiceType(str, Enum):
    IN_PATIENT = "IN PATIENT"
    OUT_PATIENT = "OUT PATIENT"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

    def __str__(self):
        return self.value


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
        max_length=256,
        choices=PayerSchemeType.choices(),
        default=PayerSchemeType.SELF_PREPAID,
    )
    due_date = models.DateTimeField(null=True, blank=True)
    confirmed_by = models.JSONField(default=dict)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.JSONField(default=dict)
    updated_by = models.JSONField(default=dict)
    cancelled_by = models.JSONField(default=dict)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Invoices"
        permissions = (
            ("add_bill", "Can add bill"),
            ("remove_bill", "Can remove bill"),
            ("edit_bill", "Can edit bills"),
            ("markup_price", "Can increase price"),
            ("markdown_price", "Can reduce price"),
            ("confirm_invoice", "Can confirm invoice"),
        )

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
            self.inv_id = None
            self.save()
            return None

        PREFIX = preferences.AppPreferences().invoice_id_prefix_code
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
