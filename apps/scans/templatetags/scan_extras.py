"""
Template tags and filters for the scans application.
"""

import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def to_json(value):
    """Convert a Python value to JSON for JavaScript."""
    return mark_safe(json.dumps(value))

@register.filter
def escape_json(value):
    """Escape a value for use in JavaScript."""
    return json.dumps(value)
