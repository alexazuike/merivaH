from collections import OrderedDict
from typing import Optional

from pydantic import BaseModel

from api.apps.imaging.models import ImagingObservationOrder
from api.apps.patient import utils as patient_utils
from api.includes import utils


class ImagingReportStruct(BaseModel):
    img_id: str
    patient_uhid: str
    patient_email: Optional[str] = str()
    patient_gender: str
    patient_age_years: Optional[str]
    patient_age_months: Optional[str]
    patient_age_days: Optional[str]
    patient_service_arm: Optional[str] = str()
    patient_service_arm_no: Optional[str] = str()
    patient: str
    modality: str
    img_obv: str
    status: str
    captured_by: Optional[str]
    captured_at: Optional[str]
    reported_by: Optional[str]
    reported_at: Optional[str]
    approved_by: Optional[str]
    approved_at: Optional[str]
    cancelled_by: Optional[str]
    cancelled_at: Optional[str]
    created_at: str

    @classmethod
    def _get_log_data(cls, instance: ImagingObservationOrder):
        audit_search_params = {
            "captured": "captured",
            "cancelled": "cancelled",
        }
        log_data = utils.extract_audit_log_data(instance.audit_log, audit_search_params)
        return log_data

    @classmethod
    def _get_patient_data(cls, instance: ImagingObservationOrder):
        patient_data = patient_utils.PatientSummary(**instance.patient).to_report_dict()
        return patient_data

    @classmethod
    def _get_reported_details(cls, instance: ImagingObservationOrder):
        first_name = instance.reported_by.get("first_name", "")
        last_name = instance.reported_by.get("last_name", "")
        return {
            "reported_at": str(instance.reported_on) if instance.reported_on else None,
            "reported_by": f"{last_name} {first_name}",
        }

    @classmethod
    def initialize(cls, instance: ImagingObservationOrder) -> "ImagingReportStruct":
        data = {
            "img_id": instance.img_order.img_id,
            "modality": instance.img_obv.get("modality", {}).get("name", ""),
            "img_obv": instance.img_obv.get("name", ""),
            "status": instance.status.upper(),
            "created_at": instance.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            **cls._get_reported_details(instance),
            **cls._get_patient_data(instance),
            **cls._get_log_data(instance),
        }
        return cls(**data)

    def to_response_struct(self):
        data = self.dict().copy()
        data = utils.to_response_struct(data)
        return OrderedDict(data)

    def to_report_struct(self):
        return utils.to_report_structure(self.dict())
