import pytz
from typing import Optional
from datetime import datetime

from dateutil.relativedelta import relativedelta
from dateutil import parser
from django.template.loader import render_to_string
from django.template import Template, Context

from api.apps.pharmacy import models
from api.includes import file_utils, utils
from config.preferences import AppPreferences


class PrescriptionResultGenerator:
    def __init__(self, prescription: models.Prescription, use_header: bool = False):
        self.prescription = prescription
        self.use_header = use_header

    def _inject_patient_age(self):
        time_difference = relativedelta(
            self.prescription.confirmed_at.replace(tzinfo=pytz.utc),
            parser.parse(self.prescription.patient.get("date_of_birth")).replace(
                tzinfo=pytz.utc
            ),
        )
        self.prescription.patient["age"] = time_difference.years

    def _get_context_data(self):
        self._inject_patient_age()
        prescription_data: dict = utils.model_to_dict(self.prescription)
        prescription_data["confirmed_at"] = self.prescription.confirmed_at
        prescription_data = utils.format_template_context(prescription_data)
        context = Context(prescription_data)
        return context

    def _render_header(self) -> Optional[str]:
        header_str = file_utils.FileUtils().read_header()
        if self.use_header and header_str:
            return header_str
        return None

    def _render_html(self, template_str: str):
        template = Template(template_str)
        context = self._get_context_data()
        return template.render(context=context)

    def render_to_html(self) -> str:
        render_context = {
            "header": self._render_header(),
            "body": self._render_html(AppPreferences().prescription_body),
            "footer": self._render_html(AppPreferences().prescription_footer),
            "company_theme_color": AppPreferences().company_theme_color,
            "text_color": AppPreferences().text_color,
            "font_size": AppPreferences().font_size,
        }
        html_content = render_to_string("prescription_main.html", render_context)
        return html_content

    def render_to_pdf(self) -> bytes:
        template_str = self.render_to_html()
        header_html = self._render_header()
        pdf_object = file_utils.FileUtils().convert_html_to_pdf(
            template_str, header_html
        )
        return pdf_object
