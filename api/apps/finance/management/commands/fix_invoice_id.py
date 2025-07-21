from django.core.management.base import BaseCommand
from typing import List

from api.apps.finance.models import Invoice, InvoiceStatus


class Command(BaseCommand):
    help = "create invoice id for invoices without invoice id"

    def handle(self, *args, **options):
        invoices: List[Invoice] = Invoice.objects.filter(inv_id__isnull=True).exclude(
            status=str(InvoiceStatus.DRAFT)
        )

        for invoice in invoices:
            invoice.set_invoice_id()
            self.stdout.write(
                self.style.SUCCESS(f"added invoice id for {invoice.inv_id}")
            )
