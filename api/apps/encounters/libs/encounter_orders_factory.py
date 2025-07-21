import json, uuid
from typing import List, OrderedDict, Union, TypedDict, Optional

from pydantic import BaseModel
from rest_framework.request import Request
from django.utils import timezone
from django.db import transaction
from django.core.serializers.json import DjangoJSONEncoder

from api.apps.laboratory import serializers as lab_serializers
from api.apps.imaging import serializers as img_serializers
from api.apps.pharmacy import serializers as pharm_serializers
from api.apps.nursing import serializers as nursing_serializers
from api.apps.encounters import models
from api.includes import exceptions, utils

############## SCHEMAS ###################


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


class ImgObservation(BaseModel):
    id: int
    name: str


class ImgObvOrder(BaseModel):
    id: int
    img_obv: ImgObservation


class ImgOrderResponseData(BaseModel):
    id: int
    img_id: str
    img_obv_orders: List[ImgObvOrder]


class Store(BaseModel):
    id: int
    name: str
    type: str
    is_pharmacy: bool


class PrescOrderResponseData(BaseModel):
    id: int
    prc_id: str
    source: str
    store: Store
    details: Union[dict, list]


class NursingOrderResponseData(BaseModel):
    id: int
    order_id: str
    station: dict


class EncounterOrderStruct(BaseModel):
    id: str = str(uuid.uuid4())
    type: models.EncounterOrderChoices
    value: Union[dict, str]
    created_at: str = timezone.now().isoformat()
    created_by: dict


class EncounterServicesOrderReturnDict(TypedDict):
    laboratory: Optional[dict]
    imaging: Optional[dict]
    prescription: Optional[dict]
    nursing: Optional[dict]


################## Operations #########################
class EncounterServicesOrderFactory:
    """Serves a factory for ordering other services from encounters"""

    def __init__(
        self,
        encounter: models.Encounter,
        request: Request,
        lab_order_data: OrderedDict = None,
        img_order_data: OrderedDict = None,
        presc_order_data: OrderedDict = None,
        nursing_order_data: OrderedDict = None,
    ):
        self.encounter = encounter
        self.request = request
        self.lab_order_data = lab_order_data
        self.img_order_data = img_order_data
        self.presc_order_data = presc_order_data
        self.nursing_order_data = nursing_order_data
        self._validate_init()  # validate data on initialization

        self._lab_serializer = lab_serializers.LabOrderSerializer
        self._imaging_serializer = img_serializers.ImagingOrderSerializer
        self._prescription_serializer = pharm_serializers.PrescriptionSerializer
        self._nursing_serializer = nursing_serializers.NursingOrderSerializer
        self._serializer_context = {"request": self.request}

    def _validate_init(self):
        if (
            not self.lab_order_data
            and not self.img_order_data
            and not self.presc_order_data
            and not self.nursing_order_data
        ):
            raise exceptions.BadRequest("No service is added for ordering")

    def __clean_lab_order_data(self, data) -> LabOrderResponseData:
        """Normalize lab order result

        Args:
            data (dict): data retrieved after lab has been ordered

        Returns:
            LabOrderResponseData: instance of LabOrderResponseData
        """
        cleaned_data = {
            "id": data["id"],
            "asn": data["asn"],
            "service_center": data["service_center"],
            "lab_panel_orders": [
                {
                    "id": record["id"],
                    "panel": {
                        "id": record["panel"]["id"],
                        "name": record["panel"]["name"],
                    },
                }
                for record in data["lab_panel_orders"]
            ],
        }
        return LabOrderResponseData(**cleaned_data)

    def __clean_img_order_data(self, data) -> ImgOrderResponseData:
        """Normalize imaging order result

        Args:
            data (dict): data retrieved after imaging has been ordered

        Returns:
            ImgOrderResponseData: instance of ImgOrderResponse data
        """
        cleaned_data = {
            "id": data["id"],
            "img_id": data["img_id"],
            "img_obv_orders": [
                {
                    "id": record["id"],
                    "img_obv": {
                        "id": record["img_obv"]["id"],
                        "name": record["img_obv"]["name"],
                    },
                }
                for record in data["img_obv_orders"]
            ],
        }
        return ImgOrderResponseData(**cleaned_data)

    def __clean_presc_order_data(self, data) -> PrescOrderResponseData:
        """Normalize Prescription Order result

        Args:
            data (dict): data retrieved after prescription is ordered

        Returns:
            PrescOrderResponseData:  instance of PrescriptionOrderData
        """
        cleaned_data = {
            "id": data.get("id"),
            "prc_id": data.get("prc_id"),
            "source": data.get("source"),
            "store": data.get("store"),
            "details": data.get("details", []),
        }
        return PrescOrderResponseData(**cleaned_data)

    def __clean_nursing_order_data(self, data: dict) -> NursingOrderResponseData:
        """Normalize Nursing Order data

        Args:
            data (dict): data retrieved after nursing order is ordered

        Returns:
            NursingOrderResponseData: instance of NursingOrderData
        """
        cleaned_data = {
            "id": data.get("id"),
            "order_id": data.get("order_id"),
            "station": data.get("station"),
        }
        return NursingOrderResponseData(**cleaned_data)

    def _order_lab(self):
        if self.lab_order_data:
            self.lab_order_data: dict = json.loads(json.dumps(self.lab_order_data))
            self.lab_order_data["patient"] = self.encounter.patient
            order_data = self._lab_serializer(
                data=self.lab_order_data, context=self._serializer_context
            )
            order_data.is_valid(raise_exception=True)
            order_data.save()
            ordered_lab = self.__clean_lab_order_data(order_data.data)
            user_data = utils.trim_user_data(utils.model_to_dict(self.request.user))
            enc_order_struct = EncounterOrderStruct(
                type=models.EncounterOrderChoices.LABORATORY,
                value=json.loads(json.dumps(ordered_lab.dict(), cls=DjangoJSONEncoder)),
                created_by=user_data,
            )
            self.encounter.orders.append(enc_order_struct.dict())
            return ordered_lab.dict()

    def _order_imaging(self):
        if self.img_order_data:
            self.img_order_data: dict = json.loads(json.dumps(self.img_order_data))
            self.img_order_data["patient"] = self.encounter.patient
            order_data = self._imaging_serializer(
                data=self.img_order_data, context=self._serializer_context
            )
            order_data.is_valid(raise_exception=True)
            order_data.save()
            ordered_img = self.__clean_img_order_data(order_data.data)
            user_data = utils.trim_user_data(utils.model_to_dict(self.request.user))
            enc_order_struct = EncounterOrderStruct(
                type=models.EncounterOrderChoices.IMAGING,
                value=ordered_img.dict(),
                created_by=user_data,
            )
            self.encounter.orders.append(enc_order_struct.dict())
            return ordered_img.dict()
        return None

    def _order_prescriptions(self):
        if self.presc_order_data:
            self.presc_order_data: dict = json.loads(json.dumps(self.presc_order_data))
            self.presc_order_data["patient"] = self.encounter.patient
            order_data = self._prescription_serializer(
                data=self.presc_order_data, context=self._serializer_context
            )
            order_data.is_valid(raise_exception=True)
            order_data.save()
            ordered_presc = self.__clean_presc_order_data(order_data.data)
            user_data = utils.trim_user_data(utils.model_to_dict(self.request.user))
            enc_order_struct = EncounterOrderStruct(
                type=models.EncounterOrderChoices.PRESCRIPTION,
                value=json.loads(
                    json.dumps(ordered_presc.dict(), cls=DjangoJSONEncoder)
                ),
                created_by=user_data,
            )
            self.encounter.orders.append(enc_order_struct.dict())
            return ordered_presc.dict()

    def _order_nursing(self):
        if self.nursing_order_data:
            self.nursing_order_data: dict = json.loads(
                json.dumps(self.nursing_order_data)
            )
            self.nursing_order_data["patient"] = self.encounter.patient
            order_data = self._nursing_serializer(
                data=self.nursing_order_data, context=self._serializer_context
            )
            order_data.is_valid(raise_exception=True)
            order_data.save()
            ordered_nursing = self.__clean_nursing_order_data(order_data.data)
            user_data = utils.trim_user_data(utils.model_to_dict(self.request.user))
            enc_order_struct = EncounterOrderStruct(
                type=models.EncounterOrderChoices.NURSING,
                value=json.loads(
                    json.dumps(ordered_nursing.dict(), cls=DjangoJSONEncoder)
                ),
                created_by=user_data,
            )
            self.encounter.orders.append(enc_order_struct.dict())
            return ordered_nursing.dict()

    @transaction.atomic
    def order_services(self) -> dict:
        """Orders all services set down to be ordered

        Returns:
            Encounter: object of saved encounter
        """
        lab_order = self._order_lab()
        img_order = self._order_imaging()
        prc_order = self._order_prescriptions()
        nursing_order = self._order_nursing()
        self.encounter.save()
        return EncounterServicesOrderReturnDict(
            laboratory=lab_order or None,
            imaging=img_order or None,
            prescription=prc_order or None,
            nursing=nursing_order or None,
        )
