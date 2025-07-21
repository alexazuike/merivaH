from . import models


def create_default_stores():
    pharmacy_store = models.Store(
        name="Pharmacy Store", type=models.StoreTypes.STORE, is_pharmacy=True
    )
    main_store = models.Store(
        name="Main Store",
        type=models.StoreTypes.STORE,
    )
    NHIS_store = models.Store(
        name="NHIS Store",
        type=models.StoreTypes.STORE,
    )
    nursing_store = models.Store(
        name="Nursing Store",
        type=models.StoreTypes.STORE,
    )
    customer_store = models.Store(
        name="Customer Store",
        type=models.StoreTypes.CUSTOMER,
    )
    inventory_loss_store = models.Store(
        name="Inventory Loss Store", type=models.StoreTypes.INVENTORY_LOSS
    )
    stores = (
        pharmacy_store,
        main_store,
        NHIS_store,
        nursing_store,
        customer_store,
        inventory_loss_store,
    )
    models.Store.objects.bulk_create(stores, ignore_conflicts=True)
    print("Default Stores Created")
