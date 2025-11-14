# festival/templatetags/custom_filters.py
from django import template
register = template.Library()

@register.filter
def get_by_id(queryset, id):
    return queryset.filter(id=id).first()

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None