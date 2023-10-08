"""
Это шаблонный фильтр model_name. Его можно применять в шаблонах как
object|model_name, чтобы получать для объекта его модельное имя.
"""

from django import template

register = template.Library()


@register.filter
def model_name(obj):
    try:
        return obj._meta.model_name
    except AttributeError:
        return None
