from pyrsistent import s
from . import models as finance_models
from . import utils
from api.config import exceptions


class Billing:
    def __init__(
        self,
        bill_item_code: str,
        quantity: int,
        module_name: str,
        patient: dict,
        description: str,
        billed_to: finance_models.PayerScheme = None,
    ):
        self.bill_item: finance_models.BillableItem = self.__get_bill_item(
            bill_item_code
        )
        self.payer_scheme: finance_models.PayerScheme = billed_to
        self.billed_to_type: utils.PayerSchemeType = None
        self.bill_source: str = module_name
        self.selling_price: float
        self.cost_price: float
        self.cleared_status: utils.BillStatus
        self.co_pay: float = 0.0
        self.quantity: int = quantity
        self.patient = patient
        self.description = description
        self.is_capitated: bool = False
        if self.payer_scheme:
            self.price_list_item = finance_models.PriceListItem.objects.get(
                bill_item_code=self.bill_item.item_code,
                price_list=self.payer_scheme.price_list,
            )

    def __get_bill_item(self, bill_item_code: str) -> finance_models.BillableItem:
        try:
            bill_item = finance_models.BillableItem.objects.get(
                item_code=bill_item_code
            )
            return bill_item
        except finance_models.BillableItem.DoesNotExist:
            raise exceptions.NotFoundException("Billable Item not found")

    def get_unit_selling_price(self) -> float:
        """Gets unit selling price
        Will retrieve price list from patient payment scheme
        if price list item is not found, will return billable item selling price
        """
        if self.payer_scheme:
            if self.price_list_item:
                return self.price_list_item.selling_price
        return self.bill_item.selling_price

    def get_co_pay_price(self, selling_price: float):
        co_pay_details: dict = self.price_list_item
        if co_pay_details.get("type") == str(utils.CoPayValueType.AMOUNT):
            return co_pay_details.get("value")
        return selling_price * (co_pay_details.get("value") / 100)

    def get_bill_status(self) -> utils.BillStatus:
        """Gets status to set bill to basedon clearance by payment schemwe"""
        if self.payer_scheme:
            if self.payer_scheme.type == str(utils.PayerSchemeType.SELF):
                return str(utils.BillStatus.UNCLEARED)
            if self.payer_scheme.type == str(utils.PayerSchemeType.INSURANCE):

                # if item has co-pay, bill is uncleared
                if self.price_list_item.co_pay:
                    total_selling_price = self.get_unit_selling_price() * self.quantity
                    self.co_pay = self.get_co_pay_price(total_selling_price)
                    return str(utils.BillStatus.UNCLEARED)

                # if item requires auth, set bill status to uncleared
                if self.price_list_item.is_auth_req:
                    return str(utils.BillStatus.UNCLEARED)

                # if item is capitated, set bill status cleared
                if self.price_list_item.is_capitated:
                    self.is_capitated = True
                    self.selling_price = 0.0
                    return str(utils.BillStatus.CLEARED)

                return str(utils.BillStatus.CLEARED)

        return str(utils.BillStatus.UNCLEARED)

    def get_billed_to_type(self):
        """Gets type of entity to whom bill is billed to"""
        if self.payer_scheme:
            if self.payer_scheme.type == str(utils.PayerSchemeType.INSURANCE):
                return str(utils.PayerSchemeType.INSURANCE)
        return str(utils.PayerSchemeType.SELF)

    def create_bill(
        self,
    ) -> finance_models.Bill:
        """Creates bill for a service"""
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
            else str(utils.BillStatus.CLEARED)
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
        )
        return bill_obj
