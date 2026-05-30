"""
Modelos para Notas de Crédito y Débito Electrónicas.

Grupo E5 - Campos específicos para NCE/NDE según Manual Técnico v150.
"""

from dataclasses import dataclass, field
from typing import Optional, Tuple

from .base import SifenObject


@dataclass
class NotaCreditoDebito(SifenObject):
    """
    Grupo E5 - Campos de la Nota de Crédito/Débito Electrónica (gCamNCDE).
    
    Obligatorio si iTiDE = 5 o 6 (NCE y NDE).
    No informar si iTiDE ≠ 5 o 6.
    
    Según Manual Técnico v150, sección E5 (E400-E499).
    """
    
    # E401 - Motivo de emisión
    iMotEmi: int = field(metadata={"required": True})
    
    # E402 - Descripción del motivo de emisión
    dDesMotEmi: str = field(metadata={"required": True})
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida los campos de nota de crédito/débito."""
        # Validar motivo de emisión (1-8)
        if self.iMotEmi not in [1, 2, 3, 4, 5, 6, 7, 8]:
            return False, f"Motivo de emisión inválido: {self.iMotEmi}"
        
        # Validar descripción según motivo
        descripciones_validas = {
            1: "Devolución y Ajuste de precios",
            2: "Devolución",
            3: "Descuento",
            4: "Bonificación",
            5: "Crédito incobrable",
            6: "Recupero de costo",
            7: "Recupero de gasto",
            8: "Ajuste de precio",
        }
        
        if self.dDesMotEmi != descripciones_validas.get(self.iMotEmi):
            return False, f"Descripción del motivo no corresponde al código {self.iMotEmi}. Debe ser: {descripciones_validas.get(self.iMotEmi)}"
        
        return True, None


# Constantes para motivos de emisión
MOTIVO_DEVOLUCION_AJUSTE = 1
MOTIVO_DEVOLUCION = 2
MOTIVO_DESCUENTO = 3
MOTIVO_BONIFICACION = 4
MOTIVO_CREDITO_INCOBRABLE = 5
MOTIVO_RECUPERO_COSTO = 6
MOTIVO_RECUPERO_GASTO = 7
MOTIVO_AJUSTE_PRECIO = 8

# Descripciones de motivos
DESCRIPCIONES_MOTIVOS = {
    MOTIVO_DEVOLUCION_AJUSTE: "Devolución y Ajuste de precios",
    MOTIVO_DEVOLUCION: "Devolución",
    MOTIVO_DESCUENTO: "Descuento",
    MOTIVO_BONIFICACION: "Bonificación",
    MOTIVO_CREDITO_INCOBRABLE: "Crédito incobrable",
    MOTIVO_RECUPERO_COSTO: "Recupero de costo",
    MOTIVO_RECUPERO_GASTO: "Recupero de gasto",
    MOTIVO_AJUSTE_PRECIO: "Ajuste de precio",
}
