from typing import List

from api.includes.utils import AuditEvent, AuditLog
from api.apps.patient import models as patient_models
from api.apps.laboratory import models as lab_models


class LabPanelsAndOrders:
    def __init__(
        self,
        lab_order_id: str,
        lab_panels: List[lab_models.LabPanel],
        user_data: dict,
        audit_fields: dict,
        payment_scheme,
    ):
        self.lab_order_id = lab_order_id
        self.user_data = user_data
        self.audit_fields = audit_fields
        self.lab_panels = lab_panels
        self.payment_scheme = payment_scheme

    def clean_lab_panel_data(self, lab_panel: dict) -> dict:
        """
        Clean up data entering in lab_panel
        """

        lab_panel.pop("active")
        lab_panel.pop("created_at", None)
        lab_panel["specimen_type"].pop("id")
        lab_panel["specimen_type"].pop("status")
        lab_panel["specimen_type"].pop("created_at", None)

        modified_observations = []
        for obv in lab_panel["obv"]:
            obv.pop("created_at", None)
            modified_observations.append(obv)

        lab_panel["obv"] = modified_observations
        return lab_panel

    def create_lab_panel_order(self, panel: lab_models.LabPanel):
        """
        Creates a lab panel order
        """
        lab_order_instance = lab_models.LabOrder.objects.get(id=self.lab_order_id)

        # get patient details
        patient_instance: "patient_models.Patient" = patient_models.Patient.objects.get(
            id=lab_order_instance.patient.get("id")
        )
        patient_data = patient_instance.to_dict()
        observations = panel.obv
        obv_ids = [obv["id"] for obv in observations] if observations else []

        observations = []
        for id in obv_ids:
            try:
                observation: lab_models.LabObservation = (
                    lab_models.LabObservation.objects.get(id=id)
                )
                observation = observation.to_dict()
                observations.append(observation)
            except lab_models.LabObservation.DoesNotExist:
                continue

        panel.obv = observations
        panel_data = panel.to_dict()
        panel_data = self.clean_lab_panel_data(panel_data)

        audit_records = [
            AuditLog(
                user=self.user_data, event=AuditEvent.CREATE, fields=self.audit_fields
            ).dict()
        ]

        lab_order_panel: lab_models.LabPanelOrder = lab_models.LabPanelOrder(
            patient=patient_data,
            lab_order=lab_order_instance,
            status="NEW",
            panel=panel_data,
            audit_log=audit_records,
        )
        lab_order_panel._payment_scheme = self.payment_scheme
        lab_order_panel._bill_item_code = panel.bill_item_code
        lab_order_panel._quantity = 1
        lab_order_panel._name = panel.name
        lab_order_panel.save()
        return lab_order_panel

    def populate_lab_panel_orders(self):
        """
        Populates lab panel orders for a lab order
        """
        results = [
            self.create_lab_panel_order(panel)
            for panel in self.lab_panels
            if panel is not None
        ]
        return results
