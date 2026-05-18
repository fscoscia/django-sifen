"""
Formateadores para datos SIFEN.

Proporciona funciones para formatear RUC, números de documento, etc.
"""

from typing import Optional, Tuple
from decimal import Decimal


def formatear_ruc(ruc: str, dv: str) -> str:
    """
    Formatea un RUC con su dígito verificador.

    Args:
        ruc: RUC sin dígito verificador.
        dv: Dígito verificador.

    Returns:
        RUC formateado (ej: "80012345-6").
    """
    return f"{ruc}-{dv}"


def formatear_numero_documento(est: str, punto: str, numero: str) -> str:
    """
    Formatea un número de documento electrónico.

    Args:
        est: Establecimiento (3 dígitos).
        punto: Punto de expedición (3 dígitos).
        numero: Número de documento (7 dígitos).

    Returns:
        Número formateado (ej: "001-001-0000001").
    """
    return f"{est}-{punto}-{numero}"


def formatear_moneda(valor: Decimal, simbolo: str = "Gs.") -> str:
    """
    Formatea un valor monetario.

    Args:
        valor: Valor a formatear.
        simbolo: Símbolo de moneda.

    Returns:
        Valor formateado (ej: "Gs. 1.000.000").
    """
    # Convertir a string con separador de miles
    valor_str = f"{valor:,.0f}".replace(",", ".")
    return f"{simbolo} {valor_str}"


def formatear_cdc(cdc: str) -> str:
    """
    Formatea un CDC para mejor legibilidad.

    Args:
        cdc: CDC de 44 caracteres.

    Returns:
        CDC formateado con guiones.
    """
    if len(cdc) != 44:
        return cdc

    # Formato: TT-EEE-PPP-NNNNNNN-C-DDDDDDDDDDDDDDDD-RRRRRRRRRR-V
    return (
        f"{cdc[0:2]}-"  # Tipo documento
        f"{cdc[2:5]}-"  # Establecimiento
        f"{cdc[5:8]}-"  # Punto expedición
        f"{cdc[8:15]}-"  # Número documento
        f"{cdc[15:16]}-"  # Tipo contribuyente
        f"{cdc[16:32]}-"  # Fecha/hora
        f"{cdc[32:42]}-"  # RUC
        f"{cdc[42:44]}"  # DV
    )


def limpiar_ruc(ruc: str) -> Tuple[str, str]:
    """
    Limpia y separa un RUC en número y DV.

    Args:
        ruc: RUC en cualquier formato.

    Returns:
        Tupla (ruc, dv).
    """
    # Remover espacios
    ruc = ruc.strip()

    # Si tiene guión, separar
    if "-" in ruc:
        parts = ruc.split("-")
        return parts[0], parts[1] if len(parts) > 1 else ""

    # Si no tiene guión, asumir que el último dígito es el DV
    if len(ruc) > 1:
        return ruc[:-1], ruc[-1]

    return ruc, ""


def formatear_telefono(telefono: str) -> str:
    """
    Formatea un número de teléfono paraguayo.

    Args:
        telefono: Número de teléfono.

    Returns:
        Teléfono formateado.
    """
    # Limpiar
    telefono = telefono.replace(" ", "").replace("-", "")

    # Si tiene código de área (021, 0981, etc.)
    if len(telefono) >= 9:
        # Formato: 0XXX-XXXXXX
        return f"{telefono[:4]}-{telefono[4:]}"
    elif len(telefono) >= 6:
        # Formato: XXX-XXX
        return f"{telefono[:3]}-{telefono[3:]}"

    return telefono


def normalizar_texto(texto: str, max_length: Optional[int] = None) -> str:
    """
    Normaliza un texto para SIFEN.

    Remueve caracteres especiales y limita longitud.

    Args:
        texto: Texto a normalizar.
        max_length: Longitud máxima (opcional).

    Returns:
        Texto normalizado.
    """
    # Remover espacios extras
    texto = " ".join(texto.split())

    # Limitar longitud si se especifica
    if max_length and len(texto) > max_length:
        texto = texto[:max_length]

    return texto
