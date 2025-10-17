"""Sales app configuration."""
from django.apps import AppConfig


class SalesConfig(AppConfig):
    """Configuration for Sales app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sales'
    verbose_name = 'Sales Management'
