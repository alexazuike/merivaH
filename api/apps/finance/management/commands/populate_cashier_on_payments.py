from django.core.management.base import BaseCommand
from typing import List

from api.apps.finance.models import Payment, Bill
from api.includes import utils


class Command(BaseCommand):
    help = "setup cashier on paments"

    def handle(self, *args, **options):
        payments: List[Payment] = Payment.objects.all()
        for payment in payments:
            created_by = self.get_log_creator(payment)
            payment.created_by = created_by or {}
        Payment.objects.bulk_update(payments, fields=["created_by"])
        self.stdout.write(self.style.SUCCESS("Payment Updated"))

    def get_log_creator(self, payment: Payment):
        log: dict = next(
            (log for log in payment.audit_log if log["event"] == "create"), None
        )
        if log:
            return log.get("user")
