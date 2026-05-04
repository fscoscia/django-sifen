"""
Configuración de la aplicación Django SIFEN API.
"""

from django.apps import AppConfig


class DjangoSifenApiConfig(AppConfig):
    """Configuración de la app django_sifen_api."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_sifen_api'
    verbose_name = 'SIFEN API'
    
    def ready(self):
        """Se ejecuta cuando la app está lista."""
        import django_sifen_api.signals
