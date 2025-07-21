from typing import List, Optional, Union, Iterable, Any, Dict
from datetime import datetime

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from pydantic import BaseModel, root_validator, Field

from api.includes import exceptions, utils
from api.includes.models import DateHistoryTracker, UserHistoryTracker
from config import preferences

# OPEN
# SCHEDULED
# CLOSED

NURSING_TASK_ID_PREFIX = (
    f"{preferences.AppPreferences().nursing_task_activity_id_prefix_code}"
)


class NursingOrderStatus(models.TextChoices):
    OPEN = "OPEN"
    SCHEDULED = "SCHEDULED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class NursingTaskStatus(models.TextChoices):
    SCHEDULED = "SCHEDULED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class NursingTaskType(models.TextChoices):
    IMMEDIATE = "IMMEDIATE"
    SCHEDULED = "SCHEDULED"


class TaskInventorySchema(BaseModel):
    product: dict
    store: dict


class NursingServiceSchema(BaseModel):
    name: str
    bill_item_code: str


class NursingTaskSchema(BaseModel):
    id: str = Field(
        default_factory=lambda: f"{NURSING_TASK_ID_PREFIX}_{get_random_string(length=8)}"
    )
    inventory: List[TaskInventorySchema] = []
    nursing_services: List[NursingServiceSchema] = []
    notes: Optional[str]
    status: Optional[NursingTaskStatus] = NursingTaskStatus.SCHEDULED
    type: NursingTaskType
    bills: List[int] = []
    bill_package_usages: List[int] = []
    created_by: dict
    created_at: datetime = Field(default_factory=timezone.now)
    scheduled_at: Optional[datetime]
    scheduled_by: Optional[dict]
    closed_by: Optional[dict]
    closed_at: Optional[datetime]
    cancelled_by: Optional[dict]
    cancelled_at: Optional[datetime]
    disposition: Optional[str]

    @classmethod
    def _validate_bills_and_packages(cls, bills: list, bill_packages: list):
        """Validates both bill and bill packages"""
        entities = (bills, bill_packages)
        if len(list(filter(bool, (entities)))) not in (0, 1):
            raise exceptions.ServerError(
                "Either bill or bill package should have a value not both"
            )

    @root_validator
    def validate_schema(cls, values: dict):
        bills = values.get("bills", [])
        bill_packages = values.get("bill_packages", [])
        if values["status"] != NursingTaskStatus.CLOSED:
            if values["type"] == NursingTaskType.IMMEDIATE:
                values["status"] = NursingTaskStatus.CLOSED
                values["scheduled_at"] = values["created_at"]
                values["scheduled_by"] = values["created_by"]
                values["closed_at"] = values["created_at"]
                values["closed_by"] = values["created_by"]

            if values["type"] == NursingTaskType.SCHEDULED:
                values["status"] = NursingTaskStatus.SCHEDULED
                values["scheduled_by"] = values["created_by"]
                values["nursing_services"] = []
                if values.get("scheduled_at") is None:
                    raise exceptions.BadRequest("Scheduled DateTime is required")
            cls._validate_bills_and_packages(bills, bill_packages)
        return values

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


def validate_nursing_tasks(value: list):
    class NursingTasks(BaseModel):
        tasks: List[NursingTaskSchema] = []

    data = {"tasks": value}
    utils.validate_schema(data=data, schema=NursingTasks)


class NursingStation(DateHistoryTracker, UserHistoryTracker):
    name = models.CharField(max_length=256, blank=False, null=False)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "NursingStations"


class NursingService(DateHistoryTracker, UserHistoryTracker):
    name = models.CharField(
        verbose_name="service_name", null=False, blank=False, max_length=256
    )
    description = models.TextField(null=True, blank=True)
    bill_item_code = models.CharField(max_length=256, null=True, blank=True)
    audit_log = models.JSONField(default=list, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "NursingServices"


class NursingOrder(DateHistoryTracker, UserHistoryTracker):
    order_id = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField(
        verbose_name=("order_description"), blank=False, null=False
    )
    status = models.CharField(
        max_length=256,
        verbose_name="task_status",
        choices=NursingOrderStatus.choices,
        default=NursingOrderStatus.OPEN,
    )
    station: dict = models.JSONField(default=dict)
    tasks: List[dict] = models.JSONField(verbose_name="nursing_tasks", default=list)
    patient: dict = models.JSONField(default=dict)
    closed_by: dict = models.JSONField(default=dict)
    closed_at = models.DateTimeField(null=True)
    cancelled_by: dict = models.JSONField(default=dict)
    cancelled_at = models.DateTimeField(null=True)
    disposition = models.TextField(null=True)

    def __str__(self):
        return self.order_id

    class Meta:
        verbose_name_plural = "NursingOrders"
        permissions = (
            ("close_order", "Can complete order"),
            ("cancel_order", "Can cancel order"),
            ("add_task", "Can add task "),
            ("remove_task", "Can remove task"),
            ("change_task", "Can change task"),
            ("view_task", "Can view task"),
        )

    @property
    def active_tasks(self):
        return [
            task
            for task in self.tasks
            if task.get("status") != NursingTaskStatus.CLOSED
        ]

    @property
    def closed_tasks(self):
        return [
            task
            for task in self.tasks
            if task.get("status") == NursingTaskStatus.CLOSED
        ]

    def save(self, *args, **kwargs) -> None:
        validate_nursing_tasks(self.tasks)
        if self._state.adding:
            self.order_id = utils.generate_sec_id(
                prefix=preferences.AppPreferences().nursing_task_id_prefix_code,
                table_name="nursing_nursingorder",
                model=NursingOrder,
                search_field="order_id",
            )
        else:
            if self.status in [
                NursingOrderStatus.CANCELLED,
                NursingOrderStatus.CLOSED,
            ] and "status" not in (kwargs.get("update_fields", []) or []):
                raise exceptions.BadRequest("Nursing is already closed or cancelled")
        return super().save(*args, **kwargs)

    def close(self, user: User, disposition: str = None):
        if self.status == NursingOrderStatus.CLOSED:
            raise exceptions.BadRequest("Nursing Order is already closed")
        if self.status == NursingOrderStatus.CANCELLED:
            raise exceptions.BadRequest("Nursing order is already cancelled")
        if not user.has_perm("nursing.close_order"):
            raise exceptions.PermissionDenied(
                "Inadequate permissions to close nursing order"
            )
        if any(
            task
            for task in self.tasks
            if task.get("status") == NursingTaskStatus.SCHEDULED
        ):
            raise exceptions.BadRequest("Order cannot be closed due to scheduled tasks")
        self.closed_by = utils.trim_user_data(utils.model_to_dict(user))
        self.closed_at = timezone.now()
        self.disposition = disposition
        self.status = NursingOrderStatus.CLOSED
        self.save(update_fields=["status"])

    def cancel(self, user: User, disposition: str = None):
        if self.status == NursingOrderStatus.CLOSED:
            raise exceptions.BadRequest("Nursing order is already closed")
        if self.status == NursingOrderStatus.CANCELLED:
            raise exceptions.BadRequest("Nursing order is already cancelled")
        if any(
            task
            for task in self.tasks
            if task.get("status") != NursingTaskStatus.CLOSED
        ):
            raise exceptions.BadRequest(
                "Cannot close nursing order due to presence of uncancelled tasks"
            )
        if not user.has_perm("nursing.cancel_order"):
            raise exceptions.PermissionDenied(
                "Inadequate permissions to cancel nursing order"
            )
        self.cancelled_by = utils.trim_user_data(utils.model_to_dict(user))
        self.cancelled_at = timezone.now()
        self.disposition = disposition
        self.status = NursingOrderStatus.CANCELLED
        self.save(update_fields=["status"])

    def update_task(self, task_id: str, values: Dict[str, Any]):
        task = next((task for task in self.tasks if task.get("id") == task_id), None)
        if not task:
            raise exceptions.ServerError("Task not found")
        index = self.tasks.index(task)
        for field, value in values.items():
            task[field] = value
        self.tasks[index] = task
        self.save(update_fields=["tasks"])
