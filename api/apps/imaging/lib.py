from typing import List
from . import models
from api.utils.lib import AuditEvent, AuditLog


class ImagingObservationAndOrder:
    def __init__(
        self,
        img_order_id: str,
        img_obvs: List[models.ImagingObservation],
        user_data: dict,
        audit_fields: dict,
        payment_scheme,
    ):
        self.img_order_id = img_order_id
        self.user_data = user_data
        self.audit_fields = audit_fields
        self.img_obvs = img_obvs
        self.payment_scheme = payment_scheme

    def __clean_imaging_obv_record(self, img_obv_record: dict) -> dict:
        """Cleans an imaging observation record"""
        img_obv_record.pop("audit_log", None)
        img_obv_record.pop("created_at", None)
        return img_obv_record

    def create_img_obv_order(
        self, img_obv: models.ImagingObservation
    ) -> models.ImagingObservationOrder:
        """Creates an imaging observation order"""
        img_order_instance = models.ImagingOrder.objects.get(id=self.img_order_id)

        patient_data = img_order_instance.patient
        img_obv_data: dict = img_obv.to_dict()
        img_obv_data = self.__clean_imaging_obv_record(img_obv_data)
        audit_records = [
            AuditLog(
                user=self.user_data, event=AuditEvent.CREATE, fields=self.audit_fields
            ).dict()
        ]

        img_obv_order: models.ImagingObservationOrder = models.ImagingObservationOrder(
            patient=patient_data,
            img_order=img_order_instance,
            img_obv=img_obv_data,
            status="NEW",
            audit_log=audit_records,
        )
        img_obv_order._payment_scheme = self.payment_scheme
        img_obv_order._bill_item_code = img_obv.bill_item_code
        img_obv_order._quantity = 1
        img_obv_order._name = img_obv.name
        img_obv_order.save()
        return img_obv_order

    def populate_img_obv_orders(self):
        """Populates imaging observation orders"""
        results = [self.create_img_obv_order(img_obv) for img_obv in self.img_obvs]
        return results
