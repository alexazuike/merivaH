from django.apps import AppConfig
from django.conf import settings
import threading


class FinanceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api.apps.finance"

    def ready(self) -> None:
        import api.apps.finance.signals  # noqa F401
        from . import utils

        # locks processes to avoid race condition
        with threading.Lock():
            utils.create_reserve_payment_method()
            utils.create_deposit_payment_method()
            utils.create_refund_payment_method()
