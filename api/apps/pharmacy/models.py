from datetime import datetime
from typing import Optional, List

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.crypto import get_random_string
from pydantic import BaseModel, Field

from api.includes import utils, exceptions, mail_utils
from api.includes.models import DateHistoryTracker, UserHistoryTracker
from api.apps.inventory import models as inv_models
from config import preferences

###########################################
########## Enums and Choices
###########################################


class PrescriptionSources(models.TextChoices):
    OPD = "OPD"
    IPD = "IPD"
    NS = "NS"


class PrescriptionDetailStatus(models.TextChoices):
    """Prescription Detail Status"""

    IN_FILLED = "FULFILLED IN"
    OUT_FILLED = "FULFILLED OUT"


class PrescriptionStatus(models.TextChoices):
    """Main Prescription status"""

    NEW = "NEW"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class PrescriptionDetailSchema(BaseModel):
    """Schema describing each line of prescription"""

    id: str = f"RXD_{get_random_string(length=8)}"
    generic_drug: dict
    product: Optional[dict] = {}
    dose: dict
    unit: dict
    route: dict
    frequency: dict
    direction: dict
    duration: dict
    dispense_quantity: int = 1
    status: str


class PrescriptionSchema(BaseModel):
    """Schema describing Prescription"""

    prc_id: Optional[str]
    patient: dict
    source: PrescriptionSources
    prescribing_physician: Optional[dict] = Field(defualt={})
    store: Optional[dict] = Field(default={})
    details: List[PrescriptionDetailSchema]
    created_by: dict
    created_at: datetime


##########################################
######## Django Models
##########################################

######################################### Config models #####################################


class Dose(DateHistoryTracker):
    name = models.CharField(max_length=256, null=False, blank=False)
    multiplier = models.FloatField(null=False, blank=False)

    class Meta:
        verbose_name_plural = "Doses"

    def __str__(self):
        return self.name


class Unit(DateHistoryTracker):
    name = models.CharField(max_length=256, null=False, blank=False)

    class Meta:
        verbose_name_plural = "Units"

    def __str__(self):
        return self.name


class Route(DateHistoryTracker):
    name = models.CharField(max_length=256, null=False, blank=False)

    class Meta:
        verbose_name_plural = "Routes"

    def __str__(self):
        return self.name


class Frequency(DateHistoryTracker):
    name = models.CharField(max_length=256, null=False, blank=False)
    multiplier = models.FloatField(null=False, blank=False)

    class Meta:
        verbose_name_plural = "Frequencies"

    def __str__(self):
        return self.name


class Direction(DateHistoryTracker):
    name = models.CharField(max_length=256, null=False, blank=False)

    class Meta:
        verbose_name_plural = "Directions"

    def __str__(self):
        return self.name


class Duration(DateHistoryTracker):
    name = models.CharField(max_length=256, null=False, blank=False)
    multiplier = models.FloatField(null=False, blank=False)

    class Meta:
        verbose_name_plural = "Durations"

    def __str__(self):
        return self.name


class Category(DateHistoryTracker):
    parent = models.ForeignKey(
        "self",
        related_name="parent_category",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=256, null=False, blank=False)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name


class GenericDrug(DateHistoryTracker):
    name = models.CharField(max_length=256)
    category = models.JSONField(default=dict)

    class Meta:
        verbose_name_plural = "Drugs"

    def __str__(self) -> str:
        return self.name


class PharmacyStore(DateHistoryTracker, UserHistoryTracker):
    name = models.CharField(max_length=180, unique=True, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    inv_store = models.ForeignKey(
        inv_models.Store, on_delete=models.RESTRICT
    )  # inventory store

    class Meta:
        verbose_name_plural = "Pharmacy Stores"

    def __str__(self):
        return self.name


class Template(DateHistoryTracker, UserHistoryTracker):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    content = models.JSONField(default=dict)
    is_public = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Templates"

    def __str__(self):
        return self.name


class Prescription(DateHistoryTracker, UserHistoryTracker):
    """Holds Prescription details"""

    prc_id = models.CharField(max_length=256, null=True, blank=True)
    patient: dict = models.JSONField(default=dict)
    source = models.CharField(max_length=256, choices=PrescriptionSources.choices)
    prescribing_physician: dict = models.JSONField(default=dict)
    details: List[dict] = models.JSONField(default=list)
    store: dict = models.JSONField(default=dict)
    status = models.CharField(
        max_length=256,
        choices=PrescriptionStatus.choices,
        default=PrescriptionStatus.NEW,
    )
    confirmed_by: dict = models.JSONField(default=dict)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_by: dict = models.JSONField(default=dict)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Prescriptions"
        permissions = (
            ("confirm_prescription", "Can confirm prescription"),
            ("cancel_prescription", "Can cancel prescription"),
            ("download_prescription", "Can download prescription"),
            ("mail_prescription", "Can mail prescription"),
        )

    def __str__(self):
        return self.patient["email"]

    def save(self, *args, **kwargs):
        if not self.id:
            self.prc_id = utils.generate_sec_id(
                prefix=preferences.AppPreferences().prescription_id_prefix_code,
                table_name="pharmacy_prescription",
                model=Prescription,
                search_field="prc_id",
            )
        else:
            old_object = Prescription.objects.get(id=self.id)
            if old_object.status != PrescriptionStatus.NEW:
                raise exceptions.BadRequest(
                    "Cannot update prescription that is has been fulfilled or cancelled"
                )
        return super().save(*args, **kwargs)

    def confirm(self, user: User):
        if not user.has_perm("pharmacy.confirm_prescription"):
            raise exceptions.PermissionDenied(
                "Inadequate Permissions to confirm prescription"
            )
        if self.status == PrescriptionStatus.CONFIRMED:
            raise exceptions.BadRequest("Prescription is already confirmed")
        if self.status == PrescriptionStatus.CANCELLED:
            raise exceptions.BadRequest("Prescription is already cancelled")
        self.confirmed_at = timezone.now()
        self.confirmed_by = utils.trim_user_data(utils.model_to_dict(user))
        self.status = PrescriptionStatus.CONFIRMED
        self.save()

    def cancel(self, user: User):
        if not user.has_perm("pharmacy.cancel_prescription"):
            raise exceptions.PermissionDenied(
                "Inadequate Permissions to cancel prescription"
            )
        if self.status == PrescriptionStatus.CONFIRMED:
            raise exceptions.BadRequest("Prescription is already confirmed")
        if self.status == PrescriptionStatus.CANCELLED:
            raise exceptions.BadRequest("Prescription is already cancelled")
        self.cancelled_at = timezone.now()
        self.cancelled_by = utils.trim_user_data(utils.model_to_dict(user))
        self.status = PrescriptionStatus.CANCELLED
        self.save()

    def to_pdf(self, user: User):
        from .libs.prescription_result_generator import PrescriptionResultGenerator

        if not user.has_perm("pharmacy.download_prescription"):
            raise exceptions.PermissionDenied(
                "Inadequate Permissions to download prescription"
            )
        if self.status != PrescriptionStatus.CONFIRMED:
            raise exceptions.BadRequest("Prescription is not confirmed")

        result_generator = PrescriptionResultGenerator(
            self, preferences.AppPreferences().use_presc_report_header
        )
        return result_generator.render_to_pdf()

    def mail_pdf(self, user: User):
        if not user.has_perm("pharmacy.mail_prescription"):
            raise exceptions.PermissionDenied(
                "Inadequate Permissions to mail prescription"
            )
        pdf_file = self.to_pdf()
        if self.patient.get("email"):
            try:
                email_utils = mail_utils.EmailUtil(
                    subject="Prescriptions",
                    body="Hello!!\nThis mail contains a file containing your prescriptions",
                    receiver_mail=self.patient.get("email"),
                    attachment=pdf_file,
                    file_name="lab_report.pdf",
                )
                email_utils.send_mail()
            except Exception as e:
                raise exceptions.ServerError("Unable to send mail")
