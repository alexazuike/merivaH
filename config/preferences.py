import base64
from enum import Enum
from typing import Tuple, Union, Optional
from django.template.loader import render_to_string

from django.conf import settings
from decouple import config as env_vars
from pydantic import BaseModel
from django.db import models

from api.includes.templates import TemplatePathReader


class AppPreferencesDataTypes(models.TextChoices):
    INT = "int"
    STR = "str"
    BOOL = "bool"
    FLOAT = "float"

    @classmethod
    def get_type(cls, value: str):
        for type in cls:
            if type.value == value:
                return (
                    str
                    if type == AppPreferencesDataTypes.STR
                    else int
                    if type == AppPreferencesDataTypes.INT
                    else bool
                    if type == AppPreferencesDataTypes.BOOL
                    else float
                )

    def to_type(self):
        return (
            str
            if self == AppPreferencesDataTypes.STR
            else int
            if self == AppPreferencesDataTypes.INT
            else bool
            if self == AppPreferencesDataTypes.BOOL
            else float
        )


class AppPrefenrencesCategories(models.TextChoices):
    GENERAL = "GENERAL"
    PATIENT = "PATIENT"
    FINANCE = "FINANCE"
    ENCOUNTER = "ENCOUNTER"
    LABORATORY = "LABORATORY"
    IMAGING = "IMAGING"
    INVENTORY = "INVENTORY"
    PHARMACY = "PHARMACY"
    NURSING = "NURSING"
    REPORTS = "REPORTS"


class PreferencesStruct(BaseModel):
    name: str
    type: AppPreferencesDataTypes
    default: Union[str, bool, int, float] = None
    category: AppPrefenrencesCategories = AppPrefenrencesCategories.GENERAL
    env: bool = False

    def to_dict(self) -> dict:
        resp_dict = self.dict(exclude={"name", "default", "env"})
        resp_dict["value"] = self.default
        return resp_dict


APP_PREFERENCES: Tuple[PreferencesStruct] = (
    # GENERAL CONFIGURATIONS
    PreferencesStruct(
        name="company_name", type=AppPreferencesDataTypes.STR, default="HealthApp"
    ),
    PreferencesStruct(
        name="company_mail",
        type=AppPreferencesDataTypes.STR,
        default="HealthApp@mail.com",
    ),
    PreferencesStruct(
        name="company_phone", type=AppPreferencesDataTypes.STR, default="08123456789"
    ),
    PreferencesStruct(
        name="company_website",
        type=AppPreferencesDataTypes.STR,
        default="www.healthapp.com",
    ),
    PreferencesStruct(
        name="company_address",
        type=AppPreferencesDataTypes.STR,
        default="Zone 5, Abuja",
    ),
    PreferencesStruct(
        name="company_timezone",
        type=AppPreferencesDataTypes.STR,
        default="Africa/Lagos",
    ),
    PreferencesStruct(
        name="company_dateformat",
        type=AppPreferencesDataTypes.STR,
        default="%Y-%m-%d %I:%M %p",
    ),
    # REPORTS STRUCTURE
    PreferencesStruct(
        name="company_theme_color",
        type=AppPreferencesDataTypes.STR,
        category=AppPrefenrencesCategories.REPORTS,
        default="white",
    ),
    PreferencesStruct(
        name="text_color",
        type=AppPreferencesDataTypes.STR,
        category=AppPrefenrencesCategories.REPORTS,
        default="black",
    ),
    PreferencesStruct(
        name="font_size",
        type=AppPreferencesDataTypes.STR,
        category=AppPrefenrencesCategories.REPORTS,
        default="14",
    ),
    PreferencesStruct(
        name="prescription_body",
        type=AppPreferencesDataTypes.STR,
        category=AppPrefenrencesCategories.REPORTS,
        default=TemplatePathReader.read_prescription_body(),
    ),
    PreferencesStruct(
        name="prescription_footer",
        type=AppPreferencesDataTypes.STR,
        category=AppPrefenrencesCategories.REPORTS,
        default=TemplatePathReader.read_prescription_footer(),
    ),
    # ENV CONFIGURATIONS
    PreferencesStruct(name="mail_api_key", type=AppPreferencesDataTypes.STR, env=True),
    PreferencesStruct(
        name="mail_provider_base_url",
        type=AppPreferencesDataTypes.STR,
        default="https://api.mailgun.net",
        env=True,
    ),
    PreferencesStruct(name="mail_domain", type=AppPreferencesDataTypes.STR, env=True),
    PreferencesStruct(name="admin_mail", type=AppPreferencesDataTypes.STR),
    # ENCOUNTER CONFIGURATIONS
    PreferencesStruct(
        name="encounter_module_code",
        type=AppPreferencesDataTypes.STR,
        default="ENC",
        category=AppPrefenrencesCategories.ENCOUNTER,
    ),
    PreferencesStruct(
        name="encounter_id_prefix_code",
        type=AppPreferencesDataTypes.STR,
        default="ENC",
        category=AppPrefenrencesCategories.ENCOUNTER,
    ),
    # LABORATORY CONFIGURATIONS
    PreferencesStruct(
        name="lab_module_code",
        type=AppPreferencesDataTypes.STR,
        default="LAB",
        category=AppPrefenrencesCategories.LABORATORY,
    ),
    PreferencesStruct(
        name="lab_id_prefix_code",
        type=AppPreferencesDataTypes.STR,
        default="ASN",
        category=AppPrefenrencesCategories.LABORATORY,
    ),
    PreferencesStruct(
        name="use_lab_report_header",
        type=AppPreferencesDataTypes.BOOL,
        default=False,
        category=AppPrefenrencesCategories.LABORATORY,
    ),
    PreferencesStruct(
        name="use_lab_mail_header",
        type=AppPreferencesDataTypes.STR,
        default=False,
        category=AppPrefenrencesCategories.LABORATORY,
    ),
    # IMAGING CONFIGURATIONS
    PreferencesStruct(
        name="imaging_module_code",
        type=AppPreferencesDataTypes.STR,
        default="IMG",
        category=AppPrefenrencesCategories.IMAGING,
    ),
    PreferencesStruct(
        name="imaging_id_prefix_code",
        type=AppPreferencesDataTypes.STR,
        default="RAD",
        category=AppPrefenrencesCategories.IMAGING,
    ),
    PreferencesStruct(
        name="use_img_report_header",
        type=AppPreferencesDataTypes.BOOL,
        default=False,
        category=AppPrefenrencesCategories.IMAGING,
    ),
    PreferencesStruct(
        name="use_img_mail_header",
        type=AppPreferencesDataTypes.BOOL,
        default=False,
        category=AppPrefenrencesCategories.IMAGING,
    ),
    # PATIENT CONFIG
    PreferencesStruct(
        name="patient_prefix_code",
        type=AppPreferencesDataTypes.STR,
        default="UHID",
        category=AppPrefenrencesCategories.PATIENT,
    ),
    # FINANCE CONFIG
    PreferencesStruct(
        name="billing_enabled",
        type=AppPreferencesDataTypes.BOOL,
        default=True,
        category=AppPrefenrencesCategories.FINANCE,
    ),
    PreferencesStruct(
        name="bill_id_prefix_code",
        type=AppPreferencesDataTypes.STR,
        default="BIL",
        category=AppPrefenrencesCategories.FINANCE,
    ),
    PreferencesStruct(
        name="invoice_id_prefix_code",
        type=AppPreferencesDataTypes.STR,
        default="INVC",
        category=AppPrefenrencesCategories.FINANCE,
    ),
    PreferencesStruct(
        name="finance_module_code",
        type=AppPreferencesDataTypes.STR,
        default="FIN",
        category=AppPrefenrencesCategories.FINANCE,
    ),
    PreferencesStruct(
        name="cashbook_id_prefix_code",
        type=AppPreferencesDataTypes.STR,
        default="CSB",
        category=AppPrefenrencesCategories.FINANCE,
    ),
    PreferencesStruct(
        name="bill_package_id_prefix_code",
        type=AppPreferencesDataTypes.STR,
        default="BILPKG",
        category=AppPrefenrencesCategories.FINANCE,
    ),
    # INVENTORY CONFIG
    PreferencesStruct(
        name="inventory_module_code",
        type=AppPreferencesDataTypes.STR,
        default="INVT",
        category=AppPrefenrencesCategories.INVENTORY,
    ),
    PreferencesStruct(
        name="inventory_enabled",
        type=AppPreferencesDataTypes.BOOL,
        default=True,
        category=AppPrefenrencesCategories.INVENTORY,
    ),
    # PHARMACY CONFIGURATIONS
    PreferencesStruct(
        name="pharamcy_module_code",
        type=AppPreferencesDataTypes.STR,
        default="PHARM",
        category=AppPrefenrencesCategories.PHARMACY,
    ),
    PreferencesStruct(
        name="prescription_id_prefix_code",
        type=AppPreferencesDataTypes.STR,
        default="RX",
        category=AppPrefenrencesCategories.PHARMACY,
    ),
    PreferencesStruct(
        name="use_presc_report_header",
        type=AppPreferencesDataTypes.BOOL,
        default=False,
        category=AppPrefenrencesCategories.PHARMACY,
    ),
    PreferencesStruct(
        name="use_presc_mail_header",
        type=AppPreferencesDataTypes.BOOL,
        default=False,
        category=AppPrefenrencesCategories.PHARMACY,
    ),
    # NURSING CONFIGURATIONS
    PreferencesStruct(
        name="nursing_module_code",
        type=AppPreferencesDataTypes.STR,
        default="NURS",
        category=AppPrefenrencesCategories.NURSING,
    ),
    PreferencesStruct(
        name="nursing_task_id_prefix_code",
        type=AppPreferencesDataTypes.STR,
        default="NST",
        category=AppPrefenrencesCategories.NURSING,
    ),
    PreferencesStruct(
        name="nursing_task_activity_id_prefix_code",
        type=AppPreferencesDataTypes.STR,
        default="NSTA",
        category=AppPrefenrencesCategories.NURSING,
    ),
)


class AppPreferences:
    def __getattribute__(self, name):
        config_prop = next(
            (prop for prop in APP_PREFERENCES if prop.name == name), None
        )
        if config_prop:
            if config_prop.env:
                return env_vars(
                    config_prop.name,
                    default=config_prop.default,
                    cast=AppPreferencesDataTypes.get_type(config_prop.type.value),
                )
            return self._get_create_app_preferences(config_prop)
        return super(AppPreferences, self).__getattribute__(name)

    @property
    def company_logo(self):
        ...

    def _get_create_app_preferences(self, config_struct: PreferencesStruct):
        from api.apps.core.models import AppPreferences as preferences_model

        title = config_struct.name.upper().replace("_", " ")
        preferences, created = preferences_model.objects.get_or_create(
            title=title,
            category=config_struct.category,
            defaults=config_struct.to_dict(),
        )
        data_type = AppPreferencesDataTypes.get_type(preferences.type)
        return data_type(preferences.value)
