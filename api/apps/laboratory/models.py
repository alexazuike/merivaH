from django.db import models
import datetime
from django.forms.models import model_to_dict

from config import preferences
from api.includes import mail_utils, utils, exceptions
from . import utils as lab_utils


DEFAULT_LAB_PANEL_TEMPLATE = lab_utils.get_default_lab_panel_template()


def generate_asn_lab_order():
    """Function generates ASN for lab order
    Uses present datetime and month as prefix
    Restarts counter for each month
    """
    serial_no = 1
    config = preferences.AppPreferences()
    if utils.is_table_exist("laboratory_laborder"):
        CURRENT_YEAR = str(datetime.datetime.utcnow().year)[2::]
        CURRENT_MONTH = str(datetime.datetime.utcnow().month).zfill(2)

        lab_orders = LabOrder.objects.filter(
            asn__contains=f"{CURRENT_YEAR}{CURRENT_MONTH}"
        )
        if lab_orders.count() > 0:
            last_lab_order = lab_orders.latest("id")
            serial_no = int(last_lab_order.asn[-6:]) + 1

    serial_no = str(serial_no).zfill(6)
    unique_id = f"{config.lab_id_prefix_code}{CURRENT_YEAR}{CURRENT_MONTH}{serial_no}"
    return unique_id


class ServiceCenter(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class LabObservation(models.Model):
    name = models.CharField(max_length=256)
    uom = models.CharField(max_length=256)
    reference_range = models.JSONField()
    type = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def to_dict(self):
        return model_to_dict(self)


class LabUnit(models.Model):
    name = models.CharField(max_length=256)
    order_no = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class LabSpecimen(models.Model):
    name = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.asn


class LabSpecimenType(models.Model):
    name = models.CharField(max_length=256)
    color = models.CharField(max_length=256)
    description = models.TextField()
    status = models.BooleanField(default=True)
    specimen = models.ForeignKey(
        LabSpecimen, null=True, blank=True, default=None, on_delete=models.DO_NOTHING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def to_dict(self):
        return model_to_dict(self)


class LabPanel(models.Model):
    name = models.CharField(max_length=256)
    obv = models.JSONField()
    active = models.BooleanField(default=True)
    specimen_type = models.ForeignKey(
        LabSpecimenType, on_delete=models.CASCADE, default=None
    )
    lab_unit = models.ForeignKey(LabUnit, on_delete=models.CASCADE, default=None)
    status = models.CharField(max_length=256, null=True, blank=True)
    bill_item_code = models.CharField(max_length=256, null=True, blank=True)
    audit_log = models.JSONField(default=list, blank=True, null=True)
    template = models.TextField(
        default=DEFAULT_LAB_PANEL_TEMPLATE, blank=False, null=False
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def to_dict(self):
        panel_dict = model_to_dict(self)
        panel_dict["specimen_type"] = model_to_dict(self.specimen_type)
        panel_dict["specimen"] = (
            model_to_dict(self.specimen_type.specimen)
            if self.specimen_type.specimen
            else {}
        )
        panel_dict["lab_unit"] = model_to_dict(self.lab_unit)
        return panel_dict


class LabOrder(models.Model):
    patient = models.JSONField(default=dict)
    asn = models.CharField(
        unique=True, default=generate_asn_lab_order, editable=False, max_length=80
    )
    stat = models.BooleanField(default=False)
    service_center = models.JSONField(null=False, blank=False)
    referral_facility = models.JSONField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    lab_panels = models.JSONField(default=list, blank=False, null=False)
    lab_panel_orders = models.JSONField(default=list, blank=False, null=False)
    ordered_by = models.JSONField(default=dict)
    ordered_datetime = models.DateTimeField(auto_now_add=True)
    ordering_physician = models.CharField(max_length=256, null=True, blank=True)
    doc_path = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return self.asn

    def mail_lab_result(self):
        """Function sends mail to patient for lab result"""
        from api.apps.laboratory.libs import LabResultGenerator

        try:
            result_generator = LabResultGenerator(
                lab_order=self.lab_order,
                header=preferences.AppPreferences().use_lab_mail_header,
            )
            file_object = result_generator.render_template_to_pdf()
            if self.patient.get("email"):
                email_utils = mail_utils.EmailUtil(
                    subject="Lab Results",
                    body="Hello!!\nThis mail contains a report of your lab report",
                    receiver_mail=self.patient.get("email"),
                    attachment=file_object,
                    file_name="lab_report.pdf",
                )
                email_utils.send_mail()
        except Exception as e:
            print(e)


class LabPanelOrder(models.Model):
    patient = models.JSONField(default=dict)
    lab_order = models.ForeignKey(LabOrder, on_delete=models.CASCADE)
    panel = models.JSONField(default=dict)
    panel_struct = models.JSONField(default=dict)
    status = models.CharField(max_length=256, blank=False, null=True)  # enum
    audit_log = models.JSONField(default=list)  # array of json field
    bill = models.CharField(max_length=256, null=True, blank=True)
    bill_package_usage = models.CharField(max_length=256, null=True, blank=True)
    is_result_sent = models.BooleanField(default=False)
    approved_by = models.JSONField(default=dict)
    approved_on = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ("take_specimen", "Can take specimen"),
            ("recieve_specimen", "Can receive specimen"),
            ("fill_result", "Can fill result"),
            ("submit_result", "Can submit result"),
            ("approve_reject_result", "Can approve or reject result"),
            ("send_print_result", "Can send or print result"),
        )

    def __str__(self):
        return self.lab_order.asn

    def _validate_bill_package(self):
        """Validates both bill and bill_package"""
        entities = (self.bill, self.bill_package_usage)
        if len(list(filter(bool, (entities)))) not in (0, 1):
            raise exceptions.ServerError(
                "Either bill or bill package should have a value not both"
            )

    def save(self, *args, **kwargs) -> None:
        self._validate_bill_package()
        return super().save(*args, **kwargs)

    def post_payment_action(self, bill):
        ...

    def mail_lab_result(self):
        """Function sends mail to patient for lab result"""
        from api.apps.laboratory.libs import LabResultGenerator

        try:
            result_generator = LabResultGenerator(
                lab_order=self.lab_order,
                lab_panel_orders=(self,),
                header=preferences.AppPreferences().use_lab_mail_header,
            )
            file_object = result_generator.render_template_to_pdf()
            if self.patient.get("email"):
                email_utils = mail_utils.EmailUtil(
                    subject="Lab Results",
                    body="Hello!!\nThis mail contains a report of your lab report",
                    receiver_mail=self.patient.get("email"),
                    attachment=file_object,
                    file_name="lab_report.pdf",
                )
                email_utils.send_mail()
        except Exception as e:
            print(e)
