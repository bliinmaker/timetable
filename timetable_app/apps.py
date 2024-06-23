"""
Configuration for the timetable application.

This module contains the AppConfig class definition for the timetable application.
"""

from django.apps import AppConfig


class TimetableAppConfig(AppConfig):
    """
    Configuration class for the timetable application.

    Inherits from Django's AppConfig to provide application-specific settings and configurations.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'timetable_app'
