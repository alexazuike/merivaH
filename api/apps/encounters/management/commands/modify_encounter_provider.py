from django.core.management.base import BaseCommand

from api.apps.encounters.models import Encounter


class Command(BaseCommand):
    help = "adds uuid to all bills in invoice bill_lines"

    def handle(self, *args, **options):
        encounters = Encounter.objects.all()
        for encounter in encounters:
            if type(encounter.provider) == str:
                encounter.provider = dict()

        else:
            print(encounters)
        Encounter.objects.bulk_update(encounters, fields=["provider"])
