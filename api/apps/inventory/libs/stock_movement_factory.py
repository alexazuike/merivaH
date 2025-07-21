from typing import List, Optional

from django.contrib.auth.models import User

from api.apps.inventory import models
from api.includes import utils
from api.includes import exceptions


class StockMovementFactory:
    def __init__(
        self,
        type: models.StockMovementType,
        source_location: dict,
        destination_location: dict,
        products: List[dict],
        user: User,
        stock_movement: Optional[models.StockMovement],
    ) -> None:
        self.type = type
        self.source_location = source_location
        self.destination_location = destination_location
        self.products = products
        self.user = user
        self.stock_movement = stock_movement
        self._init_validate()
        self._setup_store_locations()

    @classmethod
    def _get_inventory_loss_store(cls):
        store = models.Store.objects.filter(type=models.StoreTypes.INVENTORY_LOSS)
        if not store.exists():
            raise exceptions.ServerError("Inventory Loss store does not exist")
        return store.first()

    def _setup_store_locations(self):
        inventory_loss_store = self._get_inventory_loss_store()
        if self.type == models.StockMovementType.ADJUSTMENT:
            if not self.source_location:
                self.source_location = utils.model_to_dict(inventory_loss_store)
            if not self.destination_location:
                self.destination_location = utils.model_to_dict(inventory_loss_store)

        self.source_location = utils.copy_dict(
            self.source_location, ("id", "name", "type")
        )
        self.destination_location = utils.copy_dict(
            self.destination_location, ("id", "name", "type")
        )

    def _init_validate(self):
        # validates for non stock adjustments
        if type != models.StockMovementType.ADJUSTMENT:
            if not (self.source_location and self.destination_location):
                raise exceptions.BadRequest(
                    "Source and Destination locations must be set"
                )
        # validates for stock adjustments
        if type == models.StockMovementType.ADJUSTMENT:
            if (
                list(
                    map(bool, [self.source_location, self.destination_location])
                ).count(True)
                != 1
            ):
                raise exceptions.BadRequest(
                    "Only one of source or destination location must be set "
                )

    def _validate_stock_movement_types(self):
        if self.type == models.StockMovementType.PURCHASE:
            if self.source_location.get("type") != models.StoreTypes.VENDOR:
                raise exceptions.BadRequest(
                    "source location type has to be Vendor for PURCHASE stock movements"
                )

        if self.type == models.StockMovementType.SELL:
            if self.destination_location.get("type") != models.StoreTypes.CUSTOMER:
                raise exceptions.BadRequest(
                    "destination location type has to be of type customer for SELL stock movements"
                )
        if self.type == models.StockMovementType.TRANSFER:
            if not (
                self.destination_location.get("type") == models.StoreTypes.STORE
                and self.source_location.get("type") == models.StoreTypes.STORE
            ):
                raise exceptions.BadRequest(
                    "destination location and source location has to be of type STORE for TRANSFER stock movements "
                )
        if self.type == models.StockMovementType.ADJUSTMENT:
            if (
                list(
                    filter(
                        lambda location: location.get("type")
                        == models.StoreTypes.INVENTORY_LOSS,
                        [self.destination_location, self.source_location],
                    )
                ).count()
                == 1
            ):
                raise exceptions.ServerError(
                    "One of source or destination location must be of type INVENTORY LOSS"
                )

    def _run_validations(self):
        self._validate_stock_movement_types()

    def _get_store_stock(self, store: dict, product: dict):
        if store:
            if store.get("type") == models.StoreTypes.STORE:
                try:
                    stock = models.Stock.objects.get(
                        store__id=store.get("id"), product__id=product.get("id")
                    )
                    store["quantity"] = stock.quantity
                    return store
                except models.Stock.DoesNotExist:
                    store["quantity"] = 0
                    return store
        return store

    def _build_stock_movement_lines(self) -> List[models.StockMovementLine]:
        if self.type != models.StockMovementType.ADJUSTMENT:
            stock_movement_lines = [
                models.StockMovementLine(
                    move_id=self.stock_movement.move_id,
                    product=utils.copy_dict(product["product"], ["id", "name"]),
                    quantity=product("quantity"),
                    source_location=self._get_store_stock(
                        self.stock_movement.source_location, product
                    ),
                    destination_location=self._get_store_stock(
                        self.stock_movement.destination_location, product
                    ),
                    status=self.stock_movement.status,
                )
                for product in self.products
            ]
            return stock_movement_lines
        else:
            loss_store = (
                self.source_location
                if self.source_location.get("type") == models.StoreTypes.INVENTORY_LOSS
                else self.destination_location
            )
            other_store = (
                self.destination_location
                if self.source_location.get("type") == models.StoreTypes.INVENTORY_LOSS
                else self.destination_location
            )
            stock_movement_lines = []
            for product in self.products:
                stock = self._get_store_stock(loss_store, product)
                quantity = (
                    stock.get("quantity", 0) - product.get("quantity")
                    if stock.get("quantity", 0) > product.get("quantity")
                    else product.get("quantity") - stock.get("quantity", 0)
                )
                source_location, destination_location = (
                    other_store,
                    loss_store
                    if stock.get("quantity", 0) > product.get("quantity")
                    else loss_store,
                    other_store,
                )
                stock_movement_lines.append(
                    models.StockMovementLine(
                        move_id=self.stock_movement.move_id,
                        product=utils.copy_dict(product["product"], ["id", "name"]),
                        quantity=quantity,
                        source_location=self._get_store_stock(source_location, product),
                        destination_location=self._get_store_stock(
                            destination_location, product
                        ),
                        status=self.stock_movement.status,
                    )
                )
            return stock_movement_lines

    def _create_stock_movement(self):
        self.stock_movement = models.StockMovement.objects.create(
            type=self.type,
            source_location=self.source_location,
            destination_location=self.destination_location,
            created_by=utils.trim_user_data(utils.model_to_dict(self.user)),
        )

    def _create_stock_movement_lines(self):
        if self.stock_movement is None:
            raise exceptions.ServerError("Stock Movement is not set")
        stock_movement_lines = self._build_stock_movement_lines()
        models.StockMovementLine.objects.bulk_create(stock_movement_lines)
        return self.stock_movement

    def _update_stock_movement(self):
        ...

    def _update_stock_movement_lines(self):
        ...

    def create(self) -> models.StockMovement:
        self._run_validations()
        self._create_stock_movement()
        self._create_stock_movement_lines()
        return self.stock_movement

    def update(self) -> models.StockMovement:
        self._run_validations()
        self._update_stock_movement()
        self._update_stock_movement_lines()
        return self.stock_movement
