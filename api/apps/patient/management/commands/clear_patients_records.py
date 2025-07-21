from django.core.management.base import BaseCommand
from api.apps import finance

from api.apps.patient import models as patient_models
from api.apps.laboratory import models as lab_models
from api.apps.imaging import models as imaging_models
from api.apps.encounters import models as encounters_models
from api.apps.finance import models as finance_models


class Command(BaseCommand):
    help = "Clear patient records"

    def handle(self, *args, **options):
        # clear all patient records
        patients = patient_models.Patient.objects.all()
        patients.update(deposit=0, reserve=0, payment_scheme=[])
        self.stdout.write(self.style.SUCCESS("Patient records updated"))

        # clear all laboaatory models
        lab_models.LabOrder.objects.all().delete()
        lab_models.LabPanelOrder.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("laboratory patients records cleared"))

        # clear all imaging models
        imaging_models.ImagingOrder.objects.all().delete()
        imaging_models.ImagingObservationOrder.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("imaging patients records cleared"))

        # clear all encounters models
        encounters_models.Encounter.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("encounters patients records cleared"))

        # clear all finance models
        finance_models.Bill.objects.all().delete()
        finance_models.Payment.objects.all().delete()
        finance_models.Invoice.objects.all().delete()
        finance_models.PriceListItem.objects.all().delete()
        finance_models.PayerScheme.objects.all().delete()
        finance_models.PriceList.objects.all().delete()
        finance_models.Payer.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("finance patients records cleared"))
