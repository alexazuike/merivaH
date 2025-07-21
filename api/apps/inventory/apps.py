from django.apps import AppConfig
import threading


class InventoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api.apps.inventory"

    def ready(self) -> None:
        from . import utils

        with threading.Lock():
            utils.create_default_stores()
