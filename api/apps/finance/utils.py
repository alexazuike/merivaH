from typing import Dict, List, Optional, Type
from decimal import Decimal

from api.includes import exceptions
from api.includes import utils
from api.apps.encounters.models import Encounter
from api.apps.laboratory.models import LabPanelOrder
from api.apps.imaging.models import ImagingObservationOrder
from api.apps.finance.models import PatientBillPackageSubscription
from . import models


MODULE_TO_BILL_MODEL_MAPPING: Dict[str, Type[utils.DJANGO_MODEL]] = {
    utils.Modules.ENCOUNTERS.value: Encounter,
    utils.Modules.LABORATORY.value: LabPanelOrder,
    utils.Modules.IMAGING.value: ImagingObservationOrder,
    utils.Modules.FINANCE.value: PatientBillPackageSubscription,
}


def get_uncleared_bill_object(bill_id: int):
    try:
        bill = models.Bill.objects.get(id=bill_id)
        if bill.cleared_status == str(models.BillStatus.CLEARED):
            raise exceptions.BadRequest(f"Bill with id {bill_id} is already cleared")
        return bill
    except models.Bill.DoesNotExist:
        raise models.Bill.DoesNotExist(f"Bill with id {bill_id} does not exist")


def clear_bill(bill):
    if bill.cleared_status == str(models.BillStatus.CLEARED):
        raise exceptions.BadRequest(f"Bill with id {bill.id} is already cleared")
    bill.cleared_status = str(models.BillStatus.CLEARED)
    bill.save()
    return bill


def clean_bill_details(bill_details: dict):
    bill_details.pop("bill_source", None)
    bill_details.pop("co_pay", None)
    bill_details.pop("service_center", None)
    bill_details.pop("description", None)
    bill_details.pop("is_capitated", None)
    bill_details.pop("patient", None)
    return bill_details


def create_reserve_payment_method() -> "models.PaymentMethod":
    """This method creates a reserve payment method.
    If the reserve payment method already exists it skips creation
    """
    details = {
        "name": "reserve",
        "description": "payment method for patient reserve finance",
    }
    object, created = models.PaymentMethod.objects.get_or_create(
        name="reserve", defaults=details
    )
    print(f"reserve method created status: {created}")
    return object


def create_refund_payment_method() -> "models.PaymentMethod":
    """This method creates a refund payment method.
    If the refund payment method already exists it skips creation
    """
    details = {
        "name": "refund",
        "description": "payment method for patient refund finance",
    }
    object, created = models.PaymentMethod.objects.get_or_create(
        name="refund", defaults=details
    )
    print(f"refund method created status: {created}")
    return object


def create_deposit_payment_method() -> "models.PaymentMethod":
    """This method creates a deposit payment method.
    If the deposit payment method already exists it skips creation
    """
    details = {
        "name": "deposit",
        "description": "payment method for patient deposit finance",
    }
    object, created = models.PaymentMethod.objects.get_or_create(
        name="deposit", defaults=details
    )
    print(f"deposit method created status: {created}")
    return object


def add_payments(
    patient_dict: dict,
    payment_details: List[models.PaymentMethodStruct],
    user_details: dict,
    bills: Optional[List[dict]],
    payment_type: models.PaymentType,
):
    """This method adds payments to payment history"""
    payment_objs = []
    for payment in payment_details:
        amount = str(payment.amount)
        payment_method = payment.payment_method

        audit_log = utils.AuditLog(
            user=user_details,
            event=utils.AuditEvent.CREATE,
            fields={
                "amount": amount,
                "payment_method": payment_method,
            },
        ).dict()

        payment_obj = models.Payment(
            patient=patient_dict,
            payment_type=str(payment_type),
            total_amount=Decimal(amount),
            payment_method=payment_method,
            audit_log=[audit_log],
            bills=bills,
        )
        payment_objs.append(payment_obj)

    payments = models.Payment.objects.bulk_create(payment_objs)
    return utils.list_to_queryset(models.Payment, payments)
