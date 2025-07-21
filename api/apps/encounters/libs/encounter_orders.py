import json
from enum import Enum
from typing import List
from pydantic import BaseModel

from api.apps.laboratory import serializers as lab_serializers
from api.apps.imaging import serializers as img_serializers
from api.apps.pharmacy import serializers as pharm_serializers
from api.apps.encounters import models


class EncounterServices(str, Enum):
    LABORATORY = "LABORATORY"
    IMAGING = "IMAGING"
    PRESCRIPTION = "PRESCRPTION"


class ServiceCenter(BaseModel):
    id: int
    name: str


class LabPanel(BaseModel):
    id: int
    name: str


class LabPanelOrder(BaseModel):
    id: int
    panel: LabPanel


class LabOrderResponseData(BaseModel):
    id: int
    asn: str
    service_center: ServiceCenter
    lab_panel_orders: List[LabPanelOrder]


class EncounterServicesFactory:
    """Serves a factory for ordering other services from encounters"""

    def __init__(self, encounter: models.Encounter):
        self.encounter = encounter

    def __clean_lab_order_data(self) -> LabOrderResponseData:
        ...

    def __clean_img_order_data(self) -> dict:
        ...

    def __clean_pharm_order_data(self) -> dict:
        ...

    def order_services(self):
        ...
