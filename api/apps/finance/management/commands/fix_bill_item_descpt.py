from django.core.management.base import BaseCommand
from typing import List

from api.apps.laboratory import models as lab_models
from api.apps.finance import models as finance_models
from api.apps.encounters import models as encounter_models
from api.apps.imaging import models as imaging_models
from api.includes import utils


class Command(BaseCommand):
    help = "add description to billable items without description"

    def handle(self, *args, **options):
        billable_items = finance_models.BillableItem.objects.filter(
            description__isnull=True
        )

        for billable_item in billable_items:
            if billable_item.module == str(utils.Modules.ENCOUNTERS):
                clinic = encounter_models.Clinic.objects.filter(
                    bill_item_code=billable_item.item_code
                )
                if clinic.count() > 0:
                    billable_item.description = clinic[0].name
                    billable_item.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Updated description for {billable_item.item_code}"
                        )
                    )
            elif billable_item.module == str(utils.Modules.LABORATORY):
                lab_panel = lab_models.LabPanel.objects.filter(
                    bill_item_code=billable_item.item_code
                )
                if lab_panel.count() > 0:
                    billable_item.description = lab_panel[0].name
                    billable_item.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Updated description for {billable_item.item_code}"
                        )
                    )

            elif billable_item.module == str(utils.Modules.IMAGING):
                imaging_test = imaging_models.ImagingObservation.objects.filter(
                    bill_item_code=billable_item.item_code
                )
                if imaging_test.count() > 0:
                    billable_item.description = imaging_test[0].name
                    billable_item.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Updated description for {billable_item.item_code}"
                        )
                    )
