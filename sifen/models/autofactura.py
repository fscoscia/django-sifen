"""
Modelos para Autofactura Electrónica.

Grupo E4 - Campos específicos para AFE según Manual Técnico v150.
"""

from dataclasses import dataclass, field
from typing import Optional, Tuple

from .base import SifenObject


@dataclass
class Autofactura(SifenObject):
    """
    Grupo E4 - Campos de la Autofactura Electrónica (gCamAE).

    Obligatorio si iTiDE = 4 (Autofactura).
    No informar si iTiDE ≠ 4.

    La autofactura se emite cuando el comprador debe facturar por compras
    a proveedores que no emiten factura (ej: productores, no contribuyentes).

    Según Manual Técnico v150, sección E4 (E300-E399).
    """

    # E301 - Naturaleza del vendedor
    iNatVen: int = field(metadata={"required": True})

    # E302 - Descripción de la naturaleza del vendedor
    dDesNatVen: str = field(metadata={"required": True})

    # E304 - Tipo de documento de identidad del vendedor
    iTipIDVen: int = field(metadata={"required": True})

    # E305 - Descripción del tipo de documento de identidad del vendedor
    dDTipIDVen: str = field(metadata={"required": True})

    # E306 - Número de documento de identidad del vendedor
    dNumIDVen: str = field(metadata={"required": True})

    # E307 - Nombre y apellido del vendedor
    dNomVen: str = field(metadata={"required": True})

    # E308 - Dirección del vendedor
    dDirVen: str = field(metadata={"required": True})

    # E316 - Lugar de la transacción (dirección donde se provee el servicio o producto)
    dDirProv: str = field(metadata={"required": True})

    # E309 - Número de casa del vendedor
    dNumCasVen: Optional[int] = field(default=None, metadata={"required": False})

    # E310 - Código del departamento del vendedor
    cDepVen: Optional[int] = field(default=None, metadata={"required": False})

    # E311 - Descripción del departamento del vendedor
    dDesDepVen: Optional[str] = field(default=None, metadata={"required": False})

    # E312 - Código del distrito del vendedor
    cDisVen: Optional[int] = field(default=None, metadata={"required": False})

    # E313 - Descripción del distrito del vendedor
    dDesDisVen: Optional[str] = field(default=None, metadata={"required": False})

    # E314 - Código de la ciudad del vendedor
    cCiuVen: Optional[int] = field(default=None, metadata={"required": False})

    # E315 - Descripción de la ciudad del vendedor
    dDesCiuVen: Optional[str] = field(default=None, metadata={"required": False})

    # E317 - Código del departamento donde se realiza la transacción
    cDepProv: Optional[int] = field(default=None, metadata={"required": False})

    # E318 - Descripción del departamento donde se realiza la transacción
    dDesDepProv: Optional[str] = field(default=None, metadata={"required": False})

    # E319 - Código del distrito donde se realiza la transacción
    cDisProv: Optional[int] = field(default=None, metadata={"required": False})

    # E320 - Descripción del distrito donde se realiza la transacción
    dDesDisProv: Optional[str] = field(default=None, metadata={"required": False})

    # E321 - Código de la ciudad donde se realiza la transacción
    cCiuProv: Optional[int] = field(default=None, metadata={"required": False})

    # E322 - Descripción de la ciudad donde se realiza la transacción
    dDesCiuProv: Optional[str] = field(default=None, metadata={"required": False})

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida los campos de autofactura."""
        # Validar naturaleza del vendedor (1-2)
        if self.iNatVen not in [1, 2]:
            return False, f"Naturaleza del vendedor inválida: {self.iNatVen}"

        # Validar descripción según naturaleza
        descripciones_naturaleza = {
            1: "No contribuyente",
            2: "Extranjero",
        }

        if self.dDesNatVen != descripciones_naturaleza.get(self.iNatVen):
            return (
                False,
                f"Descripción de naturaleza no corresponde al código {self.iNatVen}. Debe ser: {descripciones_naturaleza.get(self.iNatVen)}",
            )

        # Validar tipo de documento de identidad (1-4)
        if self.iTipIDVen not in [1, 2, 3, 4]:
            return False, f"Tipo de documento de identidad inválido: {self.iTipIDVen}"

        # Validar descripción según tipo de documento
        descripciones_tipo_doc = {
            1: "Cédula paraguaya",
            2: "Pasaporte",
            3: "Cédula extranjera",
            4: "Carnet de residencia",
        }

        if self.dDTipIDVen != descripciones_tipo_doc.get(self.iTipIDVen):
            return (
                False,
                f"Descripción del tipo de documento no corresponde al código {self.iTipIDVen}. Debe ser: {descripciones_tipo_doc.get(self.iTipIDVen)}",
            )

        # Validar longitud del número de documento (1-20 caracteres)
        if not self.dNumIDVen or len(self.dNumIDVen) < 1 or len(self.dNumIDVen) > 20:
            return False, "Número de documento debe tener entre 1 y 20 caracteres"

        # Validar longitud del nombre (4-60 caracteres)
        if not self.dNomVen or len(self.dNomVen) < 4 or len(self.dNomVen) > 60:
            return False, "Nombre del vendedor debe tener entre 4 y 60 caracteres"

        # Validar longitud de la dirección del vendedor (1-255 caracteres)
        if not self.dDirVen or len(self.dDirVen) < 1 or len(self.dDirVen) > 255:
            return False, "Dirección del vendedor debe tener entre 1 y 255 caracteres"

        # Validar longitud de la dirección de la transacción (1-255 caracteres)
        if not self.dDirProv or len(self.dDirProv) < 1 or len(self.dDirProv) > 255:
            return (
                False,
                "Dirección de la transacción debe tener entre 1 y 255 caracteres",
            )

        # Validar consistencia de departamento
        if self.cDepVen and not self.dDesDepVen:
            return (
                False,
                "Si se especifica código de departamento del vendedor, debe incluir descripción",
            )

        if self.dDesDepVen and not self.cDepVen:
            return (
                False,
                "Si se especifica descripción de departamento del vendedor, debe incluir código",
            )

        # Validar consistencia de distrito
        if self.cDisVen and not self.dDesDisVen:
            return (
                False,
                "Si se especifica código de distrito del vendedor, debe incluir descripción",
            )

        if self.dDesDisVen and not self.cDisVen:
            return (
                False,
                "Si se especifica descripción de distrito del vendedor, debe incluir código",
            )

        # Validar consistencia de ciudad
        if self.cCiuVen and not self.dDesCiuVen:
            return (
                False,
                "Si se especifica código de ciudad del vendedor, debe incluir descripción",
            )

        if self.dDesCiuVen and not self.cCiuVen:
            return (
                False,
                "Si se especifica descripción de ciudad del vendedor, debe incluir código",
            )

        # Validar consistencia de departamento de transacción
        if self.cDepProv and not self.dDesDepProv:
            return (
                False,
                "Si se especifica código de departamento de transacción, debe incluir descripción",
            )

        if self.dDesDepProv and not self.cDepProv:
            return (
                False,
                "Si se especifica descripción de departamento de transacción, debe incluir código",
            )

        # Validar consistencia de distrito de transacción
        if self.cDisProv and not self.dDesDisProv:
            return (
                False,
                "Si se especifica código de distrito de transacción, debe incluir descripción",
            )

        if self.dDesDisProv and not self.cDisProv:
            return (
                False,
                "Si se especifica descripción de distrito de transacción, debe incluir código",
            )

        # Validar consistencia de ciudad de transacción
        if self.cCiuProv and not self.dDesCiuProv:
            return (
                False,
                "Si se especifica código de ciudad de transacción, debe incluir descripción",
            )

        if self.dDesCiuProv and not self.cCiuProv:
            return (
                False,
                "Si se especifica descripción de ciudad de transacción, debe incluir código",
            )

        return True, None


# Constantes para naturaleza del vendedor
NATURALEZA_NO_CONTRIBUYENTE = 1
NATURALEZA_EXTRANJERO = 2

# Descripciones de naturaleza del vendedor
DESCRIPCIONES_NATURALEZA = {
    NATURALEZA_NO_CONTRIBUYENTE: "No contribuyente",
    NATURALEZA_EXTRANJERO: "Extranjero",
}

# Constantes para tipo de documento de identidad
TIPO_DOC_CEDULA_PARAGUAYA = 1
TIPO_DOC_PASAPORTE = 2
TIPO_DOC_CEDULA_EXTRANJERA = 3
TIPO_DOC_CARNET_RESIDENCIA = 4

# Descripciones de tipo de documento
DESCRIPCIONES_TIPO_DOC = {
    TIPO_DOC_CEDULA_PARAGUAYA: "Cédula paraguaya",
    TIPO_DOC_PASAPORTE: "Pasaporte",
    TIPO_DOC_CEDULA_EXTRANJERA: "Cédula extranjera",
    TIPO_DOC_CARNET_RESIDENCIA: "Carnet de residencia",
}
