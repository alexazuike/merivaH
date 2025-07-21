from concurrent.futures import ThreadPoolExecutor
from django.db.models.signals import post_save
from django.dispatch import receiver

from api.includes import utils
from api.apps.finance.models import Payment, Bill


@receiver(post_save, sender=Payment)
def post_payment_hooks(sender, instance: Payment, created, **kwargs):
    """
    Integrates after payment hooks
    """

    if created:
        bills = instance.bills
        if not bills:
            return
        bills = Bill.objects.filter(id__in=[bill["id"] for bill in bills])
        with ThreadPoolExecutor(max_workers=5) as context:
            context.map(lambda bill: bill.run_post_payment_action, bills)
