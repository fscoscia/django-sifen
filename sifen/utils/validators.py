"""
Validadores para datos SIFEN.

Proporciona funciones para validar RUC, CDC, y otros datos.
"""

import re
from typing import Optional


def validar_ruc(ruc: str, dv: Optional[str] = None) -> bool:
    """
    Valida un RUC paraguayo.
    
    Args:
        ruc: RUC sin dígito verificador o con formato "XXXXXXXX-X".
        dv: Dígito verificador (opcional si ruc incluye formato completo).
    
    Returns:
        True si el RUC es válido.
    """
    # Si viene con formato "XXXXXXXX-X", separar
    if '-' in ruc:
        parts = ruc.split('-')
        if len(parts) != 2:
            return False
        ruc = parts[0]
        dv = parts[1]
    
    # Validar que sea numérico
    if not ruc.isdigit():
        return False
    
    # Validar longitud (puede ser de 1 a 8 dígitos)
    if len(ruc) < 1 or len(ruc) > 8:
        return False
    
    # Si se proporcionó DV, validar
    if dv is not None:
        if not dv.isdigit() or len(dv) != 1:
            return False
        
        # Calcular DV esperado
        dv_calculado = calcular_dv_ruc(ruc)
        return dv == str(dv_calculado)
    
    return True


def calcular_dv_ruc(ruc: str) -> int:
    """
    Calcula el dígito verificador de un RUC.
    
    Algoritmo: módulo 11 base 2-9.
    
    Args:
        ruc: RUC sin dígito verificador.
    
    Returns:
        Dígito verificador (0-9).
    """
    # Asegurar que sea string numérico
    ruc = str(ruc).strip()
    
    # Completar con ceros a la izquierda hasta 8 dígitos
    ruc = ruc.zfill(8)
    
    # Algoritmo módulo 11 base 2-9
    suma = 0
    multiplicador = 2
    
    # Recorrer de derecha a izquierda
    for digit in reversed(ruc):
        suma += int(digit) * multiplicador
        multiplicador += 1
        if multiplicador > 9:
            multiplicador = 2
    
    # Calcular DV
    resto = suma % 11
    dv = 11 - resto
    
    # Si DV es 10 u 11, se usa 0
    if dv >= 10:
        dv = 0
    
    return dv


def validar_cdc(cdc: str) -> bool:
    """
    Valida un Código de Control (CDC).
    
    El CDC debe tener 44 caracteres numéricos.
    
    Args:
        cdc: Código de Control.
    
    Returns:
        True si el CDC es válido.
    """
    if not cdc:
        return False
    
    # Debe tener exactamente 44 caracteres
    if len(cdc) != 44:
        return False
    
    # Debe ser numérico
    if not cdc.isdigit():
        return False
    
    # Validar dígito verificador (último dígito)
    base = cdc[:43]
    dv = int(cdc[43])
    
    dv_calculado = calcular_dv_cdc(base)
    
    return dv == dv_calculado


def calcular_dv_cdc(base: str) -> int:
    """
    Calcula el dígito verificador de un CDC.
    
    Algoritmo: módulo 11 base 2-9.
    
    Args:
        base: CDC sin dígito verificador (43 caracteres).
    
    Returns:
        Dígito verificador (0-9).
    """
    suma = 0
    multiplicador = 2
    
    # Recorrer de derecha a izquierda
    for digit in reversed(base):
        suma += int(digit) * multiplicador
        multiplicador += 1
        if multiplicador > 9:
            multiplicador = 2
    
    # Calcular DV
    resto = suma % 11
    dv = 11 - resto
    
    # Si DV es 10 u 11, se usa 0
    if dv >= 10:
        dv = 0
    
    return dv


def validar_email(email: str) -> bool:
    """
    Valida un email.
    
    Args:
        email: Dirección de email.
    
    Returns:
        True si el email es válido.
    """
    if not email:
        return False
    
    # Patrón básico de email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validar_telefono(telefono: str) -> bool:
    """
    Valida un número de teléfono paraguayo.
    
    Args:
        telefono: Número de teléfono.
    
    Returns:
        True si el teléfono es válido.
    """
    if not telefono:
        return False
    
    # Remover espacios y guiones
    telefono_limpio = telefono.replace(' ', '').replace('-', '')
    
    # Debe tener entre 6 y 15 dígitos
    if not telefono_limpio.isdigit():
        return False
    
    if len(telefono_limpio) < 6 or len(telefono_limpio) > 15:
        return False
    
    return True


def validar_codigo_seguridad(codigo: str) -> bool:
    """
    Valida el código de seguridad del DE.
    
    Debe ser numérico de 9 dígitos.
    
    Args:
        codigo: Código de seguridad.
    
    Returns:
        True si es válido.
    """
    if not codigo:
        return False
    
    # Debe tener exactamente 9 dígitos
    if len(codigo) != 9:
        return False
    
    # Debe ser numérico
    return codigo.isdigit()
