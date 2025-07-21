from django.core.management.base import BaseCommand
from typing import List

from api.apps.laboratory import models


class Command(BaseCommand):
    help = "Create lab panel prices for panels without price"

    def handle(self, *args, **options):
        lab_panels: List[models.LabPanel] = models.LabPanel.objects.filter(
            bill_item_code__isnull=True
        )
        if lab_panels.count() > 0:
            for lab_panel in lab_panels:
                lab_panel.create_bill_item(
                    created_by={
                        "id": None,
                        "username": "system",
                    },
                    bill_price=0,
                    cost_price=0,
                    description=lab_panel.name,
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Created bill item for {lab_panel.name}")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS("Done creating bill items for lab panels")
                )
        else:
            self.stdout.write(self.style.SUCCESS("No lab panels without price"))
