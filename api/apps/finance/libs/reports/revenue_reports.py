from collections import OrderedDict
from typing import Optional, TypedDict
from decimal import Decimal
from datetime import datetime

from django.db.models import Sum, Count, F
from django.db.models.query import QuerySet

from api.apps.finance.models.bills import Bill
from api.includes import utils


class ReportSummaryStruct(TypedDict):
    module: str
    total_amount: float
    count: int


class ReportDetailStruct(TypedDict):
    bill_source: str
    bill_item_code: str
    description: str
    total_quantity: int
    total_amount: float
    count: int


class RevenueSummaryReportGenerator:
    def __init__(self, bills: QuerySet[Bill], is_invoiced: bool):
        self.modules = [module.value for module in utils.Modules]
        self.bills = bills
        self.is_invoiced = is_invoiced

    def _compute_report_data(self, module: str) -> ReportSummaryStruct:
        bills = self.bills.filter(is_invoiced=self.is_invoiced, bill_source=module)
        data = ReportSummaryStruct(
            module=module,
            total_amount=bills.aggregate(Sum("selling_price"))["selling_price__sum"]
            or 0,
            count=bills.count(),
        )
        return data

    def _compute_report(self) -> list:
        response_data = [self._compute_report_data(module) for module in self.modules]
        return response_data

    def to_response_struct(self):
        data = self._compute_report()
        return data

    def to_report_struct(self):
        return utils.to_report_structure(self.to_response_struct())


class RevenueDetailReportGenerator:
    def __init__(self, bills: QuerySet[Bill], is_invoiced: bool):
        self.bills = (
            bills.filter(is_invoiced=is_invoiced)
            .values("bill_item_code")
            .annotate(
                count=Count("bill_item_code"),
                total_amount=Sum("selling_price"),
                total_quantity=Sum("quantity"),
                bill_source=F("bill_source"),
                description=F("description"),
            )
        )

    def to_response_struct(self):
        return self.bills

    def to_report_struct(self):
        return utils.to_report_structure(list(self.bills))
