"""
Modelos para Documento Asociado.

Grupo H - Campos que identifican al documento asociado según Manual Técnico v150.
"""

from dataclasses import dataclass, field
from typing import Optional, Tuple
from datetime import date

from .base import SifenObject


@dataclass
class DocumentoAsociado(SifenObject):
    """
    Grupo H - Campos que identifican al DE asociado (gCamDEAsoc).
    
    Obligatorio si iTiDE = 4, 5, 6 (Autofactura, NCE, NDE).
    Opcional si iTiDE = 1.
    
    Según Manual Técnico v150, sección H (H001-H049).
    """
    
    # H002 - Tipo de documento asociado
    iTipDocAso: int = field(metadata={"required": True})
    
    # H003 - Descripción del tipo de documento asociado
    dDesTipDocAso: str = field(metadata={"required": True})
    
    # H004 - CDC del DTE referenciado (obligatorio si H002=1)
    dCdCDERef: Optional[str] = None
    
    # H005 - Número de timbrado del documento impreso de referencia (obligatorio si H002=2)
    dNTimDI: Optional[str] = None
    
    # H006 - Establecimiento (obligatorio si H002=2)
    dEstDocAso: Optional[str] = None
    
    # H007 - Punto de expedición (obligatorio si H002=2)
    dPExpDocAso: Optional[str] = None
    
    # H008 - Número del documento (obligatorio si H002=2)
    dNumDocAso: Optional[str] = None
    
    # H009 - Tipo de documento impreso (obligatorio si H002=2, no informar si H002=1 o 3)
    iTipoDocAso: Optional[int] = None
    
    # H010 - Descripción del tipo de documento impreso
    dDTipoDocAso: Optional[str] = None
    
    # H011 - Fecha de emisión del documento impreso de referencia
    dFecEmiDI: Optional[date] = None
    
    # H012 - Número de comprobante de retención
    dNumComRet: Optional[str] = None
    
    # H013 - Número de resolución de crédito fiscal
    dNumResCF: Optional[str] = None
    
    # H014 - Tipo de constancia (obligatorio cuando H002=3)
    iTipCons: Optional[int] = None
    
    # H015 - Descripción del tipo de constancia
    dDesTipCons: Optional[str] = None
    
    # H016 - Número de constancia
    dNumCons: Optional[int] = None
    
    # H017 - Número de control de la constancia
    dNumControl: Optional[str] = None
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida los campos de documento asociado."""
        # Validar tipo de documento asociado (1=Electrónico, 2=Impreso, 3=Constancia Electrónica)
        if self.iTipDocAso not in [1, 2, 3]:
            return False, f"Tipo de documento asociado inválido: {self.iTipDocAso}"
        
        # Validar descripción según tipo
        descripciones_validas = {
            1: "Electrónico",
            2: "Impreso",
            3: "Constancia Electrónica",
        }
        
        if self.dDesTipDocAso != descripciones_validas.get(self.iTipDocAso):
            return False, f"Descripción del tipo de documento asociado no corresponde al código {self.iTipDocAso}. Debe ser: {descripciones_validas.get(self.iTipDocAso)}"
        
        # Validaciones según tipo de documento
        if self.iTipDocAso == 1:  # Electrónico
            if not self.dCdCDERef:
                return False, "CDC del DTE referenciado es obligatorio para documentos electrónicos"
            if len(self.dCdCDERef) != 44:
                return False, f"CDC debe tener 44 caracteres, tiene {len(self.dCdCDERef)}"
        
        elif self.iTipDocAso == 2:  # Impreso
            if not self.dNTimDI:
                return False, "Número de timbrado es obligatorio para documentos impresos"
            if not self.dEstDocAso or len(self.dEstDocAso) != 3:
                return False, "Establecimiento debe tener 3 dígitos"
            if not self.dPExpDocAso or len(self.dPExpDocAso) != 3:
                return False, "Punto de expedición debe tener 3 dígitos"
            if not self.dNumDocAso or len(self.dNumDocAso) != 7:
                return False, "Número de documento debe tener 7 dígitos"
            if not self.iTipoDocAso:
                return False, "Tipo de documento impreso es obligatorio"
            
            # Validar tipo de documento impreso
            if self.iTipoDocAso not in [1, 2, 3, 4, 5]:
                return False, f"Tipo de documento impreso inválido: {self.iTipoDocAso}"
            
            descripciones_tipo_doc = {
                1: "Factura",
                2: "Nota de crédito",
                3: "Nota de débito",
                4: "Nota de remisión",
                5: "Comprobante de retención",
            }
            
            if self.dDTipoDocAso and self.dDTipoDocAso != descripciones_tipo_doc.get(self.iTipoDocAso):
                return False, f"Descripción del tipo de documento impreso no corresponde"
        
        elif self.iTipDocAso == 3:  # Constancia Electrónica
            if not self.iTipCons:
                return False, "Tipo de constancia es obligatorio"
            if self.iTipCons not in [1, 2]:
                return False, f"Tipo de constancia inválido: {self.iTipCons}"
            
            descripciones_constancia = {
                1: "Constancia de no ser contribuyente",
                2: "Constancia de microproductores",
            }
            
            if self.dDesTipCons and self.dDesTipCons != descripciones_constancia.get(self.iTipCons):
                return False, f"Descripción del tipo de constancia no corresponde"
        
        return True, None


# Constantes para tipo de documento asociado
TIPO_DOC_ASOCIADO_ELECTRONICO = 1
TIPO_DOC_ASOCIADO_IMPRESO = 2
TIPO_DOC_ASOCIADO_CONSTANCIA = 3

# Constantes para tipo de documento impreso
TIPO_DOC_IMPRESO_FACTURA = 1
TIPO_DOC_IMPRESO_NOTA_CREDITO = 2
TIPO_DOC_IMPRESO_NOTA_DEBITO = 3
TIPO_DOC_IMPRESO_NOTA_REMISION = 4
TIPO_DOC_IMPRESO_COMPROBANTE_RETENCION = 5

# Constantes para tipo de constancia
TIPO_CONSTANCIA_NO_CONTRIBUYENTE = 1
TIPO_CONSTANCIA_MICROPRODUCTORES = 2

# Descripciones
DESCRIPCIONES_TIPO_DOC_ASOCIADO = {
    TIPO_DOC_ASOCIADO_ELECTRONICO: "Electrónico",
    TIPO_DOC_ASOCIADO_IMPRESO: "Impreso",
    TIPO_DOC_ASOCIADO_CONSTANCIA: "Constancia Electrónica",
}

DESCRIPCIONES_TIPO_DOC_IMPRESO = {
    TIPO_DOC_IMPRESO_FACTURA: "Factura",
    TIPO_DOC_IMPRESO_NOTA_CREDITO: "Nota de crédito",
    TIPO_DOC_IMPRESO_NOTA_DEBITO: "Nota de débito",
    TIPO_DOC_IMPRESO_NOTA_REMISION: "Nota de remisión",
    TIPO_DOC_IMPRESO_COMPROBANTE_RETENCION: "Comprobante de retención",
}

DESCRIPCIONES_TIPO_CONSTANCIA = {
    TIPO_CONSTANCIA_NO_CONTRIBUYENTE: "Constancia de no ser contribuyente",
    TIPO_CONSTANCIA_MICROPRODUCTORES: "Constancia de microproductores",
}
