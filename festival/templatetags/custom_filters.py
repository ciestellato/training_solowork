# festival/templatetags/custom_filters.py
from django import template
register = template.Library()

@register.filter
def get_by_id(queryset, id):
    return queryset.filter(id=id).first()