import os
from enum import Enum
from typing import Type

from django.conf import settings
from django.contrib.auth.models import User

from api.includes import utils


class LabPanelOrderStatus(str, Enum):
    NEW = "NEW"
    TAKE_SPECIMEN = "TAKE SPECIMEN"
    RECIEVE_SPECIMEN = "RECIEVE SPECIMEN"
    FILL_RESULT = "FILL RESULT"
    AWAITING_APPROVAL = "AWAITING APPROVAL"
    APPROVED = "APPROVED"
    CANCELLED = "CANCELLED"

    def __str__(self):
        return self.value


def has_panel_order_status_perm(
    user: User, status: str, instance: Type[utils.DJANGO_MODEL]
) -> bool:

    """Checks if a user has permission to perform a certain action
    on a lab panel order

    Args:
        user (User): The user to check permissions for
        status (str): The status to check permissions for
        instance (LabPanelOrder): The lab panel order to check permissions for

    Returns:
        bool: True if the user has permission, False otherwise
    """
    if status.casefold() == str(LabPanelOrderStatus.TAKE_SPECIMEN).casefold():
        return user.has_perm("laboratory.take_specimen") or user.has_perm(
            "laboratory.change_labpanelorder"
        )
    if status.casefold() == str(LabPanelOrderStatus.RECIEVE_SPECIMEN).casefold():
        return user.has_perm("laboratory.recieve_specimen") or user.has_perm(
            "laboratory.change_labpanelorder"
        )
    if (
        status.casefold() == str(LabPanelOrderStatus.FILL_RESULT).casefold()
        and instance.status.casefold()
        == str(LabPanelOrderStatus.AWAITING_APPROVAL).casefold()
    ):
        return user.has_perm("laboratory.approve_reject_result") or user.has_perm(
            "laboratory.change_labpanelorder"
        )

    if status.casefold() == str(LabPanelOrderStatus.FILL_RESULT).casefold():
        return user.has_perm("laboratory.fill_result") or user.has_perm(
            "laboratory.change_labpanelorder"
        )

    if status.casefold() == str(LabPanelOrderStatus.AWAITING_APPROVAL).casefold():
        return user.has_perm("laboratory.submit_result") or user.has_perm(
            "laboratory.change_labpanelorder"
        )
    if (
        status.casefold() == str(LabPanelOrderStatus.APPROVED).casefold()
        or status.casefold() == str(LabPanelOrderStatus.CANCELLED).casefold()
    ):
        return user.has_perm("laboratory.approve_reject_result") or user.has_perm(
            "laboratory.change_labpanelorder"
        )
    return False


def get_lab_panel_order_data(*panel_orders):
    """
    Get lab panel orders data for a given lab order id.
    """
    panel_order_data = [
        utils.model_to_dict(lab_panel_order) for lab_panel_order in panel_orders
    ]
    return panel_order_data


def get_default_lab_panel_template():
    try:
        file_path = os.path.join(
            settings.BASE_DIR,
            "api",
            "apps",
            "laboratory",
            "templates",
            "default_panel_template.html",
        )
        file = open(file_path)
        content = file.read()
        file.close()
        return content
    except FileNotFoundError:
        return None


def to_panel_report_struct(lab_order_panel: dict):
    panel = lab_order_panel.copy()
    obv_dict = {}
    obvs: list[dict] = panel.get("obv")
    for obv in obvs:
        obv_dict[obv.get("name")] = obv
    panel["obv"] = obv_dict
    return panel
