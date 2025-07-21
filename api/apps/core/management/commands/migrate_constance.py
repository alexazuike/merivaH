from django.core.management.base import BaseCommand
from typing import List

from config.preferences import AppConfig
from api.apps.core import models
from api.includes import utils


class Command(BaseCommand):
    help = "migrate constance settings to app configuration settings"

    def handle(self, *args, **options):
        configs = AppConfig().dict()
        existing_config = {
            "GENERAL": (
                "COMPANY_NAME",
                "COMPANY_MAIL",
                "COMPANY_PHONE",
                "COMPANY_WEBSITE",
                "COMPANY_ADDRESS",
                "MAIL_PROVIDER_BASE_URL",
                "MAIL_DOMAIN",
                "ADMIN_MAIL",
            ),
            "ENCOUNTER": (
                "ENCOUNTER_MODULE_NAME",
                "ENCOUNTER_MODULE_CODE",
                "ENCOUNTER_ID_PREFIX_CODE",
            ),
            "LABORATORY": (
                "LAB_MODULE_NAME",
                "LAB_MODULE_CODE",
                "LAB_ID_PREFIX_CODE",
                "USE_LAB_REPORT_HEADER",
                "USE_LAB_MAIL_HEADER",
            ),
            "IMAGING": (
                "IMAGING_MODULE_NAME",
                "IMAGING_MODULE_CODE",
                "IMAGING_ID_PREFIX_CODE",
                "USE_IMG_REPORT_HEADER",
                "USE_IMG_MAIL_HEADER",
            ),
            "FINANCE": (
                "BILLING_ENABLED",
                "BILL_ID_PREFIX_CODE",
                "INVOICE_ID_PREFIX_CODE",
                "FINANCE_MODULE_NAME",
                "FINANCE_MODULE_CODE",
                "CASHBOOK_ID_PREFIX_CODE",
            ),
            "PATIENT": ("PATIENT_PREFIX_CODE"),
            "INVENTORY": ("INVENTORY_MODULE_NAME"),
        }

        for key in configs:
            category = next(
                inner_key
                for inner_key in existing_config
                if key.upper() in existing_config[inner_key]
            )
            print(
                str(type(configs[key]))
                .replace("<class ", "")
                .replace(">", "")
                .replace("'", "")
                .strip()
            )
            config_obj = models.AppConfiguration.objects.get_or_create(
                title=key.upper().replace("_", " "),
                type=str(type(configs[key]))
                .replace("<class ", "")
                .replace(">", "")
                .replace("'", "")
                .strip(),
                value=configs[key],
                category=category,
            )
            print(str(config_obj))
