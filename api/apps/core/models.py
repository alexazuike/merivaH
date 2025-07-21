from enum import Enum
from django.db import models

from api.includes import utils, exceptions
from api.includes.models import DateHistoryTracker
from config.preferences import AppPrefenrencesCategories, AppPreferencesDataTypes

# Create your models here.


class Salutation(models.Model):
    salutations = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Salutation"

    def __str__(self):
        return self.salutations


class Gender(models.Model):
    gender = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Gender"

    def __str__(self):
        return self.gender


class Country(models.Model):
    country = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Countries"
        ordering = ["country"]

    def __str__(self):
        return self.country


class State(models.Model):
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="states"
    )
    state = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "States"

    def __str__(self):
        return self.state


class LGA(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="lgas")
    lga = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "LGA"

    def __str__(self):
        return self.lga


class District(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="districts")
    district = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Districts"

    def __str__(self):
        return self.district


class Occupation(models.Model):
    occupation = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Occupations"

    def __str__(self):
        return self.occupation


class MaritalStatus(models.Model):
    marital_status = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Marital Status"

    def __str__(self):
        return self.marital_status


class Religion(models.Model):
    religion = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Religion"

    def __str__(self):
        return self.religion


class Identity(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "Identities"

    def __str__(self):
        return self.name


class Template(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    content = models.TextField(blank=False, null=False)
    source = models.CharField(
        choices=utils.Modules.choices(), null=False, max_length=128
    )
    created_by = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Templates"

    def __str__(self):
        return self.name


class Diagnosis(models.Model):
    type = models.CharField(max_length=256)
    case = models.CharField(max_length=256)
    code = models.CharField(max_length=256)

    def __str__(self):
        return self.code


class ServiceArm(models.Model):
    name = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "ServiceArm"

    def __str__(self):
        return self.name


class DocumentType(DateHistoryTracker):
    name = models.CharField(max_length=256)

    class Meta:
        verbose_name_plural = "DocumentTypes"

    def __str__(self):
        return self.name


class AppPreferences(DateHistoryTracker):
    title = models.CharField(max_length=256, null=False, blank=False, unique=True)
    type = models.CharField(
        max_length=256,
        default=AppPreferencesDataTypes.STR,
        choices=AppPreferencesDataTypes.choices,
    )
    value = models.TextField(null=True)
    category = models.CharField(
        max_length=128,
        null=False,
        default=AppPrefenrencesCategories.GENERAL,
        choices=AppPrefenrencesCategories.choices,
    )

    class Meta:
        verbose_name_plural = "ApplicationPrefencess"

    def __str__(self):
        return self.title

    def _validate_value(self):
        try:
            if self.value:
                self.value = (
                    str(self.value)
                    if self.type == AppPreferencesDataTypes.STR
                    else int(self.value)
                    if self.type == AppPreferencesDataTypes.INT
                    else utils.str_to_bool(self.value)
                    if self.type == AppPreferencesDataTypes.BOOL
                    else float(self.value)
                )
        except (TypeError, ValueError):
            raise exceptions.BadRequest(
                "Value provided does not match provided data type"
            )

    def save(self, *args, **kwargs) -> None:
        self._validate_value()
        return super().save(*args, **kwargs)
