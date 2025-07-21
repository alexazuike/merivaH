from django.core.management.base import BaseCommand
from typing import List

from api.apps.finance.models import Payment, Bill
from api.includes import utils


class Command(BaseCommand):
    help = "convert ids of bills to objects on payments"

    def handle(self, *args, **options):
        payments = Payment.objects.all()
        for payment in payments:
            bill_objs = Bill.objects.filter(id__in=payment.bills)
            if bill_objs.exists():
                bills_data = [
                    utils.model_to_dict(
                        instance=bill, exclude_fields={"invoice", "patient"}
                    )
                    for bill in bill_objs
                ]
                payment.bills = bills_data
                payment.save()
                print(f"payment {payment.id} is modified")
