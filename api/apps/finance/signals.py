from typing import List, Dict
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone

from api.apps.patient.models import Patient
from api.includes import exceptions, utils
from config import preferences
from api.apps.finance.models import (
    BillableItem,
    Bill,
    BillStatus,
    Invoice,
    InvoiceStatus,
)
from api.apps.finance.libs import billing
from api.apps.finance.libs.invoice import Invoice as InvoiceLib
from api.apps.encounters.models import Encounter, Clinic
from api.apps.laboratory.models import LabPanel, LabPanelOrder
from api.apps.laboratory.utils import LabPanelOrderStatus
from api.apps.imaging.models import ImagingObservation, ImagingObservationOrder
from api.apps.imaging.utils import ImagingObservationOrderStatus
from api.apps.inventory.models import Product
from api.apps.nursing.models import NursingService, NursingOrder, NursingOrderStatus


@receiver(post_save, sender=Clinic)
@receiver(post_save, sender=LabPanel)
@receiver(post_save, sender=ImagingObservation)
@receiver(post_save, sender=Product)
@receiver(post_save, sender=NursingService)
def create_modify_bill_item(sender, instance, created, **kwargs):
    """Function creates or modifies billeable item"""
    if created:
        module = (
            str(utils.Modules.NURSING)
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
def delete_bill_item(sender, instance, **kwargs):
    """Function deletes billable item"""
    if instance.bill_item_code is not None and instance.bill_item_code != "":
        bill_item: BillableItem = BillableItem.objects.get(
            item_code=instance.bill_item_code
        )
        bill_item.delete()
        return bill_item


@receiver(pre_save, sender=Encounter)
@receiver(pre_save, sender=LabPanelOrder)
@receiver(pre_save, sender=ImagingObservationOrder)
def validate_bill_services(sender, instance, raw, **kwargs):
    if instance.id:
        db_instance = sender.objects.get(id=instance.id)
        if db_instance.status.casefold() == "cancelled".casefold():
            raise exceptions.BadRequest("Cannot update a cancelled service")

        if preferences.AppPreferences().billing_enabled:
            if db_instance.bill:
                bill: Bill = Bill.objects.get(id=int(instance.bill))
                if (
                    bill.cleared_status == str(BillStatus.UNCLEARED)
                    and instance.status.casefold() != "cancelled".casefold()
                ):
                    raise exceptions.BadRequest("Bill is not cleared")

                if instance.status.casefold() == "cancelled".casefold():
                    if bill.is_invoiced:
                        raise exceptions.BadRequest(
                            "Cannot cancel service that has been invoiced or rendered"
                        )
                    if bill.is_service_rendered:
                        raise exceptions.BadRequest(
                            "Cannot cancel service that has been invoiced or rendered"
                        )
                    bill.delete()
                    instance.bill = None


@receiver(post_save, sender=Encounter)
@receiver(post_save, sender=LabPanelOrder)
@receiver(post_save, sender=ImagingObservationOrder)
def create_bill(sender, instance, created, **kwargs):
    """Function creates bill for services"""
    if created:
        module = (
            str(utils.Modules.LABORATORY)
            if sender == LabPanelOrder
            else str(utils.Modules.IMAGING)
            if sender == ImagingObservationOrder
            else str(utils.Modules.ENCOUNTERS)
        )

        if preferences.AppPreferences().billing_enabled:
            billing_util = billing.Billing(
                bill_item_code=instance._bill_item_code,
                quantity=instance._quantity or 1,
                module_name=module,
                patient=instance.patient,
                description=instance._name,
                billed_to=instance._payment_scheme,
            )
            bill = billing_util.create_bill()
            instance.bill = bill.id
            instance.save()
            return instance
    else:
        ########## updates bills service rendered
        if instance.bill:
            bill: Bill = Bill.objects.get(id=instance.bill)

            if str(instance.status).casefold() in (
                LabPanelOrderStatus.RECIEVE_SPECIMEN.casefold(),
                ImagingObservationOrderStatus.CAPTURE.casefold(),
            ) or (sender == Encounter and instance.acknowledged_at):
                bill.is_service_rendered = True
                bill.serviced_rendered_at = timezone.now()
                bill.save()

                # add bill to invoice after service has been rendered
                # get all invoice for a patient, in draft, and of the billed_to
                if not bill.is_invoiced:
                    patient = Patient.objects.get(id=bill.patient.get("id"))
                    invoices = Invoice.objects.filter(
                        patient__id=bill.patient.get("id"),
                        status=str(InvoiceStatus.DRAFT),
                        scheme_type=bill.billed_to_type,
                    )
                    if bill.billed_to:
                        invoices = invoices.filter(payer_scheme=bill.billed_to)
                    else:
                        invoices = invoices.filter(payer_scheme__isnull=True)
                    if invoices.count() > 0:
                        # add bill to invoice
                        invoice_obj: Invoice = invoices.first()
                        invoice_lib = InvoiceLib(
                            patient=patient,
                            user_data=bill.updated_by,
                            invoice=invoice_obj,
                        )
                        if bill.id not in invoice_lib.get_bills():
                            invoice_lib.add_bills(bills=[bill])
                    else:
                        # create new invoice
                        invoice_lib = InvoiceLib(
                            patient=patient,
                            user_data=bill.updated_by,
                            scheme_type=str(bill.billed_to_type),
                            payer_scheme=bill.billed_to,
                        )
                        invoice_obj = invoice_lib.create_invoice(bills=[bill])
        return instance


@receiver(post_save, sender=NursingOrder)
def create_bills_direct_to_invoice(sender, instance: NursingOrder, created, **kwargs):
    """Function creates bill for services"""

    if (
        instance.status == NursingOrderStatus.CLOSED
        and "status" in kwargs.get("update_fields")
        and preferences.AppPreferences().billing_enabled
    ):
        # get all nusrsing services in the order tasks
        # create bills for them
        # get current invoice for patient and add bill to invoice

        # GET BILLABLE ITEMS IN NURSING ORDER
        tasks = instance.tasks
        service_billables: Dict[str, List[BillableItem]] = {}
        bills: List[Bill] = []
        for task in tasks:
            services_bill_item_code = [
                service["bill_item_code"]
                for service in task.get("nursing_services")
                if service.get("bills")
            ]
            if services_bill_item_code:
                billable_items_objs = BillableItem.objects.filter(
                    id__in=services_bill_item_code
                )
                if billable_items_objs.exists():
                    service_billables[task.get("id")] = billable_items_objs.values_list(
                        "id", flat=True
                    )

        # CREATE BILLS
        if service_billables:
            for task_id, billable_items in service_billables.items():
                task_bills: List[int] = []
                for billable_item in billable_items:
                    billing_util = billing.Billing(
                        bill_item_code=billable_item.item_code,
                        quantity=1,
                        module_name=utils.Modules.NURSING,
                        patient=instance.patient,
                        description=billable_item.description,
                    )
                    bill = billing_util.create_bill()
                    bills.append(bill)
                    task_bills.append(bill.id)
                instance.update_task(task_id=task_id, field="bills", value=task_bills)

        # CREATE/ ADD BiLLS TO INVOICE
        patient = Patient.objects.get(id=bill.patient.get("id"))
        invoices = Invoice.objects.filter(
            patient__id=bill.patient.get("id"),
            status=str(InvoiceStatus.DRAFT),
            scheme_type=bill.billed_to_type,
        )
        if bill.billed_to:
            invoices = invoices.filter(payer_scheme=bill.billed_to)
        else:
            invoices = invoices.filter(payer_scheme__isnull=True)
        if invoices.count() > 0:
            invoice_obj: Invoice = invoices.first()
            invoice_lib = InvoiceLib(
                patient=patient,
                user_data=bill.updated_by,
                invoice=invoice_obj,
            )
            if bill.id not in invoice_lib.get_bills():
                invoice_lib.add_bills(bills=bills)
            else:
                invoice_lib = InvoiceLib(
                    patient=patient,
                    user_data=bill.updated_by,
                    scheme_type=str(bill.billed_to_type),
                    payer_scheme=bill.billed_to,
                )
                invoice_obj = invoice_lib.create_invoice(bills=[bill])
