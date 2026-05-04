"""
Utilidades para SIFEN.

Proporciona validadores, calculadoras y formateadores.
"""

from sifen.utils.validators import (
    validar_ruc,
    calcular_dv_ruc,
    validar_cdc,
    calcular_dv_cdc,
    validar_email,
    validar_telefono,
    validar_codigo_seguridad,
)

from sifen.utils.calculators import (
    calcular_iva_item,
    calcular_valor_item,
    calcular_totales,
    redondear_moneda,
    calcular_precio_con_iva,
    calcular_precio_sin_iva,
)

from sifen.utils.formatters import (
    formatear_ruc,
    formatear_numero_documento,
    formatear_moneda,
    formatear_cdc,
    limpiar_ruc,
    formatear_telefono,
    normalizar_texto,
)


__all__ = [
    # Validadores
    "validar_ruc",
    "calcular_dv_ruc",
    "validar_cdc",
    "calcular_dv_cdc",
    "validar_email",
    "validar_telefono",
    "validar_codigo_seguridad",
    # Calculadoras
    "calcular_iva_item",
    "calcular_valor_item",
    "calcular_totales",
    "redondear_moneda",
    "calcular_precio_con_iva",
    "calcular_precio_sin_iva",
    # Formateadores
    "formatear_ruc",
    "formatear_numero_documento",
    "formatear_moneda",
    "formatear_cdc",
    "limpiar_ruc",
    "formatear_telefono",
    "normalizar_texto",
]
