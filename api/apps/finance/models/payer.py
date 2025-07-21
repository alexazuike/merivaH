from enum import Enum

from django.db import models

from . import PriceList

###################### SCHEMA ###########################


class PayerSchemeType(str, Enum):
    SELF_PREPAID = "SELF (PREPAID)"
    SELF_POSTPAID = "SELF (POSTPAID)"
    INSURANCE = "INSURANCE"
    CORPORATE = "CORPORATE"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

    @classmethod
    def get_scheme_type(cls, value: str):
        for item in cls:
            if (
                str(item.value).casefold() == value.casefold()
                or str(item.name).casefold() == value.casefold()
            ):
                return item
            return None

    @classmethod
    def get_response(cls):
        values = enumerate(iterable=(i.value for i in cls), start=1)
        response_values = [{"id": data[0], "category": data[1]} for data in values]
        return response_values

    @classmethod
    def get_scheme_type(cls, value: str):
        scheme_type = next(
            (i for i in cls if str(i.value).casefold() == value.casefold()), None
        )
        return scheme_type

    def __str__(self):
        return self.value


########################## MODELS #########################


class Payer(models.Model):
    name = models.CharField(max_length=256)
    address = models.CharField(max_length=256, blank=True, null=True)
    mobile_number = models.CharField(max_length=256, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Payers"

    def __str__(self):
        return self.name


class PayerScheme(models.Model):
    name = models.CharField(max_length=256)
    price_list = models.ForeignKey(
        PriceList,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    payer = models.ForeignKey(Payer, on_delete=models.PROTECT)
    type = models.CharField(
        max_length=256,
        choices=PayerSchemeType.choices(),
        default=PayerSchemeType.SELF_PREPAID.value,
    )
    created_by = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Payer Schemes"

    def __str__(self):
        return self.name
