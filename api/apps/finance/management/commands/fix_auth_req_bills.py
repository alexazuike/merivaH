from django.core.management.base import BaseCommand
from typing import List

from api.apps.finance.models import Bill, PriceListItem, PayerSchemeType, PriceList


class Command(BaseCommand):
    help = "create invoice id for invoices without invoice id"

    def handle(self, *args, **options):
        # get all Insurance Bills
        bills = Bill.objects.filter(billed_to_type=str(PayerSchemeType.INSURANCE))

        # set is_auth_req for all of them
        if bills.count() > 0:
            for bill in bills:
                self.stdout.write(
                    self.style.SUCCESS(f"former is_auth_req {bill.is_auth_req}")
                )
                print(bill.billed_to)
                price_list_item = PriceListItem.objects.get(
                    price_list=bill.billed_to.price_list,
                    bill_item_code=bill.bill_item_code,
                )
                bill.is_auth_req = price_list_item.is_auth_req
                bill.save()
                self.stdout.write(
                    self.style.SUCCESS(f"present is_auth_req {bill.is_auth_req}")
                )
