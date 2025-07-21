from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from api.includes import utils
from api.apps.finance.models import BillableItem
from api.apps.encounters.models import Clinic
from api.apps.laboratory.models import LabPanel
from api.apps.imaging.models import ImagingObservation
from api.apps.inventory.models import Product
from api.apps.nursing.models import NursingService
from api.apps.messaging.models import MessageService


@receiver(post_save, sender=Clinic)
@receiver(post_save, sender=LabPanel)
@receiver(post_save, sender=ImagingObservation)
@receiver(post_save, sender=Product)
@receiver(post_save, sender=NursingService)
@receiver(post_save, sender=MessageService)
def create_modify_bill_item(sender, instance, created, **kwargs):
    """Function creates or modifies billeable item"""
    if created:
        module = (
            str(utils.Modules.MESSAGING)
            if sender == MessageService
            else str(utils.Modules.NURSING)
            if sender == NursingService
            else str(utils.Modules.INVENTORY)
            if sender == Product
            else str(utils.Modules.LABORATORY)
            if sender == LabPanel
            else str(utils.Modules.IMAGING)
            if sender == ImagingObservation
            else str(utils.Modules.ENCOUNTERS)
        )
        billable_item = BillableItem.objects.create(
            module=module,
            created_by=instance._created_by or {},
            selling_price=instance._bill_price or 0,
            cost=instance._cost_price or 0,
            description=instance.name,
        )
        instance.bill_item_code = billable_item.item_code
        instance.save()
        return instance
    else:
        bill_item_search = BillableItem.objects.filter(
            item_code=instance.bill_item_code
        )
        if bill_item_search.exists():
            bill_item = bill_item_search.first()
            bill_item.update_module_bill_details(
                bill_price=instance._bill_price,
                cost_price=instance._cost_price,
                description=instance.name,
            )
            return bill_item
        else:
            billable_item = BillableItem.objects.create(
                module=module,
                created_by={},
                selling_price=instance._bill_price or 0,
                cost=instance._cost_price or 0,
                description=instance.name,
            )
            instance.bill_item_code = billable_item.item_code
            instance.save()
            return instance


@receiver(post_delete, sender=Clinic)
@receiver(post_delete, sender=LabPanel)
@receiver(post_delete, sender=ImagingObservation)
@receiver(post_delete, sender=Product)
@receiver(post_delete, sender=NursingService)
@receiver(post_delete, sender=MessageService)
def delete_bill_item(sender, instance, **kwargs):
    """Function deletes billable item"""
    if instance.bill_item_code is not None and instance.bill_item_code != "":
        bill_item: BillableItem = BillableItem.objects.get(
            item_code=instance.bill_item_code
        )
        bill_item.delete()
        return bill_item
