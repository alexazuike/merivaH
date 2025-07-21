from enum import Enum
from django.db import models

from api.includes import utils, models as generic_models
from config.preferences import AppPreferences


class BillableItem(models.Model):
    item_code = models.CharField(max_length=256, unique=True, editable=False)
    description = models.CharField(max_length=256, blank=True, null=True)
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, default=0.0
    )
    selling_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, default=0.0
    )
    module = models.CharField(max_length=256, choices=utils.Modules.choices())
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.JSONField(default=dict)
    updated_by = models.JSONField(default=dict)

    class Meta:
        verbose_name_plural = "Billable Items"

    def __str__(self):
        return self.item_code

    def save(self, *args, **kwargs):
        if self.id is None:
            module_prefix = str(utils.Modules.get_module(self.module).value)
            self.item_code = utils.generate_sec_id(
                prefix=module_prefix,
                table_name="finance_billableitem",
                model=BillableItem,
                search_field="item_code",
            )
        super(BillableItem, self).save(*args, **kwargs)

    def update_module_bill_details(
        self,
        bill_price: float = None,
        cost_price: float = None,
        description: str = None,
    ):
        """Function updates bill details for app module"""
        self.selling_price = bill_price or self.selling_price
        self.cost = cost_price or self.cost
        self.description = description or self.description
        self.save()


class PriceList(models.Model):
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=256, blank=True, null=True)
    created_by = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)
    meta = models.JSONField(default=dict)

    class Meta:
        verbose_name_plural = "Price Lists"

    def __str__(self):
        return self.name


class PriceListItem(models.Model):
    bill_item_code = models.CharField(max_length=256, null=False, blank=False)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_list = models.ForeignKey(PriceList, on_delete=models.CASCADE)
    co_pay = models.JSONField(default=dict)
    is_auth_req = models.BooleanField(default=False)
    is_capitated = models.BooleanField(default=False)
    module = models.CharField(
        max_length=256, choices=utils.Modules.choices(), null=True
    )
    is_exclusive = models.BooleanField(default=False)
    post_auth_allowed = models.BooleanField(default=False)
    created_by = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Price List Items"

    def __str__(self):
        return self.bill_item_code
