import io
from decimal import Decimal
from typing import List
from concurrent.futures import ThreadPoolExecutor

from api.includes import file_utils, utils, exceptions
from api.apps.finance import models


class PriceListLib:
    """Hander for uploading price list item excel file"""

    def __init__(
        self,
        price_list: models.PriceList,
        user_dict: dict,
        excel_file=None,
        price_list_items: List[dict] = None,
    ):
        self.price_list = price_list
        self.excel_file = excel_file
        self.user = user_dict
        self.price_list_items: List[dict] = price_list_items
        self.INSURANCE_CORPORATE_PRICE_LIST_ITEM_HEADERS_OUTPUT = (
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
        self.INSURANCE_CORPORATE_PRICE_LIST_ITEM_HEADERS_INPUT = (
            "bill_item_code",
            "selling_price",
            "co_pay",
            "is_auth_req",
            "is_capitated",
            "module",
            "is_exclusive",
            "post_auth_allowed",
        )
        self.SELF_PRICE_LIST_ITEM_HEADERS_OUTPUT = (
            "bill_item_code",
            "description",
            "selling_price",
            "module",
            "post_paid",
        )
        self.SELF_PRICE_LIST_ITEM_HEADERS_INPUT = (
            "bill_item_code",
            "selling_price",
            "module",
            "is_post_paid",
        )
        self.INPUT_HEADERS = list(
            set(
                self.SELF_PRICE_LIST_ITEM_HEADERS_INPUT
                + self.INSURANCE_CORPORATE_PRICE_LIST_ITEM_HEADERS_OUTPUT
            )
        )
        self.OUTPUT_HEADERS = list(
            set(
                self.SELF_PRICE_LIST_ITEM_HEADERS_OUTPUT
                + self.INSURANCE_CORPORATE_PRICE_LIST_ITEM_HEADERS_OUTPUT
            )
        )

    def __parse_co_pay_in(self, co_pay_value: str, co_pay_type: str) -> dict:
        value_type = models.CoPayValueType.AMOUNT
        if co_pay_type.casefold() == str(models.CoPayValueType.PERCENTAGE).casefold():
            value_type = models.CoPayValueType.PERCENTAGE

        return models.CoPaySchema(value=float(co_pay_value), type=value_type).dict()

    def __parse_price_list_item_out(
        self, price_list_item: models.PriceListItem
    ) -> dict:
        """Parses price list item to dictionary

        Args:
            price_list_item: Price list item object

        Returns:
            price_list_item_data: Dictionary containing price list item data
        """
        billable_item = models.BillableItem.objects.filter(
            item_code=price_list_item.bill_item_code
        )

        price_list_item_data = {
            "bill_item_code": price_list_item.bill_item_code,
            "description": (
                billable_item.first().description if billable_item.exists() else None
            ),
            "selling_price": price_list_item.selling_price,
            "co_pay_value": price_list_item.co_pay["value"],
            "co_pay_type": price_list_item.co_pay["type"],
            "auth_required": bool(price_list_item.is_auth_req),
            "capitated": bool(price_list_item.is_capitated),
            "module": price_list_item.module,
            "is_exclusive": bool(price_list_item.is_exclusive),
            "post_auth_allowed": bool(price_list_item.post_auth_allowed),
        }
        return price_list_item_data

    def __parse_price_list_item_in(self, price_list_item: dict) -> dict:
        """Parses dictionary to price_list_item

        Args:
            price_list_item: dict

        Returns:
            dict: parsed
        """
        price_list_item_data = {
            "bill_item_code": price_list_item["bill_item_code"],
            "selling_price": Decimal(price_list_item["selling_price"]),
            "price_list": self.price_list,
            "co_pay": self.__parse_co_pay_in(
                price_list_item["co_pay_value"], price_list_item["co_pay_type"]
            ),
            "is_auth_req": utils.str_to_bool(price_list_item["auth_required"]),
            "is_capitated": utils.str_to_bool(price_list_item["capitated"]),
            "module": price_list_item["module"],
            "is_exclusive": utils.str_to_bool(price_list_item["excluded"]),
            "post_auth_allowed": utils.str_to_bool(
                price_list_item["post_auth_allowed"]
            ),
        }
        return price_list_item_data

    def __create_update_data(self, price_list_item_data: dict):
        """Creates or updates price list items in database

        Args:
            price_list_items: List of price list items

        Returns:
            bill_item_code: str: returns bill item code of items that fails to upload
        """
        if (
            models.BillableItem.objects.filter(
                item_code=price_list_item_data["bill_item_code"]
            ).count()
            > 0
        ):
            models.PriceListItem.objects.update_or_create(
                bill_item_code=price_list_item_data["bill_item_code"],
                price_list=self.price_list,
                defaults=price_list_item_data,
            )
            return None
        return price_list_item_data["bill_item_code"]

    def upload(self):
        """Uploads large content to price list item

        Args:
            file: File object
            price_list_id: Id of price list

        Raises:
            exceptions.BadRequest: If excel file is invalid
        """
        if self.excel_file:
            file_handler = file_utils.FileUtils()
            excel_file_schema = file_handler.read_excel_file(self.excel_file)
            excel_file_content = excel_file_schema.body
            excel_file_headers = excel_file_schema.headers

            caseless_headers = [header.lower() for header in excel_file_headers]
            caseless_self_headers = [header.lower() for header in self.OUTPUT_HEADERS]

            if set(caseless_headers).difference(set(caseless_self_headers)):
                raise exceptions.BadRequest(
                    "Invalid excel file headers. Expected: {}".format(
                        self.INPUT_HEADERS
                    )
                )
            try:
                self.price_list_items = [
                    self.__parse_price_list_item_in(price_list_item)
                    for price_list_item in excel_file_content
                ]
            except ValueError as e:
                raise exceptions.BadRequest(str(e))
        with ThreadPoolExecutor(max_workers=10) as executor:
            failed_bill_item_codes = executor.map(
                self.__create_update_data, self.price_list_items
            )
            return failed_bill_item_codes

    def download(self, module: str = None) -> io.BytesIO:
        """Creates an excel file for download"""
        price_list_items = models.PriceListItem.objects.filter(
            price_list=self.price_list
        )
        if module:
            price_list_items = price_list_items.filter(module=module)

        price_list_items_out = [
            self.__parse_price_list_item_out(price_list_item)
            for price_list_item in price_list_items
        ]
        file_handler = file_utils.FileUtils()
        return file_handler.write_excel_file(price_list_items_out)
