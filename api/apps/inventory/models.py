from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from api.includes import utils, exceptions
from api.includes.models import DateHistoryTracker, UserHistoryTracker

################# Enums And Schemas #####################


class StoreTypes(models.TextChoices):
    CUSTOMER = "CUSTOMER"
    INVENTORY_LOSS = "INVENTORY LOSS"
    CONSUMPTION = "CONSUMPTION"
    STORE = "STORE"
    SUPPLIER = "SUPPLIER"


class StockMovementType(models.TextChoices):
    PURCHASE = "PURCHASE"
    SELL = "SELL"
    TRANSFER = "TRANSFER"
    ADJUSTMENT = "ADJUSTMENT"


class StockMovementStatus(models.TextChoices):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    CANCELLED = "CANCELLED"
    DONE = "DONE"


#################### Django Models ####################


class Category(DateHistoryTracker):
    parent = models.ForeignKey(
        "self",
        related_name="parent_category",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=180, null=False, blank=False)
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        unique_together = ("parent", "name")

    def __str__(self):
        return self.name


class Store(DateHistoryTracker, UserHistoryTracker):
    name = models.CharField(max_length=180, unique=True, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    type = models.CharField(
        max_length=218, blank=False, null=False, choices=StoreTypes.choices
    )
    is_pharmacy = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Stores"

    def __str__(self):
        return self.name


class Product(DateHistoryTracker, UserHistoryTracker):
    code = models.CharField(max_length=180, unique=True, null=True, blank=True)
    sec_id = models.CharField(max_length=180, unique=True, null=True, blank=True)
    name = models.CharField(max_length=256, null=False, blank=False)
    uom = models.CharField(max_length=180, null=False, blank=False)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    divider = models.FloatField(null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    bill_item_code = models.CharField(max_length=256, null=True, blank=True)
    category = models.JSONField(default=dict)
    generic_drug = models.JSONField(default=dict)
    is_drug = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.generic_drug and self.is_drug:
            raise exceptions.BadRequest("Generic Drug is not set")
        if not self.id:
            self.sec_id = utils.generate_sec_id(
                prefix="PRD",
                table_name="inventory_product",
                model=Product,
                search_field="sec_id",
            )
        return super().save(*args, **kwargs)


class Stock(DateHistoryTracker):
    store = models.JSONField(default=dict)
    product = models.JSONField(default=dict)
    quantity = models.IntegerField()
    # reserved: int

    class Meta:
        verbose_name_plural = "Stocks"

    def __str__(self):
        return f"{self.store['name']}_{self.product['name']}"


class StockMovementLine(DateHistoryTracker):
    move_id = models.CharField(max_length=256, blank=True, null=True, editable=False)
    product = models.JSONField(default=dict)
    quantity = models.IntegerField()
    source_location = models.JSONField(default=dict)
    destination_location = models.JSONField(default=dict)
    status = models.CharField(
        max_length=128, choices=StockMovementStatus.choices, blank=False, null=False
    )
    approved_by = models.JSONField(default=dict)
    approved_at = models.DateTimeField(null=True, blank=False)
    cancelled_by = models.JSONField(default=dict)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    moved_by = models.JSONField(default=dict)
    moved_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "StockMovementLines"

    def __str__(self):
        return self.move_id

    def save(self, *args, **kwargs) -> None:
        if self.id and not (self.approved_at or self.cancelled_by):
            raise exceptions.BadRequest(
                "Cannot update a stock movement line that is either approved or  cancelled"
            )
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.status != StockMovementStatus.DRAFT:
            raise exceptions.BadRequest("Cannot delete non-draft stock movement lines")
        return super().delete(*args, **kwargs)


class StockMovement(DateHistoryTracker, UserHistoryTracker):
    move_id = models.CharField(max_length=256, unique=True, blank=True, null=True)
    type = models.CharField(
        max_length=128, choices=StockMovementType.choices, blank=False, null=False
    )
    source_location: dict = models.JSONField(default=dict)
    destination_location: dict = models.JSONField(default=dict)
    status = models.CharField(
        max_length=128,
        choices=StockMovementStatus.choices,
        default=StockMovementStatus.DRAFT,
        blank=False,
        null=False,
    )
    approved_by = models.JSONField(default=dict)
    approved_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.JSONField(default=dict)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    moved_by = models.JSONField(default=dict)
    moved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "StockMovements"
        permissions = (
            ("approve_stock_movement", "Can approve stock movement"),
            ("cancel_stock_movemnet", "Can cancel stock movement"),
            ("move_stock", "Can perform stock movements"),
        )

    def __str__(self):
        return self.move_id

    @property
    def is_approved(self):
        return self.status == StockMovementStatus.APPROVED

    @property
    def is_draft(self):
        return self.status == StockMovementStatus.DRAFT

    @property
    def is_cancelled(self):
        return self.status == StockMovementStatus.CANCELLED

    @property
    def is_done(self):
        return self.status == StockMovementStatus.DONE

    def _validate_stock_movement_type(self):
        if self.type == StockMovementType.PURCHASE:
            if self.source_location.get("type") != StoreTypes.VENDOR:
                raise exceptions.BadRequest(
                    "source location type has to be Vendor for PURCHASE stock movements"
                )

        if self.type == StockMovementType.SELL:
            if self.destination_location.get("type") != StoreTypes.CUSTOMER:
                raise exceptions.BadRequest(
                    "destination location type has to be of type customer for SELL stock movements"
                )
        if self.type == StockMovementType.TRANSFER:
            if not (
                self.destination_location.get("type") == StoreTypes.STORE
                and self.source_location.get("type") == StoreTypes.STORE
            ):
                raise exceptions.BadRequest(
                    "destination location and source location has to be of type STORE for TRANSFER stock movements "
                )
        if self.type == StockMovementType.ADJUSTMENT:
            if (
                list(
                    filter(
                        lambda location: location.get("type")
                        == StoreTypes.INVENTORY_LOSS,
                        [self.destination_location, self.source_location],
                    )
                ).count()
                == 1
            ):
                raise exceptions.BadRequest(
                    "One of source or destination location must be of type INVENTORY LOSS"
                )

    def save(self, *args, **kwargs) -> None:
        if not self.id:
            self.status = StockMovementStatus.DRAFT
            self.move_id = utils.generate_sec_id(
                prefix="STM",
                table_name="inventory_stockmovement",
                model=StockMovement,
                search_field="created_at",
            )
        self._validate_stock_movement_type()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.status != StockMovementStatus.DRAFT:
            raise exceptions.BadRequest("Cannot delete non-draft stock movements")
        lines = StockMovementLine.objects.filter(move_id=self.move_id)
        lines.delete()
        return super().delete(*args, **kwargs)

    def approve(self, user: User):
        user = utils.trim_user_data(utils.model_to_dict(user))
        if not self.is_draft:
            raise exceptions.BadRequest("Can only approve stock movements in draft")
        self.status = StockMovementStatus.APPROVED
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()
        StockMovementLine.objects.filter(move_id=self.move_id).update(
            approved_by=user,
            approved_at=timezone.now(),
            status=StockMovementStatus.APPROVED,
        )

    def cancel(self, user: User):
        user = utils.trim_user_data(utils.model_to_dict(user))
        if not self.is_draft:
            raise exceptions.BadRequest("Can only cancel stock movements in draft")
        self.status = StockMovementStatus.CANCELLED
        self.cancelled_by = user
        self.cancelled_at = timezone.now()
        self.save()
        StockMovementLine.objects.filter(move_id=self.move_id).update(
            cancelled_by=user,
            cancelled_at=timezone.now(),
            status=StockMovementStatus.CANCELLED,
        )

    def move(self, user: User):
        from .libs.stock_movement_actions_factory import StockMovementActionsFactory

        movement_actions_factory = StockMovementActionsFactory(self, user)
        movement_actions_factory.move()
