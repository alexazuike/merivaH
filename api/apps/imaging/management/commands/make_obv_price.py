from django.core.management.base import BaseCommand
from typing import List

from api.apps.imaging import models


class Command(BaseCommand):
    help = "Create imaging prices for imaging without price"

    def handle(self, *args, **options):
        imaging_obvs: List[
            models.ImagingObservation
        ] = models.ImagingObservation.objects.filter(bill_item_code__isnull=True)
        if imaging_obvs.count() > 0:
            for imaging_obv in imaging_obvs:
                imaging_obv.create_bill_item(
                    created_by={
                        "id": None,
                        "username": "system",
                    },
                    bill_price=0,
                    cost_price=0,
                    description=imaging_obv.name,
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Created bill item for {imaging_obv.name}")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        "Done creating bill items for imaging observations"
                    )
                )
        else:
            self.stdout.write(self.style.SUCCESS("No imaging panels without price"))
