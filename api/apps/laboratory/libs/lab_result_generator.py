import pytz
from typing import List, Optional, Tuple

from dateutil.relativedelta import relativedelta
from dateutil import parser
from django.template import Context, Template
from django.template.loader import render_to_string

from api.apps.laboratory import models
from api.includes import file_utils, utils
from api.includes import exceptions
from config.preferences import AppPreferences


class LabResultGenerator:
    def __init__(
        self,
        lab_order: models.LabOrder,
        lab_panel_orders: Tuple[models.LabPanelOrder] = tuple(),
        header: bool = False,
    ):
        self.lab_order = lab_order
        self.lab_panel_orders = lab_panel_orders
        self.header = header
        self.lab_order_data: dict = utils.model_to_dict(instance=lab_order)
        self.lab_panel_orders_data: list[dict] = self._get_lab_panel_orders()

    @classmethod
    def extract_panel_order_data(
        cls, lab_order: models.LabOrder, panel_orders: List[models.LabPanelOrder]
    ) -> List[dict]:
        """
        Prepares data for usage as context by extracting out usefull data from other context
        and inserting those data into prepared context data
        """
        panel_order_data = [
            utils.model_to_dict(lab_panel_order) for lab_panel_order in panel_orders
        ]
        for panel_order in panel_order_data:
            panel_order["logs"] = cls._get_logs_data(panel_order.get("audit_log"))
            panel_order["logs_comments"] = cls._get_comments(
                panel_order.get("audit_log")
            )
            panel_order["asn"] = lab_order.asn
            panel_order["company_theme_color"] = AppPreferences().company_theme_color
            panel_order["text_color"] = AppPreferences().text_color
        return panel_order_data

    @classmethod
    def _get_logs_data(cls, audit_log):
        audit_search_params = {
            "recieve specimen": "specimen_taken",
            "fill result": "specimen_recieved",
            "awaiting approval": "result_submitted",
        }
        log_data = utils.extract_audit_log_data(
            audit_log, audit_search_params, with_comments=True, use_datetime=False
        )
        return log_data

    @classmethod
    def _get_comments(cls, audit_log):
        logs = cls._get_logs_data(audit_log)
        comments = [
            value for key, value in logs.items() if str(key).find("_comments") != -1
        ]
        return comments

    def _get_lab_panel_orders(self):
        """Get all panel orders within the available scope

        Returns:
            List[dict]: list of dict represented panel order
        """
        if not self.lab_panel_orders:
            panel_orders = models.LabPanelOrder.objects.filter(
                id__in=self.lab_order.lab_panel_orders
            ).filter(status__iexact="approved")
            if not panel_orders.exists():
                raise exceptions.BadRequest("No approved lab panel orders")
            return self.extract_panel_order_data(self.lab_order, list(panel_orders))
        return self.extract_panel_order_data(self.lab_order, self.lab_panel_orders)

    def _render_panel_template(self, panel_order_data: dict):
        panel_order_data = utils.ContextFormatter(panel_order_data).process()
        template_string = panel_order_data.get("panel", {}).get("template")
        template = Template(template_string)
        context = Context(panel_order_data)
        template_string = template.render(context)
        panel_order_data["panel"]["template"] = template_string
        return panel_order_data

    def _render_panels_template(self):
        self.lab_panel_orders_data = [
            self._render_panel_template(panel_order_data)
            for panel_order_data in self.lab_panel_orders_data
        ]
        return self.lab_panel_orders_data

    def _render_header_to_html(self) -> Optional[str]:
        header_str = file_utils.FileUtils().read_header()
        if self.header and header_str:
            self.lab_order_data["header"] = header_str
            return header_str
        return None

    def render_template_to_html(self) -> str:
        patient_age = None
        if self.lab_order.patient.get("date_of_birth"):
            time_difference = relativedelta(
                self.lab_order.ordered_datetime.replace(tzinfo=pytz.utc),
                parser.parse(self.lab_order.patient.get("date_of_birth")).replace(
                    tzinfo=pytz.utc
                ),
            )
            patient_age = time_difference.years
            self.lab_order_data["patient"]["age"] = patient_age
        self.lab_order_data["header"] = self._render_header_to_html()
        self.lab_order_data["lab_panel_orders"] = self._render_panels_template()
        self.lab_order_data["company"] = utils.get_company_data()
        self.lab_order_data["patient"]["age"] = patient_age
        self.lab_order_data["ordered_datetime"] = utils.to_12_hour_format(
            self.lab_order.ordered_datetime
        )
        self.lab_order_data[
            "company_theme_color"
        ] = AppPreferences().company_theme_color
        self.lab_order_data["text_color"] = AppPreferences().text_color
        self.lab_order_data["font_size"] = AppPreferences().font_size
        lab_order_data = utils.ContextFormatter(
            context_data=self.lab_order_data
        ).process()
        html_content = render_to_string("lab_order_report.html", lab_order_data)
        return html_content

    def render_template_to_pdf(self) -> bytes:
        template_str = self.render_template_to_html()
        header_html = self._render_header_to_html()
        pdf_object = file_utils.FileUtils().convert_html_to_pdf(
            template_str, header_html
        )
        return pdf_object
