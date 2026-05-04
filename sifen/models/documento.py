"""
Modelo principal del Documento Electrónico.

Basado en DocumentoElectronico.java de la librería Java.
"""

from typing import Optional, List
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


@dataclass
class DocumentoElectronico(SifenObject):
    """
    Documento Electrónico (DE) completo para SIFEN.
    
    Representa la estructura completa de un DE según el Manual Técnico v150.
    Este es el objeto principal que se firma y envía a SIFEN.
    """
    
    # Versión del formato del DE
    dVerFor: int = field(default=150, metadata={'required': True})
    
    # A - Campos de identificación del DE
    gTimb: IdentificacionDE = field(metadata={'required': True})
    
    # B - Datos generales de la operación
    gDatGralOpe: DatosGeneralesDE = field(metadata={'required': True})
    
    # D - Datos del emisor
    gEmis: Emisor = field(metadata={'required': True})
    
    # E - Datos del receptor
    gDatRec: Receptor = field(metadata={'required': True})
    
    # E - Items de la operación
    gCamItem: List[Item] = field(default_factory=list, metadata={'required': True})
    
    # F - Totales de la operación
    gTotSub: Totales = field(metadata={'required': True})
    
    # E600 - Condición de la operación
    gPaConEIni: CondicionOperacion = field(metadata={'required': True})
    
    # CDC - Código de Control (se genera después de crear el DE)
    CDC: Optional[str] = None
    
    # ID del DE (para referencia en la firma)
    Id: str = field(default="", metadata={'required': True})
    
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
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        return f"DE{timestamp}"
    
    def generate_cdc(self) -> str:
        """
        Genera el Código de Control (CDC) del documento.
        
        El CDC es un código de 44 caracteres que identifica únicamente al DE.
        Formato: TTEEEPPPPPPPPNNNNNNNNCDDDDDDDDDDDDDDDDDDDDV
        
        Returns:
            CDC generado.
        """
        # TT - Tipo de documento (2 dígitos)
        tipo_doc = str(self.gTimb.iTiDE).zfill(2)
        
        # EEE - Establecimiento (3 dígitos)
        establecimiento = self.gTimb.dEst
        
        # PPP - Punto de expedición (3 dígitos)
        punto_exp = self.gTimb.dPunExp
        
        # NNNNNNN - Número de documento (7 dígitos)
        numero_doc = self.gTimb.dNumDoc
        
        # C - Tipo de contribuyente (1 dígito)
        tipo_contrib = str(self.gEmis.iTipCont)
        
        # DDDDDDDDDDDDDDDD - Fecha y hora de emisión (16 dígitos: YYYYMMDDHHmmss00)
        fecha_emision = self.gTimb.dFeIniT.strftime('%Y%m%d%H%M%S00')
        
        # RRRRRRRRRR - RUC del emisor sin DV (hasta 10 dígitos, completar con ceros a la izquierda)
        ruc = self.gEmis.dRucEm.replace('-', '').zfill(10)
        
        # Concatenar todo (sin DV todavía)
        cdc_sin_dv = (
            tipo_doc +
            establecimiento +
            punto_exp +
            numero_doc +
            tipo_contrib +
            fecha_emision +
            ruc
        )
        
        # Calcular dígito verificador
        dv = self._calculate_dv(cdc_sin_dv)
        
        # CDC completo
        cdc = cdc_sin_dv + str(dv)
        
        # Guardar CDC
        self.CDC = cdc
        
        return cdc
    
    def _calculate_dv(self, base: str) -> int:
        """
        Calcula el dígito verificador del CDC usando módulo 11.
        
        Args:
            base: String base para calcular el DV.
        
        Returns:
            Dígito verificador (0-9).
        """
        # Algoritmo módulo 11 base 2-9
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
    
    def validate(self) -> tuple[bool, Optional[str]]:
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
        
        # Validar condición de operación
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
            data['CDC'] = self.CDC
        
        return data
