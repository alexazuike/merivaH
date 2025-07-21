from django.db import models
import datetime
from django.forms.models import model_to_dict

from api.apps.finance import models as finance_models
from api.includes import (
    exceptions,
    mail_utils,
    utils,
    file_utils,
    models as generic_models,
)
from config import preferences


def generate_imaging_order_id():
    """Function generates ASN for lab order
    Uses present datetime and month as prefix
    Restarts counter for each month
    """
    serial_no = 1
    config = preferences.AppPreferences()
    if utils.is_table_exist("imaging_imagingorder"):
        CURRENT_YEAR = str(datetime.datetime.utcnow().year)[2::]
        CURRENT_MONTH = str(datetime.datetime.utcnow().month).zfill(2)

        imaging_orders = ImagingOrder.objects.filter(
            img_id__contains=f"{CURRENT_YEAR}{CURRENT_MONTH}"
        )
        if imaging_orders.count() > 0:
            last_img_order = imaging_orders.latest("id")
            serial_no = int(last_img_order.img_id[-6:]) + 1

    serial_no = str(serial_no).zfill(6)
    unique_id = (
        f"{config.imaging_id_prefix_code}{CURRENT_YEAR}{CURRENT_MONTH}{serial_no}"
    )
    return unique_id


def generate_imaging_obv_order_id():
    """Function generates ASN for lab order
    Uses present datetime and month as prefix
    Restarts counter for each month
    """
    serial_no = 1
    config = preferences.AppPreferences()
    if utils.is_table_exist("imaging_imagingobservationorder"):
        CURRENT_YEAR = str(datetime.datetime.utcnow().year)[2::]
        CURRENT_MONTH = str(datetime.datetime.utcnow().month).zfill(2)

        if ImagingObservationOrder.objects.all().count() > 0:
            imaging_observation_orders = ImagingObservationOrder.objects.filter(
                img_id__contains=f"{CURRENT_YEAR}{CURRENT_MONTH}"
            )

            if imaging_observation_orders.count() > 0:
                last_img_obv_order = imaging_observation_orders.latest("id")
                serial_no = int(last_img_obv_order.img_id[-6:]) + 1

    serial_no = str(serial_no).zfill(6)
    unique_id = (
        f"{config.imaging_id_prefix_code}{CURRENT_YEAR}{CURRENT_MONTH}{serial_no}"
    )

    return unique_id


class ServiceCenter(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class Modality(models.Model):
    name = models.CharField(max_length=256)
    order_no = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ImagingObservation(models.Model):
    name = models.CharField(max_length=256)
    active = models.BooleanField(default=True)
    modality = models.ForeignKey(Modality, on_delete=models.CASCADE)
    status = models.CharField(max_length=256, null=True, blank=True)
    audit_log = models.JSONField(default=list, blank=True, null=True)
    bill_item_code = models.CharField(max_length=256, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def to_dict(self):
        img_obv_dict = model_to_dict(self)
        img_obv_dict["modality"] = model_to_dict(self.modality)
        return img_obv_dict


class ImagingOrder(models.Model):
    patient = models.JSONField(default=dict)
    img_id = models.CharField(
        unique=True, max_length=256, default=generate_imaging_order_id
    )
    stat = models.BooleanField(default=False)
    service_center = models.JSONField(null=False, blank=False)
    referral_facility = models.JSONField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    img_obv = models.JSONField(default=list, blank=False, null=False)
    img_obv_orders = models.JSONField(default=list, blank=False, null=False)
    diagnosis = models.JSONField(default=list, blank=False, null=True)
    ordered_by = models.JSONField(default=dict)
    ordered_datetime = models.DateTimeField(auto_now_add=True)
    ordering_physician = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return self.img_id

    def to_dict(self):
        return model_to_dict(self)

    def mail_report(self):
        from . import utils as imaging_utils

        try:
            if self.patient.get("email"):
                file_object = imaging_utils.generate_img_order_reports(
                    img_order=self,
                    header=preferences.AppPreferences().use_img_mail_header,
                )
                email_utils = mail_utils.EmailUtil(
                    subject="Radiology Results",
                    body="Hello!!\n\n This mail contains an attached copy of your radiology result.\n\nRegards,\nRadiology Team",
                    receiver_mail=self.patient.get("email"),
                    attachment=file_object,
                    file_name="imaging_report.pdf",
                )
                email_utils.send_email()
        except Exception as e:
            print(e)
            pass


class ImagingObservationOrder(models.Model):
    patient = models.JSONField(default=dict)
    img_order = models.ForeignKey(ImagingOrder, on_delete=models.CASCADE)
    img_obv = models.JSONField(default=dict)
    status = models.CharField(max_length=256, null=True, blank=True)
    bill = models.CharField(max_length=256, null=True, blank=True)
    bill_package_usage = models.CharField(max_length=256, null=True, blank=True)
    is_result_sent = models.BooleanField(default=False)
    report = models.TextField(null=True, blank=True)
    reported_by = models.JSONField(default=dict)
    reported_on = models.DateTimeField(null=True, blank=True)
    approved_by = models.JSONField(default=dict)
    approved_on = models.DateTimeField(null=True, blank=True)
    audit_log = models.JSONField(default=list, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ("capture_imaging", "Can capture imaging"),
            ("submit_imaging", "Can submit imaging"),
            ("approve_reject_imaging", "Can approve or reject imaging"),
            ("mail_print_result", "Can mail or print result"),
        )

    def __str__(self):
        return self.img_id

    def _validate_bill_package(self):
        """Validates both bill and"""
        entities = (self.bill, self.bill_package_usage)
        if len(list(filter(bool, (entities)))) not in (0, 1):
            raise exceptions.ServerError(
                "Either bill or bill package should have a value not both"
            )

    def save(self, *args, **kwargs) -> None:
        self._validate_bill_package()
        return super().save(*args, **kwargs)

    def to_dict(self):
        img_obv_order_dict = model_to_dict(self)
        img_obv_order_dict["img_order"] = model_to_dict(self.img_order)
        return img_obv_order_dict

    def mail_result(self):
        """
        Function to mail result to patient
        """
        try:
            from . import utils as imaging_utils

            if self.patient.get("email"):
                file_object = imaging_utils.generate_img_obv_order_reports(
                    img_obv_order=self,
                    header=preferences.AppPreferences().use_img_mail_header,
                )
                email_utils = mail_utils.EmailUtil(
                    subject="Radiology Results",
                    body="Hello!!\n\n This mail contains an attached copy of your radiology result.\n\nRegards,\nRadiology Team",
                    receiver_mail=self.patient.get("email"),
                    attachment=file_object,
                    file_name="imaging_report.pdf",
                )
                email_utils.send_mail()
        except Exception as e:
            print(e)
            pass

    def post_payment_action(self, bill: finance_models.Bill):
        ...


class ImagingObserverOrderAttachments(
    generic_models.DateHistoryTracker, generic_models.UserHistoryTracker
):
    img_obv_order = models.ForeignKey(ImagingObservationOrder, on_delete=models.CASCADE)
    file_path = models.CharField(max_length=256, null=False, blank=False)

    def __str__(self):
        return self.img_obv_order.patient.get("username")

    def delete(self, *args, **kwargs):
        try:
            file_utils.FileUtils().remove_static_file(self.file_path)
        finally:
            return self.delete(*args, **kwargs)
