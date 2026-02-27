"""
App configuration for tracker app.
"""

from django.apps import AppConfig


class TrackerConfig(AppConfig):
    """Configuration for tracker app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tracker'
