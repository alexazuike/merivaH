from django.core.management.base import BaseCommand

from api.apps.encounters.models import Encounter

class Command(BaseCommand):
    help = "adds uuid to all bills in invoice bill_lines"

    def handle(self, *args, **options):
        encounters = Encounter.objects.all()
        for encounter in encounters:
            chart = encounter.chart
            diags = chart['diag']
            for  diag in diags:
                print(diag, "\n")
                if type(diag['value']['comment']) == str:
                    diags.remove(diag)
                    
            chart['diag'] = diags
            encounter.chart = chart
            encounter.save()
