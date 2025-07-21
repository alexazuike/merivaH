from django.db import models

from api.apps.facilities import models as facility_models
from .template import EncounterTemplate


class Clinic(models.Model):
    name = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey(
        facility_models.Department, on_delete=models.CASCADE, related_name="clinics"
    )
    bill_item_code = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    templates = models.ManyToManyField(EncounterTemplate)

    class Meta:
        verbose_name_plural = "Clinics"

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name
