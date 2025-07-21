from typing import List
from concurrent.futures import ThreadPoolExecutor

from api.apps.finance import models
from api.includes import exceptions, utils, file_utils


class BillableItemLib:
    """Handler for billable item library"""

    def __init__(
        self,
        user_data: dict,
    ):
        self.user_data = user_data
        self.BILLABLE_HEADERS = (
            "item_code",
            "description",
            "cost",
            "selling_price",
            "module",
        )

        self.PRICE_LIST_ITEM_HEADERS = (
            "bill_item_code",
            "description",
            "selling_price",
            "co_pay_value",
            "co_pay_type",
            "module",
            "auth_required",
            "capitated",
            "excluded",
            "post_auth_allowed",
        )

    def __parse_price_list_data_template(
        self, billable_items: List[models.BillableItem]
    ):
        """parses list of price list items to list of dictionaries"""
        price_list_items_values = []
        for billable_item in billable_items:
            price_list_item_value = {
                "bill_item_code": billable_item.item_code,
                "module": billable_item.module,
                "selling_price": billable_item.selling_price,
                "description": billable_item.description,
                "co_pay_value": 0,
                "co_pay_type": str(models.CoPayValueType.AMOUNT),
                "auth_required": True,
                "capitated": False,
                "excluded": False,
                "post_auth_allowed": False,
            }
            price_list_items_values.append(price_list_item_value)
        return price_list_items_values

    def __update_billable_item(self, billable_item: dict):
        """Update billable item"""
        bill_item = models.BillableItem.objects.filter(
            item_code=billable_item["item_code"]
        )

        if bill_item.exists():
            bill_item_obj: models.BillableItem = bill_item.first()
            bill_item_obj.cost = billable_item["cost"]
            bill_item_obj.selling_price = billable_item["selling_price"]
            bill_item_obj.save()
            return None
        return billable_item["bill_item_code"]

    def get_billable_item_excel(self, module: str = None):
        """Gets spreedset bytes of billable item excel file

        Args:
            module: module of billable item

        Returns:
            bytes of excel file
        """
        billable_items = models.BillableItem.objects.all()
        if module:
            module = utils.Modules.get_module_value(module)
            billable_items = billable_items.filter(module=module)
        billable_items = billable_items.order_by("item_code")
        billable_items_values = [
            utils.model_to_dict(
                billable_item,
                exclude_fields={"created_by", "updated_by", "created_at", "updated_at"},
            )
            for billable_item in billable_items
        ]
        excel_bytes = file_utils.FileUtils().write_excel_file(billable_items_values)
        return excel_bytes

    def upload_billable_items_excel(self, excel_file) -> List[str]:
        """Uploads billable items excel file

        Args:
            excel_file: excel file

        Returns:
            list of billable items that were not uploaded
        """
        try:
            file_util = file_utils.FileUtils()
            excel_data = file_util.read_excel_file(excel_file)
            headers = excel_data.headers
            excel_content = excel_data.body

            caseless_headers = [header.lower() for header in headers]
            caseless_self_headers = [header.lower() for header in self.BILLABLE_HEADERS]

            if set(caseless_self_headers).difference(set(caseless_headers)):
                raise exceptions.BadRequest(
                    "Invalid headers in excel file. Expected headers: {}".format(
                        self.BILLABLE_HEADERS
                    )
                )

            with ThreadPoolExecutor(max_workers=10) as executor:
                bill_items = executor.map(self.__update_billable_item, excel_content)
                return bill_items
        except ValueError as e:
            raise exceptions.BadRequest("Invalid excel file")

    def get_price_list_excel(self, module: str = None):
        """Gets spreadsheet template for  price list items
        of a payerscheme from billable items
        """
        billable_items = models.BillableItem.objects.all()
        if module:
            billable_items = billable_items.filter(module=module)
        price_list_items_values = self.__parse_price_list_data_template(billable_items)
        excel_bytes = file_utils.FileUtils().write_excel_file(price_list_items_values)
        return excel_bytes
