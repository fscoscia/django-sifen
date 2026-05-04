"""
Modelos para datos del emisor del Documento Electrónico.

Basado en TgEmis.java (Grupo D) de la librería Java.
"""

from typing import Optional, List
from dataclasses import dataclass, field

from sifen.models.base import SifenObject, Direccion, ActividadEconomica


@dataclass
class ResponsableDE(SifenObject):
    """
    Grupo D010 - Responsable de la generación del DE (gRespDE).
    """
    
    # D011 - Tipo de contribuyente del responsable
    iTipIDRespDE: int = field(metadata={'required': True})
    
    # D012 - Descripción del tipo de documento
    dDTipIDRespDE: Optional[str] = None
    
    # D013 - Número de documento del responsable
    dNumIDRespDE: str = field(metadata={'required': True})
    
    # D014 - Nombre del responsable
    dNomRespDE: str = field(metadata={'required': True})
    
    # D015 - Cargo del responsable
    dCarRespDE: Optional[str] = None


@dataclass
class Emisor(SifenObject):
    """
    Grupo D - Campos que identifican al emisor del Documento Electrónico (gEmis).
    
    Según Manual Técnico v150, sección 4.4.
    """
    
    # D001 - RUC del emisor
    dRucEm: str = field(metadata={'required': True})
    
    # D002 - Dígito verificador del RUC
    dDVEmi: int = field(metadata={'required': True})
    
    # D003 - Tipo de contribuyente
    iTipCont: int = field(metadata={'required': True})
    
    # D004 - Descripción del tipo de contribuyente
    dDesTipCont: Optional[str] = None
    
    # D005 - Tipo de régimen (opcional)
    cTipReg: Optional[int] = None
    
    # D006 - Descripción del tipo de régimen
    dDesTipReg: Optional[str] = None
    
    # D007 - Nombre o razón social del emisor
    dNomEmi: str = field(metadata={'required': True})
    
    # D008 - Nombre de fantasía
    dNomFanEmi: Optional[str] = None
    
    # D009 - Dirección del emisor
    dDirEmi: str = field(metadata={'required': True})
    
    # D010 - Número de casa
    dNumCas: Optional[int] = None
    
    # D011 - Complemento de dirección 1
    dCompDir1: Optional[str] = None
    
    # D012 - Complemento de dirección 2
    dCompDir2: Optional[str] = None
    
    # D013 - Código de departamento
    cDepEmi: int = field(metadata={'required': True})
    
    # D014 - Descripción del departamento
    dDesDepEmi: Optional[str] = None
    
    # D015 - Código de distrito
    cDisEmi: int = field(metadata={'required': True})
    
    # D016 - Descripción del distrito
    dDesDisEmi: Optional[str] = None
    
    # D017 - Código de ciudad
    cCiuEmi: int = field(metadata={'required': True})
    
    # D018 - Descripción de la ciudad
    dDesCiuEmi: Optional[str] = None
    
    # D019 - Teléfono del emisor
    dTelEmi: str = field(metadata={'required': True})
    
    # D020 - Correo electrónico del emisor
    dEmailE: str = field(metadata={'required': True})
    
    # D021 - Denominación de la sucursal (opcional)
    dDenSuc: Optional[str] = None
    
    # D022 - Actividades económicas
    gActEco: List[ActividadEconomica] = field(default_factory=list)
    
    # D023 - Responsable de la generación del DE (opcional)
    gRespDE: Optional[ResponsableDE] = None
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Valida los datos del emisor."""
        # Validar RUC (formato: 12345678-9)
        if not self.dRucEm or len(self.dRucEm.replace('-', '')) < 8:
            return False, f"RUC inválido: {self.dRucEm}"
        
        # Validar DV (1 dígito)
        if self.dDVEmi < 0 or self.dDVEmi > 9:
            return False, f"Dígito verificador inválido: {self.dDVEmi}"
        
        # Validar tipo de contribuyente
        if self.iTipCont not in [1, 2]:
            return False, f"Tipo de contribuyente inválido: {self.iTipCont}"
        
        # Validar email
        if not self.dEmailE or '@' not in self.dEmailE:
            return False, f"Email inválido: {self.dEmailE}"
        
        # Validar actividades económicas (al menos una)
        if not self.gActEco:
            return False, "Debe especificar al menos una actividad económica"
        
        return True, None
