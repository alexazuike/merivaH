from django.core.management.base import BaseCommand

from api.apps.laboratory import models, utils


class Command(BaseCommand):
    help = "populate lab panel order obv struct"

    def handle(self, *args, **options):
        panel_orders = models.LabPanelOrder.objects.filter(status__iexact="approved")
        for order in panel_orders:
            order.panel_struct = utils.to_panel_report_struct(order.panel)
            order.save()
            print(order.id)
        self.stdout.write("populate panel struct")
