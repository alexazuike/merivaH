from typing import Union, List
from pydantic import BaseModel
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.crypto import get_random_string
from django.utils import timezone

from api.apps.encounters.models import Encounter, EncounterChart


class ChartSchema(BaseModel):
    id: str = f"CHT_{get_random_string(length=5)}"
    value: dict
    created_by: dict
    created_at: str = timezone.now().isoformat()


class ChartDataSchema(BaseModel):
    id: str = f"CHT_{get_random_string(length=5)}"
    type: str
    value: dict
    created_by: dict
    created_at: str = timezone.now().isoformat()


class Command(BaseCommand):
    help = "migrates encounters charts to list of dictionaries"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        encounters: List[Encounter] = Encounter.objects.all()
        for encounter in encounters:
            self._backup_legacy_charts(encounter)
            # self._modify_chart(encounter)
        else:
            Encounter.objects.bulk_update(encounters, ["legacy_chart", "chart"])
            self.stdout.write(self.style.SUCCESS("Encounter Charts Migration Done"))

    def _backup_legacy_charts(self, encounter: Encounter):
        encounter.legacy_chart = encounter.chart
        encounter.chart = []

    def _modify_chart(self, encounter: Encounter):
        charts = []
        legacy_chart = encounter.legacy_chart
        user_ids = set()
        for key, value in legacy_chart.items():
            if key not in ["orders", "vitals"]:
                for item in value:
                    user_id = item.get("created_by", {}).get("id")
                    user_ids.add(user_id)

        for user_id in user_ids:
            chart: dict = self._get_user_chart(user_id, encounter)
            charts.append(chart)
        encounter.chart = charts

    def _get_user_chart(self, user_id: int, encounter: Encounter) -> dict:
        values = []
        created_by = {}
        for key, value in encounter.legacy_chart.items():
            if key not in ["orders", "vitals"]:
                for item in value:
                    if user_id == item.get("created_by", {}).get("id"):
                        created_by = item.get("created_by")
                        values.append(
                            ChartDataSchema(type=str(key), value=item.get("value"))
                        )
        chart = EncounterChart(chart=values, created_by=created_by)
        return chart.dict()
