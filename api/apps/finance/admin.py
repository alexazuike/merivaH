from django.contrib import admin

from . import models

# Register your models here.
admin.site.register(models.BillableItem)
admin.site.register(models.PriceList)
admin.site.register(models.PriceListItem)
admin.site.register(models.PaymentMethod)
admin.site.register(models.PayerScheme)
admin.site.register(models.Payer)
