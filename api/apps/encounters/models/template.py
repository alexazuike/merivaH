from django.db import models

from api.includes import models as generic_models, exceptions


class EncounterTemplate(
    generic_models.UserHistoryTracker, generic_models.DateHistoryTracker
):
    title: str = models.CharField(max_length=256, null=False, blank=False)
    description: str = models.TextField(null=True, blank=True)
    content: list = models.JSONField(default=list)
    is_active: bool = models.BooleanField(default=True)
    is_default: bool = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "EncounterTemplates"
        ordering = ["-id"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs) -> None:
        return super().save(*args, **kwargs)
