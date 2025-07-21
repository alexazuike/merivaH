from django import template

register = template.Library()


@register.filter()
def split(sentence: str, sep: str):
    return sentence.split(sep=sep)
