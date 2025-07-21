import io
import datetime as mod_datetime
from django.utils import timezone
from pydantic import BaseModel
from typing import List

from api.includes import file_utils, mail_utils, utils
from .report_gen_abstraction import ReportGenAbstract
from api.apps.finance.models import Bill, InvoiceStatus, Payment
from config import preferences


class SummaryReportStruct(BaseModel):
    """Serves as a structure for producing a summary report"""

    qty: int
    amount: float


class PeriodReportStruct(BaseModel):
    """Serves as structure for producing report at appropriate intervals"""

    present: SummaryReportStruct
    week_date: SummaryReportStruct
    month_date: SummaryReportStruct


class ReportStruct(BaseModel):
    """Structure of Report Output"""

    module: str
    report: PeriodReportStruct
    created_at: mod_datetime.datetime = timezone.now()


class PaymentReportStruct(BaseModel):
    """Strcuture for payment report struct"""

    payment_method: str
    date_amount: float
    week_date_amount: float
    month_date_amount: float


class SummaryReportGenerator(ReportGenAbstract):
    """Generates Summary Report for finance"""

    def __init__(self):
        pass

    def get_date_payment_summary(
        self,
        payment_method_name,
        min_date: mod_datetime.datetime,
        max_date: mod_datetime.datetime,
    ) -> PaymentReportStruct:
        """ """
        min_date = min_date.replace(tzinfo=mod_datetime.timezone.utc)
        max_date = max_date.replace(tzinfo=mod_datetime.timezone.utc)

        payments = Payment.objects.filter(
            payment_method__name=payment_method_name,
            created_at__range=[min_date, max_date],
        )
        return sum(payment.total_amount for payment in payments)

    def get_payment_methods_summary(self) -> List[PaymentReportStruct]:
        """Gets all payment methods used and gets
        total Invoice and Deposit amount

        PaymentMethod   Deposit     Insurance
        """
        payment_methods = list(
            Payment.objects.distinct("payment_method__name").values_list(
                "payment_method__name", flat=True
            )
        )
        end_date = timezone.now()
        daily_start_date = end_date - mod_datetime.timedelta(days=1)
        week_start_date = (
            end_date
            if end_date.weekday() == 0
            else end_date - mod_datetime.timedelta(days=end_date.weekday())
        )
        month_start_date = (
            end_date
            if end_date.day == 1
            else end_date - mod_datetime.timedelta(days=(end_date.day - 1))
        )

        report_objects: List[PaymentReportStruct] = []
        for method in payment_methods:
            report = PaymentReportStruct(
                payment_method=method or "None",
                date_amount=self.get_date_payment_summary(
                    method, daily_start_date, end_date
                ),
                week_date_amount=self.get_date_payment_summary(
                    method, week_start_date, end_date
                ),
                month_date_amount=self.get_date_payment_summary(
                    method, month_start_date, end_date
                ),
            )
            report_objects.append(report)
        return report_objects

    def get_summarised_report(
        self,
        module: utils.Modules,
        min_date: mod_datetime.datetime,
        max_date: mod_datetime.datetime,
    ) -> SummaryReportStruct:
        """Generates summarised financial report for a duration of time in a module

        Args:
            module [lib.Modules]: module to get financial reports
            min_date [datetime]: lower boundary of datetime
            max_date [datetime]: higher boundary of datetime

        Returns:
            SummaryReportStruct: object of SummaryReportStruct
        """
        min_date = min_date.replace(tzinfo=mod_datetime.timezone.utc)
        max_date = max_date.replace(tzinfo=mod_datetime.timezone.utc)

        bills = (
            Bill.objects.filter(bill_source=module)
            .filter(is_invoiced=True)
            .filter(invoice__confirmed_at__range=[min_date, max_date])
            .exclude(invoice__status=str(InvoiceStatus.DRAFT))
        )
        total_quantity = sum(bill.quantity for bill in bills)
        total_amount = sum(bill.selling_price for bill in bills)
        return SummaryReportStruct(qty=total_quantity, amount=total_amount)

    def gen_daily_report(self, module: utils.Modules):
        today_date = timezone.now()
        return self.get_summarised_report(
            module,
            min_date=today_date,
            max_date=today_date - mod_datetime.timedelta(days=1),
        )

    def gen_week_date_report(self, module: utils.Modules):
        end_date = timezone.now()
        start_date = (
            end_date
            if end_date.weekday() == 0
            else end_date - mod_datetime.timedelta(days=end_date.weekday())
        )
        return self.get_summarised_report(
            module=module, min_date=start_date, max_date=end_date
        )

    def gen_month_date_report(self, module: utils.Modules):
        end_date = timezone.now()
        start_date = (
            end_date
            if end_date.day == 1
            else end_date - mod_datetime.timedelta(days=(end_date.day - 1))
        )

        return self.get_summarised_report(
            module=module, min_date=start_date, max_date=end_date
        )

    def generate_modules_report(self) -> List[ReportStruct]:
        """Generates summary report"""
        modules = utils.Modules.module_values()
        reports = []
        for module in modules:
            present_report = self.gen_daily_report(module)
            week_report = self.gen_week_date_report(module)
            month_report = self.gen_month_date_report(module)

            period_report = PeriodReportStruct(
                present=present_report, week_date=week_report, month_date=month_report
            )

            module_report = ReportStruct(module=module, report=period_report)
            reports.append(module_report)

        return reports

    def generate_excel_report(self) -> io.BytesIO:
        """Generate excel report of sunnary records"""
        module_report_data = self.generate_modules_report()
        module_data = []
        for data in module_report_data:
            record = {
                "module": data.module,
                "amount": data.report.present.amount,
                "quantity": data.report.present.qty,
                "week_date_amount": data.report.week_date.amount,
                "week_date_qty": data.report.week_date.qty,
                "month_date_amount": data.report.month_date.amount,
                "month_date_qty": data.report.month_date.qty,
            }
            module_data.append(record)

        payment_data = self.get_payment_methods_summary()
        payment_data = [data.dict() for data in payment_data]

        excel_bytes = file_utils.FileUtils().write_multiple_sheets(
            file_utils.SheetRecord(sheet_name="Payment Record", data=payment_data),
            file_utils.SheetRecord(sheet_name="Module Report", data=module_data),
        )
        return excel_bytes

    def mail_excel_report(self):
        """Sends Admin mail"""
        admin_mail = preferences.AppPreferences().admin_mail
        print(admin_mail)
        file_object = self.generate_excel_report()
        print(file_object)
        email_utils = mail_utils.EmailUtil(
            subject="Summary Financial Report",
            body="The financial report has been attached to this mail",
            receiver_mail=admin_mail,
            attachment=file_object,
            file_name="Financial Summary Report.xlsx",
        )
        email_utils.send_mail()
        print("mail sent")
        return None
