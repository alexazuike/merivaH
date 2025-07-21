from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from api.includes import exceptions, utils
from config import preferences
from .models import StoreTypes, Store, Stock

# @receiver(post_save, sender=Store)
# def create_store_stock(sender, instance, created, **kwargs):
#     """ Function creates a stock for a store once it is created
#     """
#     if created:
#         store_data
