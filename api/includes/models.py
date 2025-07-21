from django.db import models


class DateHistoryTracker(models.Model):
    """
    Tracks date of creation and modification
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserHistoryTracker(models.Model):
    """
    Tracks user who created and updated the table record
    """

    created_by: dict = models.JSONField(default=dict)
    updated_by: dict = models.JSONField(default=dict)

    class Meta:
        abstract = True
