"""
Configuration de l'application tracker.
"""

from django.apps import AppConfig


class TrackerConfig(AppConfig):
    """Configuration de l'application tracker."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tracker'
