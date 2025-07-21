from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
import pytz
from typing import Optional

from pydantic import BaseModel
from django.utils import timezone

from api.includes import utils


class PatientSummary(BaseModel):
    lastname: str = str()
    firstname: str = str()
    middle_name: str = str()
    uhid: str
    email: Optional[str] = str()
    gender: str
    date_of_birth: Optional[str]
    age: Optional[dict] = {}
    service_arm: Optional[str] = str()
    service_arm_no: Optional[str] = str()

    def _format_age(self, transaction_date: datetime = None):
        try:
            transaction_date = transaction_date or timezone.now()
            date_of_birth = parser.parse(self.date_of_birth)
            date_of_birth = date_of_birth.replace(tzinfo=pytz.UTC)
            date_difference: relativedelta = relativedelta(
                transaction_date, date_of_birth
            )
            return {
                "age_years": self.age.get("year", date_difference.years),
                "age_months": self.age.get("month", date_difference.months),
                "age_days": self.age.get("day", date_difference.days),
            }
        except (parser.ParserError, TypeError):
            return {
                "age_years": None,
                "age_months": None,
                "age_days": None,
            }

    def _format_name(self):
        return f"{self.lastname} {self.firstname} {self.middle_name}"

    def to_report_dict(self, transaction_date: datetime = None) -> dict:
        data_dict = self.dict()
        data_dict = {**data_dict, **self._format_age(transaction_date)}
        data_dict = {f"patient_{key}": value for key, value in data_dict.items()}
        data_dict["patient"] = self._format_name()
        return data_dict
