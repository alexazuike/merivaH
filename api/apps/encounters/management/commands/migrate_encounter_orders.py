from typing import List

from django.core.management.base import BaseCommand

from api.apps.encounters.models import Encounter


class Command(BaseCommand):
    help = "migrate encounter orders"

    def handle(self, *args, **options):
        encounters: List[Encounter] = Encounter.objects.all()
        for encounter in encounters:
            self.set_encounter_orders(encounter)
        else:
            Encounter.objects.bulk_update(encounters, fields=["orders"])
            self.stdout.write(self.style.SUCCESS("Encounter orders updated"))

    def set_encounter_orders(self, encounter: Encounter):
        lab_orders = self.get_lab_encounter_orders(encounter)
        img_orders = self.get_img_encounter_orders(encounter)
        prescription_orders = self.get_prc_encounter_orders(encounter)
        orders = [*lab_orders, *img_orders, *prescription_orders]
        encounter.orders = orders

    def get_lab_encounter_orders(self, encounter: Encounter):
        orders = encounter.chart.get("orders", {})
        laboratory: List[dict] = orders.get("laboratory", [])
        for lab in laboratory:
            lab["type"] = "laboratory"
        return laboratory

    def get_img_encounter_orders(self, encounter: Encounter):
        orders = encounter.chart.get("orders", {})
        imaging: List[dict] = orders.get("imaging", [])
        for img in imaging:
            img["type"] = "imaging"
        return imaging

    def get_prc_encounter_orders(self, encounter: Encounter):
        orders = encounter.chart.get("orders", {})
        prescription: List[dict] = orders.get("prescription", [])
        for prescription in prescription:
            prescription["type"] = "prescription"
        return prescription
