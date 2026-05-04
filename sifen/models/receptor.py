"""
Modelos para datos del receptor del Documento Electrónico.

Basado en TgDatRec.java (Grupo E) de la librería Java.
"""

from typing import Optional
from dataclasses import dataclass, field

from sifen.models.base import SifenObject


@dataclass
class Receptor(SifenObject):
    """
    Grupo E - Campos que identifican al receptor del Documento Electrónico (gDatRec).
    
    Según Manual Técnico v150, sección 4.5.
    """
    
    # E001 - Naturaleza del receptor
    iNatRec: int = field(metadata={'required': True})
    
    # E002 - Descripción de la naturaleza del receptor
    dDesNatRec: Optional[str] = None
    
    # E003 - Tipo de operación
    iTiOpe: int = field(metadata={'required': True})
    
    # E004 - Descripción del tipo de operación
    dDesTiOpe: Optional[str] = None
    
    # E005 - Código de país del receptor (opcional)
    cPaisRec: Optional[str] = None
    
    # E006 - Descripción del país del receptor
    dDesPaisRe: Optional[str] = None
    
    # E007 - Tipo de documento de identidad
    iTiContRec: Optional[int] = None
    
    # E008 - Descripción del tipo de documento
    dDesTiContRec: Optional[str] = None
    
    # E009 - Número de documento del receptor
    dNumIDRec: Optional[str] = None
    
    # E010 - Nombre o razón social del receptor
    dNomRec: str = field(metadata={'required': True})
    
    # E011 - Nombre de fantasía del receptor
    dNomFanRec: Optional[str] = None
    
    # E012 - Dirección del receptor
    dDirRec: Optional[str] = None
    
    # E013 - Número de casa
    dNumCasRec: Optional[int] = None
    
    # E014 - Código de departamento
    cDepRec: Optional[int] = None
    
    # E015 - Descripción del departamento
    dDesDepRec: Optional[str] = None
    
    # E016 - Código de distrito
    cDisRec: Optional[int] = None
    
    # E017 - Descripción del distrito
    dDesDisRec: Optional[str] = None
    
    # E018 - Código de ciudad
    cCiuRec: Optional[int] = None
    
    # E019 - Descripción de la ciudad
    dDesCiuRec: Optional[str] = None
    
    # E020 - Teléfono del receptor
    dTelRec: Optional[str] = None
    
    # E021 - Correo electrónico del receptor
    dEmailRec: Optional[str] = None
    
    # E022 - Código de cliente (opcional)
    dCodCliente: Optional[str] = None
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Valida los datos del receptor."""
        # Validar naturaleza del receptor
        if self.iNatRec not in [1, 2]:
            return False, f"Naturaleza del receptor inválida: {self.iNatRec}"
        
        # Validar tipo de operación
        if self.iTiOpe not in [1, 2, 3, 4]:
            return False, f"Tipo de operación inválido: {self.iTiOpe}"
        
        # Si es contribuyente (naturaleza 1), debe tener documento
        if self.iNatRec == 1 and not self.dNumIDRec:
            return False, "Receptor contribuyente debe tener número de documento"
        
        return True, None
