from django.db.models.signals import post_save, pre_save
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
    PatientBillPackageUsage,
    PatientBillPackageSubscription,
)
from api.apps.finance.libs import billing
from api.apps.finance.libs.invoice import Invoice as InvoiceLib
from api.apps.encounters.models import Encounter
from api.apps.laboratory.models import LabPanelOrder
from api.apps.laboratory.utils import LabPanelOrderStatus
from api.apps.imaging.models import ImagingObservationOrder
from api.apps.imaging.utils import ImagingObservationOrderStatus
from api.apps.nursing.models import NursingOrder, NursingTaskStatus


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
@receiver(post_save, sender=PatientBillPackageSubscription)
def create_bill(sender, instance, created, **kwargs):
    """Function creates bill for services"""
    if created:
        module = (
            str(utils.Modules.FINANCE)
            if sender == PatientBillPackageSubscription
            else str(utils.Modules.LABORATORY)
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
            bill_response = billing_util.create_bill()
            instance.bill = str(bill_response.bill.pk) if bill_response.bill else None
            instance.bill_package_usage = (
                str(bill_response.bill_package_usage.pk)
                if bill_response.bill_package_usage
                else None
            )
            instance.save()
            return instance
    else:
        ########## updates bills service rendered
        if instance.bill and sender != PatientBillPackageSubscription:
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

        if instance.bill_package_usage:
            if str(instance.status).casefold() in (
                LabPanelOrderStatus.RECIEVE_SPECIMEN.casefold(),
                ImagingObservationOrderStatus.CAPTURE.casefold(),
            ) or (sender == Encounter and instance.acknowledged_at):
                bill_package_usage = PatientBillPackageUsage.objects.get(
                    id=instance.bill_package_usage
                )
                bill_package_usage.is_service_renderded = True
                bill_package_usage.save()
        return instance


@receiver(post_save, sender=NursingOrder)
def bill_nursing_services(sender, instance: NursingOrder, created, **kwargs):
    """Function creates bill for services"""

    if (
        created or (not created and "tasks" in kwargs.get("update_fields", []))
    ) and preferences.AppPreferences().billing_enabled:
        for task in instance.tasks:
            # GET BILLABLE ITEMS IN NURSING ORDER
            if (
                task.get("nursing_services")
                and task.get("status") == NursingTaskStatus.CLOSED
                and not task.get("bills")
            ):
                services_bill_item_code = [
                    service["bill_item_code"]
                    for service in task.get("nursing_services", {})
                    if service.get("bill_item_code")
                ]
                billable_items = BillableItem.objects.filter(
                    item_code__in=services_bill_item_code
                )

                # CREATE BILLS
                billable_items_qty = [
                    {1: billable_item} for billable_item in billable_items
                ]
                bills_responses = billing.Billing.create_bills(
                    module=utils.Modules.NURSING,
                    patient=instance.patient,
                    billable_items_qty=billable_items_qty,
                )
                bills = [bill.bill for bill in bills_responses if bill.bill]
                bill_package_usages = [
                    response.bill_package_usage
                    for response in bills_responses
                    if response.bill_package_usage
                ]
                instance.update_task(
                    task_id=task.get("id"),
                    values={
                        "bills": [
                            response.bill.pk
                            for response in bills_responses
                            if response.bill
                        ],
                        "bill_package_usages": [
                            response.bill_package_usage.pk
                            for response in bills_responses
                            if response.bill_package_usage
                        ],
                    },
                )

                PatientBillPackageUsage.objects.filter(
                    id__in=[usage.pk for usage in bill_package_usages]
                ).update(is_service_rendered=True)

                # CREATE/ ADD BiLLS TO INVOICE
                InvoiceLib.create_invoices(
                    created_by=instance.updated_by,
                    patient=instance.patient,
                    bills=bills,
                )
