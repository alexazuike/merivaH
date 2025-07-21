from django.core.management.base import BaseCommand
from typing import List

from api.apps.laboratory import models


class Command(BaseCommand):
    help = "setup template for lab panels and lab panel orders"

    def setup_lab_panel(self):
        models.LabPanel.objects.all().update(template=models.DEFAULT_LAB_PANEL_TEMPLATE)
        self.stdout.write(self.style.SUCCESS("Lab Panels Template Update"))

    def setup_lab_panel_in_orders(self):
        lab_panel_orders: List[
            models.LabPanelOrder
        ] = models.LabPanelOrder.objects.all()
        for panel_order in lab_panel_orders:
            panel_order.panel["template"] = models.DEFAULT_LAB_PANEL_TEMPLATE
            panel_order.panel_struct["template"] = models.DEFAULT_LAB_PANEL_TEMPLATE
        models.LabPanelOrder.objects.bulk_update(lab_panel_orders, ["panel"])
        self.stdout.write(self.style.SUCCESS("Lab Panels Template Update"))

    def handle(self, *args, **options):
        self.setup_lab_panel()
        self.setup_lab_panel_in_orders()
