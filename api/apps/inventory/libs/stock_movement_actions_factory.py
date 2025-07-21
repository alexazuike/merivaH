from enum import Enum

from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.query import QuerySet

from api.includes import exceptions
from api.includes import utils
from api.apps.inventory import models


class StoreLocationType(str, Enum):
    DESTINATION = "DESTINATION"
    SOURCE = "SOURCE"


class StockMovementActionsFactory:
    def __init__(self, stock_movement: models.StockMovement, user: User):
        self.user = user
        self.stock_movement = stock_movement
        self.stock_movement_lines: QuerySet[
            models.StockMovementLine
        ] = self._get_stock_movement_lines()

    def _get_stock_movement_lines(self):
        stock_movement_lines = models.StockMovementLine.objects.filter(
            move_id=self.stock_movement.move_id
        )
        if not stock_movement_lines.exists():
            raise exceptions.BadRequest("Stock Movement has no lines")
        return stock_movement_lines

    def _handle_purchase_movement(self):
        for movement in self.stock_movement_lines:
            if movement.destination_location.get("type") == models.StoreTypes.STORE:
                self._update_store_stock(
                    store=movement.destination_location,
                    product=movement.product,
                    quantity=movement.quantity,
                    store_location_type=StoreLocationType.DESTINATION,
                )

    def _handle_sell_movement(self):
        for movement in self.stock_movement_lines:
            if movement.source_location.get("type") == models.StoreTypes.STORE:
                self._update_store_stock(
                    store=movement.sorce_location,
                    product=movement.product,
                    quantity=movement.quantity,
                    store_location_type=StoreLocationType.SOURCE,
                )

    def _handle_transfer_movement(self):
        for movement in self.stock_movement_lines:
            self._update_store_stock(
                store=movement.source_location,
                product=movement.product,
                quantity=movement.quantity,
                store_location_type=StoreLocationType.SOURCE,
            )
            self._update_store_stock(
                store=movement.destination_location,
                product=movement.product,
                quantity=movement.quantity,
                store_location_type=StoreLocationType.DESTINATION,
            )

    def _handle_adjustment_movement(self):
        for movement in self.stock_movement_lines:
            self._update_store_stock(
                store=movement.source_location,
                product=movement.product,
                quantity=movement.quantity,
                store_location_type=StoreLocationType.SOURCE,
            )
            self._update_store_stock(
                store=movement.source_location,
                product=movement.product,
                quantity=movement.quantity,
                store_location_type=StoreLocationType.DESTINATION,
            )

    def _run_validations(self):
        if not self.user.has_perm("inventory.move_stock"):
            raise exceptions.PermissionDenied("Inadequate Permission to move stock")
        if self.stock_movement.status == models.StockMovementStatus.DONE:
            raise exceptions.BadRequest("Stock Movement has already performed")
        if self.stock_movement.status != models.StockMovementStatus.APPROVED:
            raise exceptions.BadRequest("Stock Movement must be approved")

    def _update_stock_movement(self):
        user_data = utils.trim_user_data(utils.model_to_dict(self.user))
        self.stock_movement.moved_by = user_data
        self.stock_movement.moved_at = timezone.now()
        self.stock_movement.status = models.StockMovementStatus.DONE
        self.stock_movement_lines.update(
            status=models.StockMovementStatus.DONE,
            moved_by=user_data,
            moved_at=timezone.now(),
        )
        self.stock_movement.save()

    def _update_store_stock(
        self,
        store: dict,
        product: dict,
        quantity: int,
        store_location_type: StoreLocationType,
    ):
        if store.get("type") == models.StoreTypes.STORE:
            try:
                stock = models.Stock.objects.get(
                    store__id=store.get("id"), product__id=product.get("id")
                )
                stock.quantity = (
                    stock.quantity - quantity
                    if store_location_type == StoreLocationType.SOURCE
                    else stock.quantity + quantity
                )
                stock.save()
                return stock
            except models.Stock.DoesNotExist:
                quantity = (
                    quantity
                    if store_location_type == StoreLocationType.DESTINATION
                    else -quantity
                )
                stock = models.Stock.objects.create(
                    store=store, product=product, quantity=quantity
                )
                return stock
        return None

    def move(self):
        self._run_validations()
        if self.stock_movement.type == models.StockMovementType.PURCHASE:
            self._handle_purchase_movement()
        if self.stock_movement.type == models.StockMovementType.SELL:
            self._handle_sell_movement()
        if self.stock_movement == models.StockMovementType.TRANSFER:
            self._handle_transfer_movement()
        if self.stock_movement.type == models.StockMovementType.ADJUSTMENT:
            self._handle_adjustment_movement()
        self._update_stock_movement()
        return
