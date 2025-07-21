from django.core.management.base import BaseCommand
from typing import List

from api.apps.finance.models import PayerScheme, PayerSchemeType, Bill, Invoice
from api.includes import utils


class Command(BaseCommand):
    help = "fix all scheme types"

    def __fix_scheme_type(self):
        schemes = PayerScheme.objects.filter(type__iexact="SELF").update(
            type=PayerSchemeType.SELF_PREPAID
        )
        print("schemes fixed")

    def __fix_bill_scheme_type(self):
        bills = Bill.objects.filter(billed_to_type__iexact="SELF").update(
            billed_to_type=PayerSchemeType.SELF_PREPAID
        )
        print("bills scheme fixed")

    def __fix_bill_invoice_bills(self):
        invoices = Invoice.objects.all()
        for invoice in invoices:
            bill_lines: List[dict] = invoice.bill_lines
            for bill in bill_lines:
                if bill.get("billed_to_type") == "SELF":
                    bill["billed_to_type"] = PayerSchemeType.SELF_PREPAID
            invoice.bill_lines = bill_lines
            invoice.save()
        else:
            print("invoices bills fixed")

    def handle(self, *args, **options):
        self.__fix_scheme_type()
        self.__fix_bill_scheme_type()
        self.__fix_bill_invoice_bills()
