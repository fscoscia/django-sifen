"""
URLs para la API REST de SIFEN.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from django_sifen_api.views import (
    DocumentoElectronicoViewSet,
    ConsultaRUCViewSet,
    ValidacionViewSet,
    ConfiguracionSIFENViewSet,
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'documentos', DocumentoElectronicoViewSet, basename='documento')
router.register(r'consultas/ruc', ConsultaRUCViewSet, basename='consulta-ruc')
router.register(r'validaciones', ValidacionViewSet, basename='validacion')
router.register(r'configuraciones', ConfiguracionSIFENViewSet, basename='configuracion')

app_name = 'django_sifen_api'

urlpatterns = [
    path('api/', include(router.urls)),
]
