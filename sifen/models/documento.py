"""
Modelo principal del Documento Electrónico.

Basado en DocumentoElectronico.java de la librería Java.
"""

from typing import Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from sifen.models.base import (
    SifenObject,
    IdentificacionDE,
    DatosGeneralesDE,
)
from sifen.models.emisor import Emisor
from sifen.models.receptor import Receptor
from sifen.models.items import Item
from sifen.models.totales import Totales, CondicionOperacion
from sifen.models.nota_credito_debito import NotaCreditoDebito
from sifen.models.documento_asociado import DocumentoAsociado


@dataclass
class DocumentoElectronico(SifenObject):
    """
    Documento Electrónico (DE) completo para SIFEN.

    Representa la estructura completa de un DE según el Manual Técnico v150.
    Este es el objeto principal que se firma y envía a SIFEN.
    """

    # A - Campos de identificación del DE
    gTimb: IdentificacionDE = field(metadata={"required": True})

    # B - Datos generales de la operación
    gDatGralOpe: DatosGeneralesDE = field(metadata={"required": True})

    # D - Datos del emisor
    gEmis: Emisor = field(metadata={"required": True})

    # E - Datos del receptor
    gDatRec: Receptor = field(metadata={"required": True})

    # F - Totales de la operación
    gTotSub: Totales = field(metadata={"required": True})

    # E600 - Condición de la operación (no requerido para NCE/NDE)
    gPaConEIni: Optional[CondicionOperacion] = None

    # Versión del formato del DE
    dVerFor: int = field(default=150, metadata={"required": True})

    # E - Items de la operación
    gCamItem: List[Item] = field(default_factory=list, metadata={"required": True})

    # E5 - Campos de Nota de Crédito/Débito (obligatorio si iTiDE = 5 o 6)
    gCamNCDE: Optional[NotaCreditoDebito] = None

    # H - Campos que identifican al documento asociado (obligatorio si iTiDE = 4, 5, 6)
    gCamDEAsoc: Optional[DocumentoAsociado] = None

    # ID del DE (para referencia en la firma)
    Id: str = field(default="", metadata={"required": True})

    # CDC - Código de Control (se genera después de crear el DE)
    CDC: Optional[str] = None

    def __post_init__(self):
        """Inicializa valores después de crear el objeto."""
        # Generar ID si no existe
        if not self.Id:
            self.Id = self._generate_id()

    def _generate_id(self) -> str:
        """
        Genera el ID del documento para la firma XML.

        Returns:
            ID único del documento.
        """
        # Formato: DE + timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"DE{timestamp}"

    def generate_cdc(self) -> str:
        """
        Genera el Código de Control (CDC) del documento según especificación SIFEN.

        El CDC es un código de 44 caracteres (43 + 1 DV) que identifica únicamente al DE.
        Formato según librería Java oficial:
        TT + RRRRRRRR + D + EEE + PPP + NNNNNNN + C + FFFFFFFF + E + SSSSSSSSS + V

        Donde:
        - TT: Tipo de documento (2 dígitos)
        - RRRRRRRR: RUC emisor sin DV (8 dígitos, con ceros a la izquierda)
        - D: Dígito verificador del RUC (1 dígito)
        - EEE: Establecimiento (3 dígitos)
        - PPP: Punto de expedición (3 dígitos)
        - NNNNNNN: Número de documento (7 dígitos)
        - C: Tipo de contribuyente (1 dígito)
        - FFFFFFFF: Fecha de emisión YYYYMMDD (8 dígitos, solo fecha sin hora)
        - E: Tipo de emisión (1 dígito)
        - SSSSSSSSS: Código de seguridad (9 dígitos)
        - V: Dígito verificador (1 dígito)

        Returns:
            CDC generado.
        """
        # TT - Tipo de documento (2 dígitos)
        tipo_doc = str(self.gTimb.iTiDE).zfill(2)

        # RRRRRRRR - RUC del emisor sin DV (8 dígitos, con ceros a la izquierda)
        ruc_sin_dv = (
            self.gEmis.dRucEm.split("-")[0]
            if "-" in self.gEmis.dRucEm
            else self.gEmis.dRucEm
        )
        ruc = ruc_sin_dv.zfill(8)

        # D - Dígito verificador del RUC (1 dígito)
        dv_ruc = str(self.gEmis.dDVEmi)

        # EEE - Establecimiento (3 dígitos)
        establecimiento = self.gTimb.dEst

        # PPP - Punto de expedición (3 dígitos)
        punto_exp = self.gTimb.dPunExp

        # NNNNNNN - Número de documento (7 dígitos)
        numero_doc = self.gTimb.dNumDoc

        # C - Tipo de contribuyente (1 dígito)
        tipo_contrib = str(self.gEmis.iTipCont)

        # FFFFFFFF - Fecha de emisión (8 dígitos: YYYYMMDD, solo fecha sin hora)
        fecha_emision = self.gDatGralOpe.dFeEmiDE.strftime("%Y%m%d")

        # E - Tipo de emisión (1 dígito)
        tipo_emision = str(self.gDatGralOpe.iTipEmi)

        # SSSSSSSSS - Código de seguridad (9 dígitos)
        codigo_seg = str(self.gDatGralOpe.dCodSeg).zfill(9)

        # Concatenar todo (sin DV todavía)
        cdc_sin_dv = (
            tipo_doc
            + ruc
            + dv_ruc
            + establecimiento
            + punto_exp
            + numero_doc
            + tipo_contrib
            + fecha_emision
            + tipo_emision
            + codigo_seg
        )

        # Validar longitud del CDC sin DV (debe ser 43)
        if len(cdc_sin_dv) != 43:
            error_msg = (
                f"CDC sin DV debe tener 43 dígitos, tiene {len(cdc_sin_dv)}: {cdc_sin_dv}\n"
                f"  Tipo doc: {tipo_doc} ({len(tipo_doc)} dígitos)\n"
                f"  Establecimiento: {establecimiento} ({len(establecimiento)} dígitos)\n"
                f"  Punto exp: {punto_exp} ({len(punto_exp)} dígitos)\n"
                f"  Número doc: {numero_doc} ({len(numero_doc)} dígitos)\n"
                f"  Tipo contrib: {tipo_contrib} ({len(tipo_contrib)} dígitos)\n"
                f"  Fecha: {fecha_emision} ({len(fecha_emision)} dígitos)\n"
                f"  RUC: {ruc} ({len(ruc)} dígitos)"
            )
            raise ValueError(error_msg)

        # Calcular dígito verificador
        dv = self._calculate_dv(cdc_sin_dv)

        # CDC completo
        cdc = cdc_sin_dv + str(dv)

        # Validar longitud del CDC completo (debe ser 44)
        if len(cdc) != 44:
            raise ValueError(f"CDC debe tener 44 dígitos, tiene {len(cdc)}: {cdc}")

        # Guardar CDC
        self.CDC = cdc

        return cdc

    def _calculate_dv(self, base: str) -> int:
        """
        Calcula el dígito verificador del CDC usando módulo 11.

        Algoritmo según la librería Java oficial de SIFEN.

        Args:
            base: String base para calcular el DV.

        Returns:
            Dígito verificador (0-9).
        """
        # Algoritmo módulo 11 base 2-11 (según librería Java)
        base_max = 11
        suma = 0
        multiplicador = 2

        # Recorrer de derecha a izquierda
        for digit in reversed(base):
            # Reiniciar multiplicador cuando supera base_max
            if multiplicador > base_max:
                multiplicador = 2

            suma += int(digit) * multiplicador
            multiplicador += 1

        # Calcular DV según algoritmo de la librería Java oficial
        resto = suma % 11

        # Si resto > 1: DV = 11 - resto
        # Si resto <= 1: DV = 0
        if resto > 1:
            dv = 11 - resto
        else:
            dv = 0

        return dv

    def validate(self) -> Tuple[bool, Optional[str]]:
        """
        Valida el documento electrónico completo.

        Returns:
            Tupla (es_valido, mensaje_error).
        """
        # Validar identificación
        is_valid, error = self.gTimb.validate()
        if not is_valid:
            return False, f"Error en identificación: {error}"

        # Validar datos generales
        is_valid, error = self.gDatGralOpe.validate()
        if not is_valid:
            return False, f"Error en datos generales: {error}"

        # Validar emisor
        is_valid, error = self.gEmis.validate()
        if not is_valid:
            return False, f"Error en emisor: {error}"

        # Validar receptor
        is_valid, error = self.gDatRec.validate()
        if not is_valid:
            return False, f"Error en receptor: {error}"

        # Validar que tenga al menos un ítem
        if not self.gCamItem:
            return False, "El documento debe tener al menos un ítem"

        # Validar cada ítem
        for i, item in enumerate(self.gCamItem, 1):
            is_valid, error = item.validate()
            if not is_valid:
                return False, f"Error en ítem {i}: {error}"

        # Validar totales
        is_valid, error = self.gTotSub.validate()
        if not is_valid:
            return False, f"Error en totales: {error}"

        # Validar condición de operación (si existe)
        if self.gPaConEIni:
            is_valid, error = self.gPaConEIni.validate()
            if not is_valid:
                return False, f"Error en condición de operación: {error}"

        return True, None

    def to_dict(self) -> dict:
        """
        Convierte el DE a diccionario.

        Returns:
            Diccionario con todos los datos del DE.
        """
        data = super().to_dict()

        # Agregar CDC si existe
        if self.CDC:
            data["CDC"] = self.CDC

        return data
