"""
Django app configuration for core domain layer.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration for core domain layer."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core Domain Layer'
    
    def ready(self):
        """Initialize core domain layer when Django starts."""
        pass
