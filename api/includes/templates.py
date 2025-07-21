import base64
from typing import Optional

from django.conf import settings
from . import constants


class TemplatePathReader:
    @classmethod
    def _read_file(cls, path):
        with open(path, "r") as file:
            return file.read()

    @classmethod
    def read_prescription_body(cls):
        body_path = constants.PRESCRIPTION_BODY_TEMPLATE
        return cls._read_file(body_path)

    @classmethod
    def read_prescription_footer(cls):
        footer_path = constants.PRESCRIPTION_FOOTER_TEMPLATE
        return cls._read_file(footer_path)
