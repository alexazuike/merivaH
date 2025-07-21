from enum import Enum
from typing import List
from django.contrib.auth.models import User
from dateutil.relativedelta import relativedelta
from django.template.loader import render_to_string
from dateutil import parser
from datetime import datetime

from . import models
from api.includes.file_utils import FileUtils
from api.includes import utils as generic_utils


class ImagingObservationOrderStatus(str, Enum):
    NEW = "NEW"
    CAPTURE = "CAPTURED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    CANCELLED = "CANCELLED"

    def __str__(self):
        return self.value


def has_observation_order_status_perm(user: User, status: str) -> bool:
    """Checks if a user has permission to perform a certain action
    on an imaging observation order
    """
    if status.casefold() == str(ImagingObservationOrderStatus.CAPTURE).casefold():
        return user.has_perm("imaging.capture_imaging") or user.has_perm(
            "imaging.change_imagingobservationorder"
        )
    if (
        status.casefold()
        == str(ImagingObservationOrderStatus.AWAITING_APPROVAL).casefold()
    ):
        return user.has_perm("imaging.submit_imaging") or user.has_perm(
            "imaging.change_imagingobservationorder"
        )
    if (
        status.casefold() == str(ImagingObservationOrderStatus.APPROVED).casefold()
        or status.casefold() == str(ImagingObservationOrderStatus.CANCELLED).casefold()
    ):
        return user.has_perm("imaging.approve_reject_imaging") or user.has_perm(
            "imaging.change_imagingobservationorder"
        )
    return False


def get_imaging_obv_order_data(img_order_id: str):
    """Get all ImagingObservationOrder data for a given ImagingOrder id."""
    imaging_obv_orders: List[
        models.ImagingObservationOrder
    ] = models.ImagingObservationOrder.objects.filter(img_order_id=img_order_id)

    obv_order_data = [obv.to_dict() for obv in imaging_obv_orders]

    imaging_order = models.ImagingOrder.objects.get(id=img_order_id)

    for obv_order in obv_order_data:
        del obv_order["audit_log"]
        del obv_order["patient"]
        obv_order["img_id"] = imaging_order.img_id
    return obv_order_data


def generate_img_order_reports(img_order: models.ImagingOrder, header: bool = False):
    """Generate imaging order reports for a given ImagingOrder instance0."""
    img_order_data = img_order.to_dict()
    img_order_data["img_obv_orders"] = get_imaging_obv_order_data(img_order.id)
    time_difference = relativedelta(
        datetime.now(), parser.parse(img_order.patient.get("date_of_birth"))
    )
    patient_age = time_difference.years
    img_order_data["patient"]["age"] = patient_age
    if header:
        header_str = FileUtils().read_header()
        if header_str:
            img_order_data["header"] = header_str
    img_order_data = generic_utils.format_template_context(img_order_data)
    html_content = render_to_string("img_order_report.html", img_order_data)
    pdf_blob = FileUtils().convert_html_to_pdf(html_content)
    return pdf_blob


def generate_img_obv_order_reports(
    img_obv_order: models.ImagingObservationOrder, header: bool = False
):
    """Generate imaging observation order reports for a given ImagingObservationOrder instance."""
    img_order = img_obv_order.img_order
    img_order_data = img_order.to_dict()
    img_obv_orders = [img_obv_order.to_dict()]

    time_difference = relativedelta(
        datetime.now(), parser.parse(img_order.patient.get("date_of_birth"))
    )
    patient_age = time_difference.years
    img_order_data["patient"]["age"] = patient_age
    img_order_data["img_obv_orders"] = img_obv_orders

    if header:
        header_str = FileUtils().read_header()
        if header_str:
            img_order_data["header"] = header_str
    img_order_data = generic_utils.format_template_context(img_order_data)
    html_content = render_to_string("img_order_report.html", img_order_data)
    pdf_blob = FileUtils().convert_html_to_pdf(html_content)
    return pdf_blob
