from typing import List

from django.core.management.base import BaseCommand

from api.apps.encounters.models import Encounter


class Command(BaseCommand):
    help = "migrate encounter vitals"

    def handle(self, *args, **options):
        encounters: List[Encounter] = Encounter.objects.all()
        for encounter in encounters:
            self.set_encounter_vitals(encounter)
        else:
            Encounter.objects.bulk_update(encounters, fields=["vitals"])
            self.stdout.write(self.style.SUCCESS("Encounter vitals updated"))

    def set_encounter_vitals(self, encounter: Encounter):
        vitals = encounter.chart.get("vitals")
        encounter.vitals = vitals
