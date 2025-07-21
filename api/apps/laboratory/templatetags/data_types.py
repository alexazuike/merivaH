from django import template

register = template.Library()


@register.filter()
def to_float(value):
    return float(value)


@register.filter()
def get_dict_value(some_dict: dict, key):
    return some_dict.get(key, "")
