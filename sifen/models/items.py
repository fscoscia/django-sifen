"""
Modelos para ítems/productos del Documento Electrónico.

Basado en TgCamItem.java (Grupo E) de la librería Java.
"""

from typing import Optional
from dataclasses import dataclass, field
from decimal import Decimal

from sifen.models.base import SifenObject


@dataclass
class IVAItem(SifenObject):
    """
    Grupo E720 - Campos que describen el IVA de la operación por ítem (gCamIVA).
    """
    
    # E721 - Tasa de IVA
    iAfecIVA: int = field(metadata={'required': True})
    
    # E722 - Descripción de la tasa de IVA
    dDesAfecIVA: Optional[str] = None
    
    # E723 - Proporción de IVA
    dPropIVA: Decimal = field(default=Decimal('100'), metadata={'required': True})
    
    # E724 - Tasa efectiva del IVA
    dTasaIVA: Decimal = field(metadata={'required': True})
    
    # E725 - Base gravada
    dBasGravIVA: Decimal = field(metadata={'required': True})
    
    # E726 - Liquidación del IVA
    dLiqIVAItem: Decimal = field(metadata={'required': True})
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Valida los datos del IVA."""
        # Validar afectación de IVA
        if self.iAfecIVA not in [1, 2, 3, 4]:
            return False, f"Afectación de IVA inválida: {self.iAfecIVA}"
        
        # Validar proporción (0-100)
        if self.dPropIVA < 0 or self.dPropIVA > 100:
            return False, f"Proporción de IVA inválida: {self.dPropIVA}"
        
        # Validar tasa de IVA
        if self.dTasaIVA < 0:
            return False, f"Tasa de IVA inválida: {self.dTasaIVA}"
        
        return True, None


@dataclass
class ValorItem(SifenObject):
    """
    Grupo E700 - Campos que describen el valor de la operación por ítem (gValorItem).
    """
    
    # E701 - Precio unitario
    dPUniProSer: Decimal = field(metadata={'required': True})
    
    # E702 - Código de tipo de precio (opcional)
    cTipVTa: Optional[int] = None
    
    # E703 - Descripción del tipo de precio
    dDesTipVTa: Optional[str] = None
    
    # E704 - Precio unitario con descuento
    dPUniProSerDes: Optional[Decimal] = None
    
    # E705 - Descuento particular por ítem
    dDescItem: Optional[Decimal] = None
    
    # E706 - Porcentaje de descuento
    dPorcDesIt: Optional[Decimal] = None
    
    # E707 - Descuento global por ítem
    dDescGloItem: Optional[Decimal] = None
    
    # E708 - Anticipo global por ítem
    dAntPreUniIt: Optional[Decimal] = None
    
    # E709 - Anticipo particular por ítem
    dAntGloPreUniIt: Optional[Decimal] = None
    
    # E710 - Total de la operación por ítem
    dTotOpeItem: Decimal = field(metadata={'required': True})
    
    # E711 - Total de la operación por ítem con IVA
    dTotOpeGs: Optional[Decimal] = None
    
    # E720 - IVA del ítem
    gCamIVA: Optional[IVAItem] = None
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Valida los valores del ítem."""
        # Validar precio unitario
        if self.dPUniProSer <= 0:
            return False, f"Precio unitario inválido: {self.dPUniProSer}"
        
        # Validar total
        if self.dTotOpeItem < 0:
            return False, f"Total de operación inválido: {self.dTotOpeItem}"
        
        return True, None


@dataclass
class Item(SifenObject):
    """
    Grupo E - Campos que describen los ítems de la operación (gCamItem).
    
    Según Manual Técnico v150, sección 4.6.
    """
    
    # E601 - Código del ítem
    dCodInt: str = field(metadata={'required': True})
    
    # E602 - Código del producto SIFEN (opcional)
    dParAranc: Optional[str] = None
    
    # E603 - Código NCM (opcional)
    dNCM: Optional[str] = None
    
    # E604 - Código UNSPSC (opcional)
    dUNSPSC: Optional[str] = None
    
    # E605 - Código GTIN (opcional)
    dGTIN: Optional[str] = None
    
    # E606 - Código GTIN del paquete (opcional)
    dGTINPq: Optional[str] = None
    
    # E607 - Descripción del producto o servicio
    dDesProSer: str = field(metadata={'required': True})
    
    # E608 - Unidad de medida
    cUniMed: int = field(metadata={'required': True})
    
    # E609 - Descripción de la unidad de medida
    dDesUniMed: Optional[str] = None
    
    # E610 - Cantidad
    dCantProSer: Decimal = field(metadata={'required': True})
    
    # E611 - Código de país de origen (opcional)
    cPaisOrig: Optional[str] = None
    
    # E612 - Descripción del país de origen
    dDesPaisOrig: Optional[str] = None
    
    # E613 - Observación del ítem (opcional)
    dInfItem: Optional[str] = None
    
    # E614 - Código de relevancia (opcional)
    cRelMerc: Optional[int] = None
    
    # E615 - Descripción de relevancia
    dDesRelMerc: Optional[str] = None
    
    # E616 - Cantidad de paquetes (opcional)
    dCanQuiMer: Optional[Decimal] = None
    
    # E617 - Porcentaje de merma (opcional)
    dPorQuiMer: Optional[Decimal] = None
    
    # E618 - Código de CDC de anticipos (opcional)
    dCDCAnticipo: Optional[str] = None
    
    # E700 - Campos de valor del ítem
    gValorItem: ValorItem = field(metadata={'required': True})
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Valida los datos del ítem."""
        # Validar código interno
        if not self.dCodInt:
            return False, "Código interno del ítem es requerido"
        
        # Validar descripción
        if not self.dDesProSer or len(self.dDesProSer) < 3:
            return False, f"Descripción del ítem inválida: {self.dDesProSer}"
        
        # Validar unidad de medida
        if self.cUniMed <= 0:
            return False, f"Unidad de medida inválida: {self.cUniMed}"
        
        # Validar cantidad
        if self.dCantProSer <= 0:
            return False, f"Cantidad inválida: {self.dCantProSer}"
        
        # Validar valor del ítem
        if self.gValorItem:
            is_valid, error = self.gValorItem.validate()
            if not is_valid:
                return False, f"Error en valor del ítem: {error}"
        
        return True, None
