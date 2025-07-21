from typing import List, Union, Dict, Optional
import logging

from pydantic import BaseModel

from .. import models as finance_models
from api.includes import exceptions, utils
from api.apps.patient import models as patient_models


# Get an instance of a logger
logger = logging.getLogger(__name__)


class BillingDataResponse(BaseModel):
    bill_package_usage: Optional[finance_models.PatientBillPackageUsage]
    bill: Optional[finance_models.Bill]

    class Config:
        arbitrary_types_allowed = True


class Billing:
    def __init__(
        self,
        bill_item_code: str,
        quantity: int,
        module_name: str,
        patient: dict,
        description: str,
        billed_to: finance_models.PayerScheme = None,
        bill: finance_models.Bill = None,
    ):
        self.patient: dict = patient
        self.bill_item: finance_models.BillableItem = self.__get_bill_item(
            bill_item_code
        )
        payer_scheme, price_list_item = self.__get_payer_scheme(
            bill_item_code, billed_to
        )
        self.payer_scheme: finance_models.PayerScheme = payer_scheme
        self.price_list_item: finance_models.PriceListItem = price_list_item
        self.billed_to_type: finance_models.PayerSchemeType = None
        self.bill_source: str = module_name
        self.selling_price: float
        self.cost_price: float
        self.cleared_status: finance_models.BillStatus
        self.co_pay: float = 0.0
        self.quantity: int = quantity
        self.description = description
        self.is_capitated: bool = False
        self.is_reserved: bool = False
        self.is_auth_req: bool = (
            False if not self.price_list_item else self.price_list_item.is_auth_req
        )
        self.post_auth_allowed: bool = (
            False
            if not self.price_list_item
            else self.price_list_item.post_auth_allowed
        )
        self.bill = bill

    def __use_bill_package(self):
        """
        check if patient has an active bill package containing billable_item
        if true, then get the subscription and create a bill package usage
        """
        active_sub = finance_models.PatientBillPackageSubscription.get_patient_active_billable_item_subscription(
            patient_id=self.patient.get("id"), billable_item_id=self.bill_item.pk
        )
        if not active_sub:
            return
        try:
            package_sub_usage = finance_models.PatientBillPackageUsage.objects.create(
                package_subscription=active_sub,
                billable_item=utils.model_to_dict(self.bill),
                quantity=self.quantity,
            )
            return package_sub_usage
        except exceptions.BadRequest as e:
            logger.info(str(e))
            return None

    def __get_bill_item(self, bill_item_code: str) -> finance_models.BillableItem:
        """Get billable item"""
        try:
            bill_item = finance_models.BillableItem.objects.get(
                item_code=bill_item_code
            )
            return bill_item
        except finance_models.BillableItem.DoesNotExist:
            raise exceptions.NotFoundException("Billable Item not found")

    def __get_patient_schemes(self) -> Union[List[finance_models.PayerScheme], None]:
        """Gets patient schemes" """
        patient: "patient_models.Patient" = patient_models.Patient.objects.get(
            id=self.patient.get("id")
        )
        if patient.payment_scheme is not None:
            patient_scheme_ids = [
                scheme.get("payer_scheme", {}).get("id")
                for scheme in patient.payment_scheme
            ]
            patient_scheme_objs = finance_models.PayerScheme.objects.filter(
                id__in=patient_scheme_ids
            )
            return (
                list(patient_scheme_objs) if patient_scheme_objs.count() != 0 else None
            )
        return None

    def __get_price_list_item(
        self,
        bill_item_code: str,
        payer_scheme: finance_models.PayerScheme = None,
    ) -> finance_models.PriceListItem:
        """Gets price list item

        Args:
            bill_item_code: bill item code
            payer_scheme: payer scheme

        Returns:
            price list item
        """
        if payer_scheme:
            price_list = payer_scheme.price_list
            if price_list:
                price_list_item = finance_models.PriceListItem.objects.filter(
                    bill_item_code=bill_item_code, price_list=price_list
                )
                if price_list_item.exists():
                    return price_list_item.first()
        return None

    def __get_payer_scheme(
        self,
        bill_item_code: str,
        payer_scheme: finance_models.PayerScheme = None,
    ) -> Union[finance_models.PayerScheme, None]:
        """Gets payer scheme

        Args:
            bill_item_code: bill item code
            payer_scheme: payer scheme

        Returns:
            payer scheme
        """
        if payer_scheme:
            price_list_item = self.__get_price_list_item(bill_item_code, payer_scheme)
            return (payer_scheme, price_list_item) if price_list_item else None
        patient_schemes = self.__get_patient_schemes()
        if patient_schemes:
            for scheme in patient_schemes:
                price_list_item = self.__get_price_list_item(bill_item_code, scheme)
                if price_list_item:
                    return scheme, price_list_item
        return None, None

    def get_unit_selling_price(self) -> float:
        """Gets unit selling price
        Will retrieve price list from patient payment scheme
        if price list item is not found, will return billable item selling price
        """
        if self.payer_scheme and self.price_list_item:
            return self.price_list_item.selling_price
        return self.bill_item.selling_price

    def get_co_pay_price(self, selling_price: float):
        co_pay_details: dict = self.price_list_item.co_pay
        if co_pay_details.get("type") == str(finance_models.CoPayValueType.AMOUNT):
            return co_pay_details.get("value")
        return selling_price * (co_pay_details.get("value") / 100)

    def get_bill_status(self) -> finance_models.BillStatus:
        """Gets status to set bill to basedon clearance by payment schemwe"""
        if self.payer_scheme:
            if self.payer_scheme.type == str(
                finance_models.PayerSchemeType.SELF_POSTPAID
            ):
                return str(finance_models.BillStatus.CLEARED)

            if (
                self.payer_scheme.type
                in (
                    str(finance_models.PayerSchemeType.INSURANCE),
                    str(finance_models.PayerSchemeType.CORPORATE),
                )
                and self.price_list_item
            ):
                # if item has co-pay, bill is uncleared
                if not self.price_list_item.is_exclusive:
                    if self.price_list_item.co_pay:
                        total_selling_price = (
                            self.get_unit_selling_price() * self.quantity
                        )
                        self.co_pay = self.get_co_pay_price(total_selling_price)
                        return str(finance_models.BillStatus.UNCLEARED)

                    # if item requires auth, set bill status to uncleared
                    if self.price_list_item.is_auth_req:
                        if self.price_list_item.post_auth_allowed:
                            return str(finance_models.BillStatus.CLEARED)
                        return str(finance_models.BillStatus.UNCLEARED)

                    # if item is capitated, set bill status cleared
                    if self.price_list_item.is_capitated:
                        self.is_capitated = True
                        self.selling_price = 0.0
                        return str(finance_models.BillStatus.CLEARED)
                    return str(finance_models.BillStatus.CLEARED)

        # check patient deposit
        patient: "patient_models.Patient" = patient_models.Patient.objects.get(
            id=self.patient.get("id")
        )
        if patient.deposit >= self.selling_price:
            patient.send_to_reserve(
                self.selling_price
            )  # reserve bills if balance suffices
            self.is_reserved = True
            return str(finance_models.BillStatus.CLEARED)
        return str(finance_models.BillStatus.UNCLEARED)

    def get_billed_to_type(self):
        """Gets type of entity to whom bill is billed to"""
        if self.payer_scheme:
            return self.payer_scheme.type
        return str(finance_models.PayerSchemeType.SELF_PREPAID)

    def create_bill(
        self,
    ) -> BillingDataResponse:
        """Creates bill for a service"""
        package_usage = self.__use_bill_package()
        if package_usage:
            return BillingDataResponse(bill_package_usage=package_usage, bill=None)
        self.selling_price = (
            self.get_unit_selling_price() * self.quantity
            if self.bill_item.selling_price
            else 0.0
        )

        self.cost_price = (
            self.bill_item.cost * self.quantity if self.bill_item.cost else 0.0
        )

        self.cleared_status = (
            self.get_bill_status()
            if self.selling_price != 0
            else str(finance_models.BillStatus.CLEARED)
        )

        bill_obj = finance_models.Bill.objects.create(
            bill_item_code=self.bill_item.item_code,
            cost_price=self.cost_price,
            selling_price=self.selling_price,
            cleared_status=self.cleared_status,
            quantity=self.quantity,
            bill_source=self.bill_source,
            billed_to=self.payer_scheme,
            billed_to_type=self.get_billed_to_type(),
            co_pay=self.co_pay,
            is_capitated=self.is_capitated,
            description=self.description,
            patient=self.patient,
            is_reserved=self.is_reserved,
            is_auth_req=self.is_auth_req,
            post_auth_allowed=self.post_auth_allowed,
            invoice=None,
        )
        return BillingDataResponse(bill_package_usage=None, bill=bill_obj)

    @classmethod
    def create_bills(
        cls,
        module: str,
        patient: dict,
        billable_items_qty: List[Dict[int, finance_models.BillableItem]],
    ) -> List[BillingDataResponse]:
        """Creates Bills in bulk for set of services"""
        bills = []
        for billable_item in billable_items_qty:
            for quantity, billable_item in billable_item.items():
                bill = cls(
                    bill_item_code=billable_item.item_code,
                    quantity=quantity,
                    module_name=module,
                    patient=patient,
                    description=billable_item.description,
                ).create_bill()
                bills.append(bill)
        return bills

    def transfer(
        self, scheme_type: finance_models.PayerSchemeType
    ) -> finance_models.Bill:
        """Transfer bill from one scheme to another

        Args:
            scheme_type[PayerSchemeType]: scheme type of scheme to transfer to

        Returns:
            Bill: object of bill transfered
        """
        patient_schemes_ids = [
            scheme.get("payer_scheme", {}).get("id")
            for scheme in self.patient.get("payment_scheme", {})
        ]
        # validations
        if not self.bill:
            raise ValueError("Bill object must be specified")
        if self.bill.is_invoiced:
            raise exceptions.BadRequest("Cannot transfer bill that is already invoiced")
        if self.bill.is_service_rendered:
            raise exceptions.BadRequest(
                "Cannot transfer bills whose that service has been rendered"
            )
        if self.payer_scheme and str(self.payer_scheme.type) != str(scheme_type):
            raise exceptions.BadRequest("Scheme and SchemeType do not match")
        if self.payer_scheme and str(self.payer_scheme.id) not in patient_schemes_ids:
            raise exceptions.BadRequest(
                "Patient is not registered with specified payment scheme"
            )
        if (
            str(self.bill.billed_to_type)
            in (
                str(finance_models.PayerSchemeType.INSURANCE),
                str(finance_models.PayerSchemeType.CORPORATE),
            )
            and self.bill.is_auth_req
            and self.bill.auth_code
        ):
            raise exceptions.BadRequest("Bill is already cleared by payment scheme")

        # if bill is reserved and scheme_type is self, it will be unreserved
        if (
            str(self.bill.billed_to_type)
            in (
                str(finance_models.PayerSchemeType.SELF_PREPAID),
                str(finance_models.PayerSchemeType.SELF_POSTPAID),
            )
            and self.bill.is_reserved
        ):
            self.bill.unreserve()

        self.selling_price = (
            self.get_unit_selling_price() * self.quantity
            if self.bill_item.selling_price
            else 0.0
        )

        self.cost_price = (
            self.bill_item.cost * self.quantity if self.bill_item.cost else 0.0
        )

        self.cleared_status = (
            self.get_bill_status()
            if self.selling_price != 0
            else str(finance_models.BillStatus.CLEARED)
        )

        # update fields
        self.bill.bill_item_code = self.bill_item.item_code
        self.bill.cost_price = self.cost_price
        self.bill.selling_price = self.selling_price
        self.bill.cleared_status = self.cleared_status
        self.bill.billed_to = self.payer_scheme
        self.bill.billed_to_type = self.get_billed_to_type()
        self.bill.co_pay = self.co_pay
        self.bill.is_capitated = self.is_capitated
        self.bill.description = self.description
        self.bill.patient = self.patient
        self.is_reserved = self.is_reserved
        self.bill.is_auth_req = self.is_auth_req
        self.bill.post_auth_allowed = self.post_auth_allowed

        self.bill.save()  # save updates
        return self.bill
