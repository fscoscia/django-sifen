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
        return True, None

    def _validate_no_contribuyente(self) -> Tuple[bool, Optional[str]]:
        """Valida datos de receptor no contribuyente."""
        if self.iTiOpe == 1:
            return False, "Operación B2B (iTiOpe=1) solo es válida para contribuyentes"

        if self.iTiOpe == 4:
            return True, None

        if not self.iTipIDRec:
            return False, "No contribuyente debe tener tipo de documento (iTipIDRec)"

        if self.iTipIDRec not in [1, 2, 3, 4, 5, 6, 9]:
            return False, f"Tipo de documento inválido: {self.iTipIDRec}"

        if not self.dNumIDRec:
            return False, "No contribuyente debe tener número de documento (dNumIDRec)"

        return True, None

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida los datos del receptor."""
        if self.iNatRec not in [1, 2]:
            return False, f"Naturaleza del receptor inválida: {self.iNatRec}"

        if self.iTiOpe not in [1, 2, 3, 4, 9]:
            return False, f"Tipo de operación inválido: {self.iTiOpe}"

        if self.iNatRec == 1:
            return self._validate_contribuyente()

        return self._validate_no_contribuyente()
