
from django import template

register = template.Library()

@register.simple_tag
def get_field_verbosename(obj, fieldName):
    return obj.model._meta.get_field(fieldName).verbose_name