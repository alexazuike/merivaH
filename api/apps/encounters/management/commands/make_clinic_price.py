from django.core.management.base import BaseCommand
from typing import List

from api.apps.encounters import models


class Command(BaseCommand):
    help = "Create clinic prices for clinics without price"

    def handle(self, *args, **options):
        clinics: List[models.Clinic] = models.Clinic.objects.filter(
            bill_item_code__isnull=True
        )
        if clinics.count() > 0:
            for clinic in clinics:
                clinic.create_bill_item(
                    created_by={
                        "id": None,
                        "username": "system",
                    },
                    bill_price=0,
                    cost_price=0,
                    description=clinic.name,
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Created bill item for {clinic.name}")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS("Done creating bill items for clinics")
                )
        else:
            self.stdout.write(self.style.SUCCESS("No clinics without price"))
