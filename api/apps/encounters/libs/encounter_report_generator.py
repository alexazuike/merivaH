from collections import OrderedDict
from typing import Optional

from pydantic import BaseModel

from api.apps.encounters.models import Encounter
from api.apps.patient import utils as patient_utils
from api.includes import utils


class EncounterReportStruct(BaseModel):
    encounter_id: str
    encounter_type: str
    patient_uhid: str
    patient_email: Optional[str] = str()
    patient_gender: str
    patient_age_years: Optional[str]
    patient_age_months: Optional[str]
    patient_age_days: Optional[str]
    patient: str
    patient_service_arm: Optional[str] = str()
    patient_service_arm_no: Optional[str] = str()
    clinic: str
    status: str
    diagnosis: Optional[str]
    departmanet: Optional[str]
    nurse_seen_by: Optional[str]
    nurse_seen_at: Optional[str]
    acknowledged_by: Optional[str]
    acknowledged_at: Optional[str]
    signed_at: Optional[str]
    signed_by: Optional[str]
    provider: Optional[str]
    created_at: str

    @classmethod
    def _get_clinic_details(cls, instance: Encounter):
        clinic = instance.clinic.get("name")
        department = instance.clinic.get("department", {}).get(
            "name"
        ) or instance.clinic.get("Department", {}).get("name")
        return {"clinic": clinic, "department": department}

    @classmethod
    def _get_diagnosis(cls, instance: Encounter):
        try:
            diagnosis_list: list[dict] = [
                chart for chart in instance.chart if chart.get("type") == "diag"
            ]
            diagnosis_list = [
                f"{diag.get('value', {}).get('comment', {}).get('code')}-{diag.get('value', {}).get('comment', {}).get('case')}-{diag.get('value', {}).get('option', {})}"
                for diag in diagnosis_list
                if type(diag.get("value", {}).get("comment")) == dict
            ]
            return ", ".join(diagnosis_list)
        except ValueError:
            return str()

    @classmethod
    def _get_provider_details(cls, instance: Encounter):
        first_name = instance.provider.get("first_name", "")
        last_name = instance.provider.get("last_name", "")
        return f"{first_name} {last_name}"

    @classmethod
    def _get_signer_details(cls, instance: Encounter):
        first_name = instance.provider.get("first_name", "")
        last_name = instance.provider.get("last_name", "")
        return {
            "signed_at": (
                instance.signed_date.strftime("%Y-%m-%dT%H:%M:%SZ")
                if instance.signed_date
                else None
            ),
            "signed_by": f"{last_name} {first_name}",
        }

    @classmethod
    def _get_acknowledger_details(cls, instance: Encounter) -> dict:
        """Get acknowldger details

        Args:
            instance (Encounter): Encounter object

        Returns:
            dict: dict reprs of acknowldged person and datetime
        """

        first_name = instance.acknowledged_by.get("first_name", "")
        last_name = instance.acknowledged_by.get("last_name", "")
        return {
            "acknowledged_at": (
                instance.acknowledged_at.strftime("%Y-%m-%dT%H:%M:%SZ")
                if instance.acknowledged_at
                else None
            ),
            "acknowledged_by": f"{last_name} {first_name}",
        }

    @classmethod
    def _get_log_data(cls, instance: Encounter):
        audit_search_params = {
            "NS": "nurse_seen",
        }
        log_data = utils.extract_audit_log_data(instance.audit_log, audit_search_params)
        return log_data

    @classmethod
    def _get_patient_data(cls, instance: Encounter):
        patient_data = patient_utils.PatientSummary(**instance.patient).to_report_dict()
        return patient_data

    @classmethod
    def initialize(cls, instance: Encounter) -> "EncounterReportStruct":
        data = {
            "encounter_id": instance.encounter_id,
            "encounter_type": instance.encounter_type,
            "provider": cls._get_provider_details(instance),
            "status": instance.status.upper(),
            "diagnosis": cls._get_diagnosis(instance),
            "created_at": instance.created_datetime.strftime("%Y-%m-%dT%H:%M:%SZ"),
            **cls._get_patient_data(instance),
            **cls._get_log_data(instance),
            **cls._get_acknowledger_details(instance),
            **cls._get_signer_details(instance),
            **cls._get_clinic_details(instance),
        }
        return cls(**data)

    def to_response_struct(self):
        data = self.dict().copy()
        data = utils.to_response_struct(data)
        return OrderedDict(data)

    def to_report_struct(self):
        return utils.to_report_structure(self.dict())
