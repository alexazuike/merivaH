from typing import TypedDict, Optional, OrderedDict

from django.db.models.functions import Concat
from django.db.models.query import QuerySet
from django.db.models import F, Sum, Value, CharField
from pydantic import BaseModel

from api.apps.finance.models.payment import Payment
from api.apps.patient import utils as patient_utils
from api.includes import utils


class ReportSummaryStruct(TypedDict):
    payment_method: str
    cashier: str
    total_amount: float


class PaymentsSummaryReportGenerator:
    def __init__(self, payments: QuerySet[Payment]):
        self.payments = payments
        self.parsed_data = []

    def _compute_report_data(self):
        self.payments = self.payments.values(
            "payment_method__name", "created_by__id"
        ).annotate(
            payment_method=F("payment_method__name"),
            cashier=Concat(
                "created_by__last_name",
                "created_by__first_name",
                output_field=CharField(),
            ),
            total_sum=Sum("total_amount", distinct=True),
        )
        self.parsed_data = [
            ReportSummaryStruct(**self.__clean_data(payment))
            for payment in self.payments
        ]

    def __clean_data(self, payment: dict):
        cashier: str = payment.get("cashier")
        cashier = cashier.replace('"', " ").replace("\\", "").strip()
        payment["cashier"] = cashier
        payment["total_amount"] = payment.get("total_sum")
        return payment

    def to_response_struct(self):
        self._compute_report_data()
        return self.parsed_data

    def to_report_struct(self):
        return utils.to_report_structure(self.to_response_struct())


class PaymentDetailReportGenerator(BaseModel):
    patient_uhid: str
    patient_email: Optional[str] = str()
    patient_gender: str
    patient_age_years: Optional[str]
    patient_age_months: Optional[str]
    patient_age_days: Optional[str]
    patient: str
    patient_service_arm: Optional[str] = str()
    patient_service_arm_no: Optional[str] = str()
    total_amount: float
    cashier: Optional[str]
    payment_method: str
    payment_type: str
    transaction_date: str

    @classmethod
    def _get_patient_data(cls, instance: Payment):
        patient_data = patient_utils.PatientSummary(**instance.patient).to_report_dict(
            transaction_date=instance.created_at
        )
        return patient_data

    @classmethod
    def _get_cashier_details(cls, instance: Payment):
        first_name = instance.created_by.get("first_name")
        last_name = instance.created_by.get("last_name")
        return f"{first_name} {last_name}"

    @classmethod
    def initialize(cls, instance: Payment) -> "PaymentDetailReportGenerator":
        data = {
            "total_amount": instance.total_amount,
            "transaction_date": instance.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "cashier": cls._get_cashier_details(instance),
            "payment_type": instance.payment_type,
            "payment_method": instance.payment_method.get("name"),
            **cls._get_patient_data(instance),
        }
        return cls(**data)

    def to_response_struct(self):
        data = self.dict().copy()
        data = utils.to_response_struct(data)
        return OrderedDict(data)

    def to_report_struct(self):
        return utils.to_report_structure(self.dict())
