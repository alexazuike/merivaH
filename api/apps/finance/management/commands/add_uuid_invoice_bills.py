import uuid
from typing import List

from django.core.management.base import BaseCommand

from api.apps.finance.models import Invoice


class Command(BaseCommand):
    help = "adds uuid to all bills in invoice bill_lines"

    def handle(self, *args, **options):
        # gets all invoice

        invoices: List[Invoice] = Invoice.objects.all()
        for invoice in invoices:
            bill_lines = invoice.bill_lines
            for bill in bill_lines:
                bill.pop("patient", None)
                if not bill.get("_id"):
                    bill["_id"] = str(uuid.uuid4())
            for payment in invoice.payment_lines:
                payment.pop("patient", None)
                payment.pop("audit_log", None)
            invoice.save()
            self.stdout.write(self.style.SUCCESS(f"invoice id {invoice.id}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"finished adding bill _ids"))
