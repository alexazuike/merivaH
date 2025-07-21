from django.core.management.base import BaseCommand
from typing import List

from api.apps.imaging import models
from api.includes import utils


class Command(BaseCommand):
    help = "fix imaging obv order"

    def handle(self, *args, **options):
        img_obv_orders = models.ImagingObservationOrder.objects.all()
        for order in img_obv_orders:
            modality = order.img_obv.get("modality")
            if type(modality) not in [dict, None]:
                modality = models.Modality.objects.get(id=1)
                order.img_obv["modality"] = utils.model_to_dict(modality)
                order.save()
                print(order.id)
