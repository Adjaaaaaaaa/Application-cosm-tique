"""
Template tags et filtres pour l'application scans.
"""

import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def to_json(value):
    """Convertit une valeur Python en JSON pour JavaScript."""
    return mark_safe(json.dumps(value))

@register.filter
def escape_json(value):
    """Échappe une valeur pour l'utilisation dans du JavaScript."""
    return json.dumps(value)
