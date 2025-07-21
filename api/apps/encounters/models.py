from enum import Enum
from django.db import models

from api.apps.facilities import models as facility_models
from . import utils as encounter_utils
from api.includes.utils import (
    jsonfield_default_value,
    time_log_jsonfield_default_value,
)


class Clinic(models.Model):
    name = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey(
        facility_models.Department, on_delete=models.CASCADE, related_name="clinics"
    )
    bill_item_code = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Clinics"

    def __str__(self):
        return self.name


class Status(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Status"

    def __str__(self):
        return self.name


class Encounter_Type(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Encounter Types"

    def __str__(self):
        return self.name


class Encounter(models.Model):
    encounter_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        default=encounter_utils.generate_encounter_id,
    )
    clinic = models.JSONField()
    status = models.CharField(max_length=200, null=True, blank=True)
    time_log = models.JSONField(default=time_log_jsonfield_default_value)
    chart = models.JSONField(default=jsonfield_default_value)
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
    signed_by = models.JSONField(default=dict)
    signed_date = models.DateTimeField(null=True, blank=True)
    audit_log = models.JSONField(default=list)

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

    def save(self, *args, **kwargs):
        if self.id is None:
            self.status = "New"
        return super(Encounter, self).save(*args, **kwargs)


class EncounterType(str, Enum):
    INPATIENT = "INPATIENT"
    OUTPATIENT = "OUTPATIENT"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

    def __str__(self):
        return self.value
