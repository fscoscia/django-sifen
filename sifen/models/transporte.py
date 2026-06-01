"""
Modelos para Transporte de Mercaderías.

Grupo E10 - Campos de transporte según Manual Técnico v150.
Obligatorio para Nota de Remisión (iTiDE=7).
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional, Tuple, List

from .base import SifenObject


@dataclass
class LocalSalida(SifenObject):
    """
    Grupo E10.1 - Campos que identifican el local de salida de las mercaderías (gCamSal).

    Obligatorio si iTiDE = 7 (Nota de Remisión).
    """

    # Campos obligatorios primero
    # E921 - Dirección del local de salida
    dDirLocSal: str = field(metadata={"required": True})

    # E922 - Número de casa de salida
    dNumCasSal: int = field(metadata={"required": True})

    # E925 - Código del departamento del local de salida
    cDepSal: int = field(metadata={"required": True})

    # E926 - Descripción del departamento del local de salida
    dDesDepSal: str = field(metadata={"required": True})

    # E929 - Código de la ciudad del local de salida
    cCiuSal: int = field(metadata={"required": True})

    # E930 - Descripción de ciudad del local de salida
    dDesCiuSal: str = field(metadata={"required": True})

    # Campos opcionales después
    # E923 - Complemento de dirección 1 salida (opcional)
    dComp1Sal: Optional[str] = field(default=None, metadata={"required": False})

    # E924 - Complemento de dirección 2 salida (opcional)
    dComp2Sal: Optional[str] = field(default=None, metadata={"required": False})

    # E927 - Código del distrito del local de salida (opcional)
    cDisSal: Optional[int] = field(default=None, metadata={"required": False})

    # E928 - Descripción del distrito del local de salida (opcional)
    dDesDisSal: Optional[str] = field(default=None, metadata={"required": False})

    # E931 - Teléfono de contacto del local de salida (opcional)
    dTelSal: Optional[str] = field(default=None, metadata={"required": False})


@dataclass
class LocalEntrega(SifenObject):
    """
    Grupo E10.2 - Campos que identifican el local de la entrega de las mercaderías (gCamEnt).

    Obligatorio si iTiDE = 7 (Nota de Remisión).
    Puede repetirse hasta 99 veces.
    """

    # Campos obligatorios primero
    # E941 - Dirección del local de la entrega
    dDirLocEnt: str = field(metadata={"required": True})

    # E942 - Número de casa de la entrega
    dNumCasEnt: int = field(metadata={"required": True})

    # E945 - Código del departamento del local de la entrega
    cDepEnt: int = field(metadata={"required": True})

    # E946 - Descripción del departamento del local de la entrega
    dDesDepEnt: str = field(metadata={"required": True})

    # E949 - Código de la ciudad del local de la entrega
    cCiuEnt: int = field(metadata={"required": True})

    # E950 - Descripción de ciudad del local de la entrega
    dDesCiuEnt: str = field(metadata={"required": True})

    # Campos opcionales después
    # E943 - Complemento de dirección 1 entrega (opcional)
    dComp1Ent: Optional[str] = field(default=None, metadata={"required": False})

    # E944 - Complemento de dirección 2 entrega (opcional)
    dComp2Ent: Optional[str] = field(default=None, metadata={"required": False})

    # E947 - Código del distrito del local de la entrega (opcional)
    cDisEnt: Optional[int] = field(default=None, metadata={"required": False})

    # E948 - Descripción del distrito del local de la entrega (opcional)
    dDesDisEnt: Optional[str] = field(default=None, metadata={"required": False})

    # E951 - Teléfono de contacto del local de la entrega (opcional)
    dTelEnt: Optional[str] = field(default=None, metadata={"required": False})


@dataclass
class VehiculoTraslado(SifenObject):
    """
    Grupo E10.3 - Campos que identifican el vehículo del traslado de mercaderías (gVehTras).

    Obligatorio si iTiDE = 7 (Nota de Remisión).
    Puede repetirse hasta 4 veces.
    """

    # E961 - Tipo de vehículo
    dTiVehTras: str = field(metadata={"required": True})

    # E962 - Marca
    dMarVeh: str = field(metadata={"required": True})

    # E967 - Tipo de identificación del vehículo (opcional)
    dTipIdenVeh: Optional[int] = field(default=None, metadata={"required": False})

    # E963 - Número de identificación del vehículo (opcional)
    dNroIDVeh: Optional[str] = field(default=None, metadata={"required": False})

    # E964 - Datos adicionales del vehículo (opcional)
    dAdicVeh: Optional[str] = field(default=None, metadata={"required": False})

    # E965 - Número de matrícula del vehículo (opcional)
    dNroMatVeh: Optional[str] = field(default=None, metadata={"required": False})

    # E966 - Número de vuelo (opcional)
    dNroVuelo: Optional[str] = field(default=None, metadata={"required": False})


@dataclass
class Transportista(SifenObject):
    """
    Grupo E10.4 - Campos que identifican al transportista (gCamTrans).

    Obligatorio si iTiDE = 7 (Nota de Remisión).
    Opcional cuando E903=1 y E967=1.
    """

    # Campos obligatorios primero
    # E981 - Naturaleza del transportista
    iNatTrans: int = field(metadata={"required": True})

    # E982 - Nombre o razón social del transportista
    dNomTrans: str = field(metadata={"required": True})

    # E990 - Número de documento de identidad del chofer
    dNumIDChof: str = field(metadata={"required": True})

    # E991 - Nombre y apellido del chofer
    dNomChof: str = field(metadata={"required": True})

    # Campos opcionales después
    # E983 - RUC del transportista (opcional si iNatTrans=2)
    dRucTrans: Optional[str] = field(default=None, metadata={"required": False})

    # E984 - Dígito verificador del RUC (opcional)
    dDVTrans: Optional[str] = field(default=None, metadata={"required": False})

    # E985 - Tipo de documento de identidad (opcional si iNatTrans=2)
    iTipIDTrans: Optional[int] = field(default=None, metadata={"required": False})

    # E986 - Descripción del tipo de documento (opcional)
    dDTipIDTrans: Optional[str] = field(default=None, metadata={"required": False})

    # E987 - Número de documento de identidad (opcional)
    dNumIDTrans: Optional[str] = field(default=None, metadata={"required": False})

    # E988 - Nacionalidad del transportista (opcional)
    cNacTrans: Optional[str] = field(default=None, metadata={"required": False})

    # E989 - Descripción de la nacionalidad (opcional)
    dDesNacTrans: Optional[str] = field(default=None, metadata={"required": False})

    # E992 - Domicilio fiscal del transportista (opcional)
    dDomFisc: Optional[str] = field(default=None, metadata={"required": False})

    # E993 - Dirección del chofer (opcional)
    dDirChof: Optional[str] = field(default=None, metadata={"required": False})

    # E994 - Nombre o razón social del agente (opcional - casos particulares)
    dNombAg: Optional[str] = field(default=None, metadata={"required": False})

    # E995 - RUC del agente (opcional - casos particulares)
    dRucAg: Optional[str] = field(default=None, metadata={"required": False})

    # E996 - Dígito verificador del RUC del agente (opcional)
    dDVAg: Optional[str] = field(default=None, metadata={"required": False})

    # E997 - Dirección del agente (opcional)
    dDirAge: Optional[str] = field(default=None, metadata={"required": False})


@dataclass
class Transporte(SifenObject):
    """
    Grupo E10 - Campos que describen el transporte de las mercaderías (gTransp).

    Obligatorio si iTiDE = 7 (Nota de Remisión).
    Opcional si iTiDE = 1 (Factura).

    Según Manual Técnico v150, sección E10 (E900-E999).
    """

    # E901 - Tipo de transporte
    iTipTrans: int = field(metadata={"required": True})

    # E902 - Descripción del tipo de transporte
    dDesTipTrans: str = field(metadata={"required": True})

    # E903 - Modalidad del transporte
    iModTrans: int = field(metadata={"required": True})

    # E904 - Descripción de la modalidad del transporte
    dDesModTrans: str = field(metadata={"required": True})

    # E905 - Responsable del costo del flete
    iRespFlete: int = field(metadata={"required": True})

    # E906 - Condición de la negociación (opcional)
    cCondNeg: Optional[str] = field(default=None, metadata={"required": False})

    # E907 - Número de manifiesto (opcional)
    dNuManif: Optional[str] = field(default=None, metadata={"required": False})

    # E908 - Número de despacho de importación (opcional)
    dNuDespImp: Optional[str] = field(default=None, metadata={"required": False})

    # E909 - Fecha estimada de inicio de traslado (opcional para iTiDE=7)
    dIniTras: Optional[date] = field(default=None, metadata={"required": False})

    # E910 - Fecha estimada de fin de traslado (opcional)
    dFinTras: Optional[date] = field(default=None, metadata={"required": False})

    # E911 - Código del país de destino (opcional)
    cPaisDest: Optional[str] = field(default=None, metadata={"required": False})

    # E912 - Descripción del país de destino (opcional)
    dDesPaisDest: Optional[str] = field(default=None, metadata={"required": False})

    # E10.1 - Local de salida (obligatorio para iTiDE=7)
    gCamSal: Optional[LocalSalida] = field(default=None, metadata={"required": False})

    # E10.2 - Locales de entrega (obligatorio para iTiDE=7, repetible hasta 99)
    gCamEnt: List[LocalEntrega] = field(
        default_factory=list, metadata={"required": False}
    )

    # E10.3 - Vehículos de traslado (obligatorio para iTiDE=7, repetible hasta 4)
    gVehTras: List[VehiculoTraslado] = field(
        default_factory=list, metadata={"required": False}
    )

    # E10.4 - Transportista (obligatorio para iTiDE=7, opcional cuando E903=1 y E967=1)
    gCamTrans: Optional[Transportista] = field(
        default=None, metadata={"required": False}
    )

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida los campos de transporte."""
        # Validar tipo de transporte (1-2)
        if self.iTipTrans not in [1, 2]:
            return False, f"Tipo de transporte inválido: {self.iTipTrans}"

        # Validar descripción según tipo
        if self.dDesTipTrans != DESCRIPCIONES_TIPO_TRANSPORTE.get(self.iTipTrans):
            return (
                False,
                f"Descripción de tipo de transporte no corresponde al código {self.iTipTrans}",
            )

        # Validar modalidad de transporte (1-4)
        if self.iModTrans not in [1, 2, 3, 4]:
            return False, f"Modalidad de transporte inválida: {self.iModTrans}"

        # Validar descripción según modalidad
        if self.dDesModTrans != DESCRIPCIONES_MODALIDAD.get(self.iModTrans):
            return (
                False,
                f"Descripción de modalidad no corresponde al código {self.iModTrans}",
            )

        # Validar responsable del flete (1-5)
        if self.iRespFlete not in [1, 2, 3, 4, 5]:
            return False, f"Responsable del flete inválido: {self.iRespFlete}"

        return True, None


# Constantes para tipo de transporte (E901)
TIPO_TRANSPORTE_PROPIO = 1
TIPO_TRANSPORTE_TERCERO = 2

# Descripciones de tipo de transporte
DESCRIPCIONES_TIPO_TRANSPORTE = {
    TIPO_TRANSPORTE_PROPIO: "Propio",
    TIPO_TRANSPORTE_TERCERO: "Tercero",
}

# Constantes para modalidad de transporte (E903)
MODALIDAD_TERRESTRE = 1
MODALIDAD_FLUVIAL = 2
MODALIDAD_AEREO = 3
MODALIDAD_MULTIMODAL = 4

# Descripciones de modalidad de transporte
DESCRIPCIONES_MODALIDAD = {
    MODALIDAD_TERRESTRE: "Terrestre",
    MODALIDAD_FLUVIAL: "Fluvial",
    MODALIDAD_AEREO: "Aéreo",
    MODALIDAD_MULTIMODAL: "Multimodal",
}

# Constantes para responsable del flete (E905)
RESPONSABLE_FLETE_EMISOR = 1
RESPONSABLE_FLETE_RECEPTOR = 2
RESPONSABLE_FLETE_TERCERO = 3
RESPONSABLE_FLETE_AGENTE_INTERMEDIARIO = 4
RESPONSABLE_FLETE_TRANSPORTISTA = 5

# Descripciones de responsable del flete
DESCRIPCIONES_RESPONSABLE_FLETE = {
    RESPONSABLE_FLETE_EMISOR: "Emisor de la Factura Electrónica",
    RESPONSABLE_FLETE_RECEPTOR: "Receptor de la Factura Electrónica",
    RESPONSABLE_FLETE_TERCERO: "Tercero",
    RESPONSABLE_FLETE_AGENTE_INTERMEDIARIO: "Agente intermediario del transporte (cuando intervenga)",
    RESPONSABLE_FLETE_TRANSPORTISTA: "Transportista",
}
