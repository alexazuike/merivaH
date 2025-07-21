from django.db import models
from pydantic import BaseModel

from api.includes import models as abstract_models


class MessageType(models.TextChoices):
    SMS = "SMS"
    WHATSAPP = "WHATSAPP"
    EMAIL = "EMAIL"


class MessageService(
    abstract_models.UserHistoryTracker, abstract_models.DateHistoryTracker
):
    name = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=50, choices=MessageType.choices)
    bill_item_code = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "MessageServices"

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name
