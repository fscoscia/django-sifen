"""
Modelos para totales y subtotales del Documento Electrónico.

Basado en TgTotSub.java (Grupo F) de la librería Java.
"""

from typing import Optional, List, Tuple
from dataclasses import dataclass, field
from decimal import Decimal

from sifen.models.base import SifenObject


@dataclass
class SubtotalIVA(SifenObject):
    """
    Grupo F008 - Subtotales por cada tasa de IVA (gCamIVA).
    """

    # F009 - Código de la tasa de IVA
    iAfecIVA: int = field(metadata={"required": True})

    # F011 - Base gravada de la tasa de IVA
    dBasGravIVA: Decimal = field(metadata={"required": True})

    # F012 - Liquidación de IVA de la tasa
    dLiqIVA: Decimal = field(metadata={"required": True})

    # F010 - Descripción de la tasa de IVA (opcional)
    dDesAfecIVA: Optional[str] = None

    # F013 - Tasa efectiva del IVA (opcional)
    dTasaIVA: Optional[Decimal] = None


@dataclass
class Totales(SifenObject):
    """
    Grupo F - Campos que describen los subtotales y totales de la transacción (gTotSub).

    Según Manual Técnico v150, sección 4.7.
    """

    # F005 - Total de la operación
    dTotOpe: Decimal = field(metadata={"required": True})

    # F013 - Total general de la operación
    dTotGralOpe: Decimal = field(metadata={"required": True})

    # F009 - Total de IVA liquidado
    dTotIVA: Decimal = field(default=Decimal("0"), metadata={"required": True})

    # F016 - Código de moneda
    cMoneOpe: str = field(default="PYG", metadata={"required": True})

    # F008 - Subtotales por tasa de IVA
    gCamIVA: List[SubtotalIVA] = field(default_factory=list)

    # F001 - Subtotal de la operación exenta (opcional)
    dSubExe: Optional[Decimal] = None

    # F002 - Subtotal de la operación exonerada (opcional)
    dSubExo: Optional[Decimal] = None

    # F003 - Subtotal de la operación gravada 5% (opcional)
    dSub5: Optional[Decimal] = None

    # F004 - Subtotal de la operación gravada 10% (opcional)
    dSub10: Optional[Decimal] = None

    # F006 - Total de descuentos (opcional)
    dTotDesc: Optional[Decimal] = None

    # Total de descuentos globales por ítem (opcional)
    dTotDescGlotem: Optional[Decimal] = None

    # Total de anticipos por ítem (opcional)
    dTotAntItem: Optional[Decimal] = None

    # F007 - Total de anticipos (opcional)
    dTotAnt: Optional[Decimal] = None

    # Porcentaje de descuento total (opcional)
    dPorcDescTotal: Optional[Decimal] = None

    # Descuento total (opcional)
    dDescTotal: Optional[Decimal] = None

    # Anticipo (opcional)
    dAnticipo: Optional[Decimal] = None

    # Redondeo (opcional)
    dRedon: Optional[Decimal] = None

    # IVA 5% (opcional)
    dIVA5: Optional[Decimal] = None

    # IVA 10% (opcional)
    dIVA10: Optional[Decimal] = None

    # Base gravada 5% (opcional)
    dBaseGrav5: Optional[Decimal] = None

    # Base gravada 10% (opcional)
    dBaseGrav10: Optional[Decimal] = None

    # Total base gravada IVA (opcional)
    dTBasGraIVA: Optional[Decimal] = None

    # F010 - Liquidación total de IVA 5% (opcional)
    dLiqTotIVA5: Optional[Decimal] = None

    # F011 - Liquidación total de IVA 10% (opcional)
    dLiqTotIVA10: Optional[Decimal] = None

    # F012 - Total de IVA de la operación (opcional)
    dIVAComi: Optional[Decimal] = None

    # F014 - Total en moneda extranjera (opcional)
    dTotOpeMe: Optional[Decimal] = None

    # F015 - Total general en moneda extranjera (opcional)
    dTotGralOpeMe: Optional[Decimal] = None

    # F017 - Descripción de la moneda (opcional)
    dDesMoneOpe: Optional[str] = None

    # F018 - Condición de anticipo (opcional)
    dCondTiCam: Optional[Decimal] = None

    # F019 - Tipo de cambio (opcional)
    dTiCam: Optional[Decimal] = None

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida los totales."""
        # Validar total de operación
        if self.dTotOpe < 0:
            return False, f"Total de operación inválido: {self.dTotOpe}"

        # Validar total general
        if self.dTotGralOpe < 0:
            return False, f"Total general inválido: {self.dTotGralOpe}"

        # Validar que total general >= total operación
        if self.dTotGralOpe < self.dTotOpe:
            return False, "Total general debe ser mayor o igual al total de operación"

        # Validar código de moneda
        if not self.cMoneOpe or len(self.cMoneOpe) != 3:
            return False, f"Código de moneda inválido: {self.cMoneOpe}"

        return True, None


@dataclass
class Pago(SifenObject):
    """
    Grupo E605 - Campos que describen la forma de pago de la operación (gPaConEIni).
    """

    # E606 - Condición de la operación
    iTiPago: int = field(metadata={"required": True})

    # E607 - Descripción de la condición
    dDesTiPag: Optional[str] = None

    # E608 - Monto de la operación
    dMonTiPag: Optional[Decimal] = None

    # E609 - Código de moneda de pago
    cMoneTiPag: Optional[str] = None

    # E610 - Descripción de la moneda de pago
    dDesMoneTiPag: Optional[str] = None

    # E611 - Tipo de cambio
    dTiCamTiPag: Optional[Decimal] = None

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida los datos del pago."""
        # Validar tipo de pago
        if self.iTiPago not in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            return False, f"Tipo de pago inválido: {self.iTiPago}"

        return True, None


@dataclass
class Cuota(SifenObject):
    """
    Grupo E640 - Campos que describen las cuotas (gCuotas).
    """

    # E641 - Código de moneda de la cuota
    cMoneCuo: str = field(metadata={"required": True})

    # E643 - Monto de la cuota
    dMonCuota: Decimal = field(metadata={"required": True})

    # E642 - Descripción de la moneda de la cuota (opcional)
    dDMoneCuo: Optional[str] = None

    # E644 - Vencimiento de la cuota (opcional)
    dVencCuo: Optional[str] = None

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida los datos de la cuota."""
        # Validar monto
        if self.dMonCuota <= 0:
            return False, f"Monto de cuota inválido: {self.dMonCuota}"

        # Validar código de moneda
        if not self.cMoneCuo or len(self.cMoneCuo) != 3:
            return False, f"Código de moneda inválido: {self.cMoneCuo}"

        return True, None


@dataclass
class CondicionOperacion(SifenObject):
    """
    Grupo E600 - Campos que describen la condición de la operación (gPaConEIni).

    Según Manual Técnico v150, sección 4.6.
    """

    # E601 - Condición de la operación
    iCondOpe: int = field(metadata={"required": True})

    # E602 - Descripción de la condición
    dDesCondOpe: Optional[str] = None

    # E605 - Pagos
    gPaConEIni: List[Pago] = field(default_factory=list)

    # E640 - Cuotas (si es crédito)
    gCuotas: List[Cuota] = field(default_factory=list)

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida la condición de operación."""
        # Validar condición
        if self.iCondOpe not in [1, 2]:
            return False, f"Condición de operación inválida: {self.iCondOpe}"

        # Si es contado (1), debe tener al menos un pago
        if self.iCondOpe == 1 and not self.gPaConEIni:
            return False, "Operación al contado debe tener al menos una forma de pago"

        # Si es crédito (2), debe tener cuotas
        if self.iCondOpe == 2 and not self.gCuotas:
            return False, "Operación a crédito debe tener cuotas"

        return True, None
