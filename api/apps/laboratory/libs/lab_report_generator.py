from collections import OrderedDict
from typing import Optional

from pydantic import BaseModel

from api.apps.laboratory.models import LabPanelOrder
from api.apps.patient import utils as patient_utils
from api.includes import utils


class LabReportStruct(BaseModel):
    asn: str
    patient_uhid: str
    patient_email: Optional[str] = str()
    patient_gender: str
    patient_age_years: Optional[str]
    patient_age_months: Optional[str]
    patient_age_days: Optional[str]
    patient_service_arm: Optional[str] = str()
    patient_service_arm_no: Optional[str] = str()
    patient: str
    lab_unit: str
    panel: str
    status: str
    specimen_taken_by: Optional[str]
    specimen_taken_at: Optional[str]
    specimen_recieved_by: Optional[str]
    specimen_recieved_at: Optional[str]
    result_submitted_by: Optional[str]
    result_submitted_at: Optional[str]
    approved_by: Optional[str]
    approved_at: Optional[str]
    cancelled_by: Optional[str]
    cancelled_at: Optional[str]
    created_at: str

    @classmethod
    def _get_log_data(cls, instance: LabPanelOrder):
        audit_search_params = {
            "recieve specimen": "specimen_taken",
            "fill result": "specimen_recieved",
            "awaiting approval": "result_submitted",
            "approved": "approved",
            "cancelled": "cancelled",
        }
        log_data = utils.extract_audit_log_data(instance.audit_log, audit_search_params)
        return log_data

    @classmethod
    def _get_patient_data(cls, instance: LabPanelOrder):
        patient_data = patient_utils.PatientSummary(**instance.patient).to_report_dict()
        return patient_data

    @classmethod
    def initialize(cls, instance: LabPanelOrder) -> "LabReportStruct":
        data = {
            "asn": instance.lab_order.asn,
            "status": instance.status,
            "lab_unit": instance.panel.get("lab_unit", {}).get("name"),
            "panel": instance.panel.get("name"),
            "created_at": instance.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
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
