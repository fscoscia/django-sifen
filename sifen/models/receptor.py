"""
Modelos para datos del receptor del Documento Electrónico.

Basado en TgDatRec.java (Grupo E) de la librería Java.
"""

from typing import Optional, Tuple
from dataclasses import dataclass, field

from sifen.models.base import SifenObject


@dataclass
class Receptor(SifenObject):
    """
    Grupo E - Campos que identifican al receptor del Documento Electrónico (gDatRec).

    Según Manual Técnico v150, sección 4.5.
    """

    # E001 - Naturaleza del receptor
    iNatRec: int = field(metadata={"required": True})

    # E003 - Tipo de operación
    iTiOpe: int = field(metadata={"required": True})

    # E010 - Nombre o razón social del receptor
    dNomRec: str = field(metadata={"required": True})

    # E002 - Descripción de la naturaleza del receptor (opcional)
    dDesNatRec: Optional[str] = None

    # E004 - Descripción del tipo de operación (opcional)
    dDesTiOpe: Optional[str] = None

    # E005 - Código de país del receptor (opcional)
    cPaisRec: Optional[str] = None

    # E006 - Descripción del país del receptor (opcional)
    dDesPaisRe: Optional[str] = None

    # E007 - Tipo de contribuyente receptor (opcional)
    iTiContRec: Optional[int] = None

    # E008 - Descripción del tipo de contribuyente (opcional)
    dDesTiContRec: Optional[str] = None

    # E008-1 - RUC del receptor (para contribuyentes)
    dRucRec: Optional[str] = None

    # E008-2 - Dígito verificador del RUC (para contribuyentes)
    dDVRec: Optional[str] = None

    # E009 - Tipo de documento de identidad (para no contribuyentes)
    iTipIDRec: Optional[int] = None

    # E010 - Descripción del tipo de documento (para no contribuyentes)
    dDTipIDRec: Optional[str] = None

    # E011 - Número de documento del receptor (para no contribuyentes)
    dNumIDRec: Optional[str] = None

    # E011 - Nombre de fantasía del receptor (opcional)
    dNomFanRec: Optional[str] = None

    # E012 - Dirección del receptor (opcional)
    dDirRec: Optional[str] = None

    # E013 - Número de casa (opcional)
    dNumCasRec: Optional[int] = None

    # E014 - Código de departamento (opcional)
    cDepRec: Optional[int] = None

    # E015 - Descripción del departamento (opcional)
    dDesDepRec: Optional[str] = None

    # E016 - Código de distrito (opcional)
    cDisRec: Optional[int] = None

    # E017 - Descripción del distrito (opcional)
    dDesDisRec: Optional[str] = None

    # E018 - Código de ciudad (opcional)
    cCiuRec: Optional[int] = None

    # E019 - Descripción de la ciudad (opcional)
    dDesCiuRec: Optional[str] = None

    # E020 - Teléfono del receptor (opcional)
    dTelRec: Optional[str] = None

    # E021 - Correo electrónico del receptor (opcional)
    dEmailRec: Optional[str] = None

    # E022 - Código de cliente (opcional)
    dCodCliente: Optional[str] = None

    def _validate_contribuyente(self) -> Tuple[bool, Optional[str]]:
        """Valida datos de receptor contribuyente."""
        if not self.dRucRec:
            return False, "Receptor contribuyente debe tener RUC"

        # D210b (código 1334): si el receptor es contribuyente (iNatRec=1),
        # el número de documento de identidad no debe informarse.
        if self.dNumIDRec:
            return (
                False,
                "Receptor contribuyente no debe informar número de "
                "documento de identidad (dNumIDRec)",
            )

        return True, None

    def _validate_no_contribuyente(
        self, i_ti_de: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """Valida datos de receptor no contribuyente."""
        if self.iTiOpe == 1:
            return False, "Operación B2B (iTiOpe=1) solo es válida para contribuyentes"

        # D208g (código 1335): obligatorio si iNatRec=2, sin excepción por
        # iTiOpe. SIFEN rechaza los B2F (iTiOpe=4) que omiten este campo.
        if not self.iTipIDRec:
            return False, "No contribuyente debe tener tipo de documento (iTipIDRec)"

        if self.iTipIDRec not in [1, 2, 3, 4, 5, 6, 9]:
            return False, f"Tipo de documento inválido: {self.iTipIDRec}"

        # D208f (código 1333): el tipo de documento Innominado (5) solo es
        # válido cuando el tipo de operación es B2C (iTiOpe=2).
        if self.iTipIDRec == 5 and self.iTiOpe != 2:
            return (
                False,
                "El tipo de documento de identidad Innominado (5) solo es "
                "válido para operaciones B2C (iTiOpe=2)",
            )

        # D208e (código 1331): el receptor no puede ser Innominado (5) en
        # Notas de Crédito, Notas de Débito o Notas de Remisión (iTiDE 5, 6, 7).
        if self.iTipIDRec == 5 and i_ti_de in (5, 6, 7):
            return (
                False,
                "El receptor no puede ser Innominado (iTipIDRec=5) en Notas "
                "de Crédito, Débito o Remisión",
            )

        # D210 (código 1314): obligatorio si iNatRec=2 y iTiOpe≠4 (B2F).
        # En caso de receptor Innominado sin número informado, se completa
        # con "0" al generar el XML (ver xml/generator.py).
        if self.iTiOpe != 4 and not self.dNumIDRec:
            return False, "No contribuyente debe tener número de documento (dNumIDRec)"

        return True, None

    def validate(self, i_ti_de: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """
        Valida los datos del receptor.

        Args:
            i_ti_de: Tipo de Documento Electrónico (gTimb.iTiDE) del DE al
                que pertenece este receptor. Se usa para la validación
                D208e (código 1331). Si no se provee, esa validación se omite.
        """
        if self.iNatRec not in [1, 2]:
            return False, f"Naturaleza del receptor inválida: {self.iNatRec}"

        if self.iTiOpe not in [1, 2, 3, 4, 9]:
            return False, f"Tipo de operación inválido: {self.iTiOpe}"

        if self.iNatRec == 1:
            return self._validate_contribuyente()

        return self._validate_no_contribuyente(i_ti_de)
