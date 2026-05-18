"""
Clases base para los modelos de datos SIFEN.

Basado en SifenObjectBase.java de la librería Java.
"""

from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, date


@dataclass
class SifenObject:
    """
    Clase base para todos los objetos SIFEN.

    Proporciona funcionalidad común para serialización y validación.
    """

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el objeto a diccionario.

        Returns:
            Diccionario con los datos del objeto.
        """

        def convert_value(obj):
            """Convierte valores especiales a formatos serializables."""
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, date):
                return obj.isoformat()
            elif isinstance(obj, SifenObject):
                return obj.to_dict()
            elif isinstance(obj, list):
                return [convert_value(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: convert_value(v) for k, v in obj.items()}
            return obj

        data = asdict(self)
        return {k: convert_value(v) for k, v in data.items() if v is not None}

    def validate(self) -> Tuple[bool, Optional[str]]:
        """
        Valida el objeto.

        Returns:
            Tupla (es_valido, mensaje_error).
        """
        # Implementación base - las subclases pueden sobreescribir
        return True, None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SifenObject":
        """
        Crea una instancia desde un diccionario.

        Args:
            data: Diccionario con los datos.

        Returns:
            Instancia del objeto.
        """
        return cls(**data)


@dataclass
class IdentificacionDE(SifenObject):
    """
    Grupo A - Campos de identificación del Documento Electrónico (gTimb).

    Según Manual Técnico v150, sección 4.1.
    """

    # A002 - Tipo de Documento Electrónico
    iTiDE: int = field(metadata={"required": True})

    # A004 - Número del documento
    dNumTim: int = field(metadata={"required": True})

    # A005 - Establecimiento
    dEst: str = field(metadata={"required": True})

    # A006 - Punto de expedición
    dPunExp: str = field(metadata={"required": True})

    # A007 - Número del documento
    dNumDoc: str = field(metadata={"required": True})

    # A009 - Fecha de emisión
    dFeIniT: datetime = field(metadata={"required": True})

    # A003 - Descripción del Tipo de DE (opcional)
    dDesTiDE: Optional[str] = None

    # A008 - Serie del documento (opcional)
    dSerieNum: Optional[str] = None

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida los campos de identificación."""
        # Validar tipo de DE
        if self.iTiDE not in [1, 4, 5, 6, 7, 8, 9, 10]:
            return False, f"Tipo de DE inválido: {self.iTiDE}"

        # Validar establecimiento (3 dígitos)
        if not self.dEst or len(self.dEst) != 3 or not self.dEst.isdigit():
            return False, f"Establecimiento inválido: {self.dEst}"

        # Validar punto de expedición (3 dígitos)
        if not self.dPunExp or len(self.dPunExp) != 3 or not self.dPunExp.isdigit():
            return False, f"Punto de expedición inválido: {self.dPunExp}"

        # Validar número de documento (7 dígitos)
        if not self.dNumDoc or len(self.dNumDoc) != 7 or not self.dNumDoc.isdigit():
            return False, f"Número de documento inválido: {self.dNumDoc}"

        return True, None


@dataclass
class DatosGeneralesDE(SifenObject):
    """
    Grupo B - Datos generales del Documento Electrónico (gDatGralOpe).

    Según Manual Técnico v150, sección 4.2.
    """

    # B001 - Fecha de emisión del DE
    dFeEmiDE: date = field(metadata={"required": True})

    # B004 - Código de seguridad (CSC)
    dCodSeg: str = field(metadata={"required": True})

    # B002 - Tipo de emisión
    iTipEmi: int = field(default=1, metadata={"required": True})

    # B003 - Descripción del tipo de emisión (opcional)
    dDesTipEmi: Optional[str] = None

    # B005 - Información de interés del emisor (opcional)
    dInfoEmi: Optional[str] = None

    # B006 - Información de interés del fisco (opcional)
    dInfoFisc: Optional[str] = None

    # Campos de gOpeCom - Operación Comercial
    # C001 - Tipo de transacción
    iTipTra: int = field(default=1, metadata={"required": True})

    # C002 - Descripción del tipo de transacción (opcional)
    dDesTipTra: Optional[str] = None

    # C003 - Tipo de impuesto afectado
    iTImp: int = field(default=1, metadata={"required": True})

    # C004 - Descripción del tipo de impuesto (opcional)
    dDesTImp: Optional[str] = None

    # C005 - Código de moneda de la operación
    cMoneOpe: str = field(default="PYG", metadata={"required": True})

    # C006 - Descripción de la moneda (opcional)
    dDesMoneOpe: Optional[str] = None

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida los datos generales."""
        # Validar tipo de emisión
        if self.iTipEmi not in [1, 2, 3, 4, 5]:
            return False, f"Tipo de emisión inválido: {self.iTipEmi}"

        # Validar código de seguridad (9 dígitos)
        if not self.dCodSeg or len(self.dCodSeg) != 9 or not self.dCodSeg.isdigit():
            return False, f"Código de seguridad inválido: {self.dCodSeg}"

        return True, None


@dataclass
class Direccion(SifenObject):
    """
    Estructura común para direcciones.
    """

    # Dirección
    dDirec: str = field(metadata={"required": True})

    # Número de casa
    dNumCas: Optional[int] = None

    # Complemento de dirección 1
    dCompDir1: Optional[str] = None

    # Complemento de dirección 2
    dCompDir2: Optional[str] = None

    # Código de departamento
    cDepEmi: Optional[int] = None

    # Descripción del departamento
    dDesDepEmi: Optional[str] = None

    # Código de distrito
    cDisEmi: Optional[int] = None

    # Descripción del distrito
    dDesDisEmi: Optional[str] = None

    # Código de ciudad
    cCiuEmi: Optional[int] = None

    # Descripción de la ciudad
    dDesCiuEmi: Optional[str] = None


@dataclass
class Telefono(SifenObject):
    """
    Estructura común para teléfonos.
    """

    # Número de teléfono
    dNumTel: str = field(metadata={"required": True})

    # Código de país (opcional)
    cPaisTel: Optional[str] = None

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida el teléfono."""
        # Validar que tenga al menos 6 dígitos
        digits = "".join(filter(str.isdigit, self.dNumTel))
        if len(digits) < 6:
            return False, f"Número de teléfono inválido: {self.dNumTel}"

        return True, None


@dataclass
class ActividadEconomica(SifenObject):
    """
    Estructura para actividades económicas.
    """

    # Código de actividad económica
    cActEco: str = field(metadata={"required": True})

    # Descripción de la actividad económica
    dDesActEco: str = field(metadata={"required": True})
