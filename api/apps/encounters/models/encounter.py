from enum import Enum
from typing import Union, List
import uuid

from django.db import models
from django.utils import timezone
from pydantic import BaseModel, Field

from api.includes import utils as generic_utils, exceptions
from config import preferences
from api.apps.encounters import utils

preferences_config = preferences.AppPreferences()


class DiagnosisStatus(models.TextChoices):
    WORKING = "working"
    CONFIRMED = "confirmed"


class EncounterChart(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chart: dict
    created_at: str = Field(default_factory=lambda: timezone.now().isoformat())
    created_by: dict


class EncounterObservation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    value: Union[dict, str]
    created_at: str = Field(default_factory=lambda: timezone.now().isoformat())
    created_by: dict


class EncounterType(str, Enum):
    INPATIENT = "INPATIENT"
    OUTPATIENT = "OUTPATIENT"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

    def __str__(self):
        return self.value


class Encounter_Type(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Encounter Types"

    def __str__(self):
        return self.name


class EncounterOrderChoices(models.TextChoices):
    LABORATORY = "LABORATORY"
    IMAGING = "IMAGING"
    PRESCRIPTION = "PRESCRIPTION"
    NURSING = "NURSING"


class Encounter(models.Model):
    encounter_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        null=True,
        blank=True,
        default=utils.generate_encounter_id,
    )
    clinic = models.JSONField()
    status = models.CharField(max_length=200, null=True, blank=True)
    chart: list = models.JSONField(default=list)
    legacy_chart: dict = models.JSONField(default=generic_utils.jsonfield_default_value)
    acknowledged_by = models.JSONField(default=dict)
    acknowledged_at = models.DateTimeField(default=None, null=True, blank=True)
    provider = models.JSONField(default=dict)
    patient = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    encounter_type = models.CharField(max_length=255, default="Walk In")
    encounter_datetime = models.DateTimeField(auto_now=True, blank=True)
    created_datetime = models.DateTimeField(auto_now_add=True, blank=True)
    chief_complaint = models.TextField(null=True, blank=True)
    bill = models.CharField(max_length=255, blank=True, null=True)
    bill_package_usage = models.CharField(max_length=255, blank=True, null=True)
    signed_by = models.JSONField(default=dict)
    signed_date = models.DateTimeField(null=True, blank=True)
    audit_log = models.JSONField(default=list)
    vitals: list = models.JSONField(default=list)
    orders: list = models.JSONField(default=list)
    diagnosis: list = models.JSONField(default=list)

    class Meta:
        verbose_name_plural = "Encounters"
        ordering = ["-created_datetime"]
        permissions = (
            ("take_vitals", "Can take vitals"),
            ("sign_encounter", "Can sign encounter"),
            ("acknowledge_encounter", "Can acknowledge encounter"),
        )

    def __str__(self):
        return f"{self.encounter_id}"

    def _validate_bill_package(self):
        """Validates both bill and"""
        entities = (self.bill, self.bill_package_usage)
        if len(list(filter(bool, (entities)))) not in (0, 1):
            raise exceptions.ServerError(
                "Either bill or bill package should have a value not both"
            )

    def save(self, *args, **kwargs):
        if self.id is None:
            self.status = "New"
        self._validate_bill_package()
        return super(Encounter, self).save(*args, **kwargs)

    def post_payment_action(self, bill):
        ...
