from datetime import datetime, timedelta
from typing import List, Optional, TypedDict

from django.db import models
from django.db.models import F, Sum
from django.db.models.query import QuerySet
from django.utils import timezone
from django.core.validators import MinValueValidator
from pydantic import BaseModel, root_validator, Field

from api.includes import utils, models as generic_models, exceptions
from config.preferences import AppPreferences
from .billable_items import BillableItem
from .bills import Bill


class BillPackageItemDict(TypedDict):
    billable_item: dict
    quantity: int


class BillPackageItemSchema(BaseModel):
    billable_item: dict
    quantity: int = Field(gt=1)

    @root_validator
    def validate_self(cls, values: dict):
        billable_item: dict = values.get("billable_item")
        if not BillableItem.objects.filter(id=billable_item.get("id")).exists():
            raise exceptions.NotFoundException(
                f"Billable Item with id {billable_item.get('id')} is not found"
            )

    @staticmethod
    def validate_items(items: list):
        class Packages(BaseModel):
            items: List["BillPackageItemSchema"]

        data = {"items": items}
        utils.validate_schema(data, Packages)


class BillPackage(generic_models.DateHistoryTracker, generic_models.UserHistoryTracker):
    package_code = models.CharField(max_length=256, unique=True, editable=False)
    name = models.CharField(max_length=256, null=False, blank=False, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, default=0.0
    )
    validity_duration = models.BigIntegerField(verbose_name="duration_days", null=False)
    billable_items: List[dict] = models.JSONField(default=list)
    bill_item_code = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Bill Packages"

    def __str__(self):
        return self.package_code

    def _validate_billable_items(self):
        if len(self.billable_items) == 0:
            raise exceptions.BadRequest("Billable Items cannot be empty")
        BillPackageItemSchema.validate_items(self.billable_items)

    def save(self, *args, **kwargs):
        self._validate_billable_items()
        if self.id is None:
            self.package_code = utils.generate_sec_id(
                prefix=AppPreferences().bill_package_id_prefix_code,
                table_name="finance_billpackage",
                model=BillPackage,
                search_field="package_code",
            )
        super(BillPackage, self).save(*args, **kwargs)

    def get_billable_item(self, billable_item: int) -> Optional[dict]:
        return next(
            (
                item
                for item in self.billable_items
                if item.get("billable_item", {}).get("id") == billable_item
            ),
            None,
        )


class PatientBillPackageSubscription(
    generic_models.DateHistoryTracker, generic_models.UserHistoryTracker
):
    patient: dict = models.JSONField(default=dict)
    bill_package: dict = models.JSONField(default=dict)
    expiration_date: datetime = models.DateTimeField(null=True, editable=False)
    bill = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        verbose_name_plural = "PatientBillPackageSubcsriptions"

    def __str__(self):
        return self.patient.get("id")

    @property
    def is_active(self) -> bool:
        if self.expiration_date:
            return (timezone.now() < self.expiration_date) and (
                self.bill_instance and self.bill_instance.is_cleared
            )
        return False

    def _run_pre_save_validations(self):
        if self.patient_has_active_sub(
            patient_id=self.patient.get("id"),
            bill_package_id=self.bill_package.get("id"),
        ):
            raise exceptions.BadRequest(
                "Patient already has an active subscription running"
            )

    def save(self, *args, **kwargs):
        if self.id is None:
            self._run_pre_save_validations()
        return super(PatientBillPackageSubscription, self).save(*args, **kwargs)

    def post_payment_action(self, bill: Bill):
        if not self.expiration_date and bill.is_cleared:
            self.expiration_date = timezone.now() + timedelta(
                days=self.bill_package.get("validity_duration")
            )
            self.save()

    def get_billable_item(self, billable_item_id: int) -> Optional[BillPackageItemDict]:
        billable_items: list[dict] = self.bill_package.get("billable_items")
        return next(
            (
                item
                for item in billable_items
                if item.get("billable_item", {}).get("id") == billable_item_id
            ),
            None,
        )

    def get_used_billable_item_quantity(self, billable_item_id: int) -> Optional[int]:
        if not self.get_billable_item(billable_item_id):
            return None
        used_billable_items: QuerySet = self.subscription.filter(
            billable_item__id=billable_item_id
        )
        if not used_billable_items.exists():
            return 0
        return used_billable_items.aggregate(total_qty=models.Sum("quantity")).get(
            "total_qty"
        )

    @classmethod
    def __get_active_sub_query(cls, patient_id: int, bill_package_id: int) -> QuerySet:
        return cls.objects.filter(
            patient__id=patient_id,
            bill_package__id=bill_package_id,
            expiration_date__lt=timezone.now(),
        )

    @classmethod
    def patient_has_active_sub(cls, patient_id: int, bill_package_id: int) -> bool:
        return cls.__get_active_sub_query(patient_id, bill_package_id).exists()

    @classmethod
    def get_patient_active_package_billable_item_subscription(
        cls, patient_id: int, bill_package_id: int, billable_item_id: int = None
    ) -> Optional["PatientBillPackageSubscription"]:
        """
        Get active sub that contains a billable item and is not totally consumed
        """
        active_sub_querset: QuerySet = cls.__get_active_sub_query(
            patient_id, bill_package_id
        ).filter(billable_items__contains=[{"billable_item": {"id": billable_item_id}}])
        if not active_sub_querset.exists():
            return None
        active_sub: "PatientBillPackageSubscription" = active_sub_querset.first()
        if not billable_item_id:
            return active_sub
        billable_item = active_sub.get_billable_item(billable_item_id)
        quantity_used = active_sub.get_used_billable_item_quantity(billable_item_id)
        if billable_item["quantity"] - quantity_used == 0:
            return None
        return active_sub

    @classmethod
    def get_patient_active_billable_item_subscription(
        cls, patient_id: int, billable_item_id: int
    ):
        patient_active_subs = cls.objects.filter(
            patient__id=patient_id,
            bill_package__billable_items__contains=[
                {"billable_item": {"id": billable_item_id}}
            ],
            expiration_date__lt=timezone.now(),
        )
        if not patient_active_subs.exists():
            return None
        active_sub = patient_active_subs.order_by("expiration_date").first()
        billable_item = active_sub.get_billable_item(billable_item_id)
        quantity_used = active_sub.get_used_billable_item_quantity(billable_item_id)
        if billable_item["quantity"] - quantity_used == 0:
            return None
        return active_sub


class PatientBillPackageUsage(generic_models.DateHistoryTracker):
    package_subscription: PatientBillPackageSubscription = models.ForeignKey(
        PatientBillPackageSubscription,
        on_delete=models.RESTRICT,
        related_name="subscription",
    )
    billable_item: dict = models.JSONField(default=dict)
    quantity = models.IntegerField(
        null=False, validators=[MinValueValidator(limit_value=1)]
    )
    is_service_rendered = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "PatientBillPackageUsages"

    def __str__(self):
        return str(self.package_subscription.pk)

    def _validate_package_item(self, is_new: bool):
        if not self.package_subscription.is_active:
            raise exceptions.BadRequest("Package Subscription is not active")

        if not self.package_subscription.get_billable_item(self.billable_item):
            raise exceptions.BadRequest(
                "billable item not part of package subscription"
            )

        package_quantity = self.package_subscription.get_billable_item(
            self.billable_item.get("id")
        ).get("quantity")

        total_quantities_used = (
            self.package_subscription.get_used_billable_item_quantity(
                self.billable_item.get("id")
            )
        )
        if is_new:
            total_quantities_used += self.quantity

        if total_quantities_used > package_quantity:
            raise exceptions.BadRequest(
                "total quantity is greater than quantity permitted in package"
            )

    def save(self, *args, **kwargs) -> None:
        self._validate_package_item(is_new=bool(self.id))
        return super().save(*args, **kwargs)
