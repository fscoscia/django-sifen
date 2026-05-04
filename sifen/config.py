"""
Configuración para la librería SIFEN.
"""

from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any
import os

from sifen.constants import (
    URL_BASE_DEV,
    URL_BASE_PROD,
    URL_CONSULTA_QR_DEV,
    URL_CONSULTA_QR_PROD,
    PATH_RECIBE,
    PATH_RECIBE_LOTE,
    PATH_EVENTO,
    PATH_CONSULTA_LOTE,
    PATH_CONSULTA_RUC,
    PATH_CONSULTA,
    CSC_DEV_ID_1,
    CSC_DEV_VALUE_1,
    CSC_DEV_ID_2,
    CSC_DEV_VALUE_2,
    HTTP_CONNECT_TIMEOUT,
    HTTP_READ_TIMEOUT,
)
from sifen.exceptions import ConfigurationException


class TipoAmbiente(Enum):
    """Tipos de ambiente disponibles en SIFEN."""

    DEV = "DEV"
    PROD = "PROD"


class TipoCertificado(Enum):
    """Tipos de certificado soportados."""

    PFX = "PFX"
    # TODO: Implementar PEM y DER en futuras versiones


class SifenConfig:
    """
    Clase de configuración para las peticiones a SIFEN.

    Attributes:
        ambiente: Tipo de ambiente (DEV o PROD)
        certificado_archivo: Ruta al archivo del certificado
        certificado_contrasena: Contraseña del certificado
        csc: Código de Seguridad del Contribuyente
        csc_id: ID del CSC
        habilitar_nota_tecnica_13: Flag para habilitar cambios de NT13
        usar_certificado_cliente: Si se usa certificado para autenticación
        tipo_certificado: Tipo de certificado (solo PFX soportado)
        http_connect_timeout: Timeout de conexión HTTP
        http_read_timeout: Timeout de lectura HTTP
    """

    def __init__(
        self,
        ambiente: TipoAmbiente = TipoAmbiente.DEV,
        certificado_archivo: Optional[str] = None,
        certificado_base64: Optional[str] = None,
        certificado_bytes: Optional[bytes] = None,
        certificado_contrasena: Optional[str] = None,
        csc: Optional[str] = None,
        csc_id: Optional[str] = None,
        habilitar_nota_tecnica_13: bool = True,
        usar_certificado_cliente: bool = True,
        tipo_certificado: TipoCertificado = TipoCertificado.PFX,
        http_connect_timeout: int = HTTP_CONNECT_TIMEOUT,
        http_read_timeout: int = HTTP_READ_TIMEOUT,
    ):
        self.ambiente = ambiente
        self.certificado_contrasena = certificado_contrasena
        self.csc = csc
        self.csc_id = csc_id
        self.habilitar_nota_tecnica_13 = habilitar_nota_tecnica_13
        self.usar_certificado_cliente = usar_certificado_cliente
        self.tipo_certificado = tipo_certificado
        self.http_connect_timeout = http_connect_timeout
        self.http_read_timeout = http_read_timeout

        # Manejar diferentes formas de proveer el certificado
        self._certificado_bytes: Optional[bytes] = None
        self.certificado_archivo: Optional[str] = None

        if certificado_bytes:
            # Opción 1: Bytes directos (desde DB, memoria, etc.)
            self._certificado_bytes = certificado_bytes
        elif certificado_base64:
            # Opción 2: Base64 (desde variable de entorno, DB, etc.)
            import base64

            self._certificado_bytes = base64.b64decode(certificado_base64)
        elif certificado_archivo:
            # Opción 3: Ruta al archivo (tradicional)
            self.certificado_archivo = certificado_archivo

        # URLs se configuran automáticamente según el ambiente
        self._url_base = None
        self._url_consulta_qr = None

    def get_certificado_bytes(self) -> bytes:
        """
        Obtiene los bytes del certificado, ya sea desde archivo o desde memoria.

        Returns:
            Bytes del certificado.

        Raises:
            ConfigurationException: Si no se puede obtener el certificado.
        """
        if self._certificado_bytes:
            return self._certificado_bytes

        if self.certificado_archivo:
            cert_path = Path(self.certificado_archivo)
            if not cert_path.exists():
                raise ConfigurationException(
                    f"El archivo de certificado no existe: {self.certificado_archivo}"
                )
            return cert_path.read_bytes()

        raise ConfigurationException("No se ha configurado ningún certificado.")

    @property
    def url_base(self) -> str:
        """URL base según el ambiente configurado."""
        if self._url_base:
            return self._url_base
        return URL_BASE_DEV if self.ambiente == TipoAmbiente.DEV else URL_BASE_PROD

    @url_base.setter
    def url_base(self, value: str):
        """Permite sobreescribir la URL base."""
        self._url_base = value

    @property
    def url_consulta_qr(self) -> str:
        """URL de consulta QR según el ambiente configurado."""
        if self._url_consulta_qr:
            return self._url_consulta_qr
        return (
            URL_CONSULTA_QR_DEV
            if self.ambiente == TipoAmbiente.DEV
            else URL_CONSULTA_QR_PROD
        )

    @url_consulta_qr.setter
    def url_consulta_qr(self, value: str):
        """Permite sobreescribir la URL de consulta QR."""
        self._url_consulta_qr = value

    @property
    def path_recibe(self) -> str:
        """Path para recepción de DE (síncrono)."""
        return PATH_RECIBE

    @property
    def path_recibe_lote(self) -> str:
        """Path para recepción de lote de DEs (asíncrono)."""
        return PATH_RECIBE_LOTE

    @property
    def path_evento(self) -> str:
        """Path para recepción de eventos."""
        return PATH_EVENTO

    @property
    def path_consulta_lote(self) -> str:
        """Path para consulta de lote."""
        return PATH_CONSULTA_LOTE

    @property
    def path_consulta_ruc(self) -> str:
        """Path para consulta de RUC."""
        return PATH_CONSULTA_RUC

    @property
    def path_consulta(self) -> str:
        """Path para consulta de DE."""
        return PATH_CONSULTA

    def validar(self) -> None:
        """
        Valida la configuración.

        Raises:
            ConfigurationException: Si la configuración es inválida.
        """
        # Validar ambiente
        if not isinstance(self.ambiente, TipoAmbiente):
            raise ConfigurationException("Tipo de ambiente no establecido o inválido.")

        # Validar CSC
        if not self.csc_id:
            raise ConfigurationException("ID del CSC no establecido.")

        if not self.csc:
            raise ConfigurationException("CSC no establecido.")

        # Validar que no se usen CSCs de desarrollo en producción
        if self.ambiente == TipoAmbiente.PROD:
            if (self.csc_id == CSC_DEV_ID_1 and self.csc == CSC_DEV_VALUE_1) or (
                self.csc_id == CSC_DEV_ID_2 and self.csc == CSC_DEV_VALUE_2
            ):
                raise ConfigurationException(
                    "El CSC establecido solo es utilizable en el ambiente de desarrollo. "
                    "Solicitar a la SET el correspondiente a producción."
                )

        # Validar certificado si se usa
        if self.usar_certificado_cliente:
            # Verificar que se haya configurado alguna forma de certificado
            if not self._certificado_bytes and not self.certificado_archivo:
                raise ConfigurationException("Certificado digital no establecido.")

            if not self.tipo_certificado:
                raise ConfigurationException(
                    "Tipo de certificado digital no establecido."
                )

            if self.tipo_certificado == TipoCertificado.PFX:
                if not self.certificado_contrasena:
                    raise ConfigurationException(
                        "Contraseña del certificado digital no establecida."
                    )

            # Verificar que el archivo existe (solo si se usa archivo)
            if self.certificado_archivo:
                cert_path = Path(self.certificado_archivo)
                if not cert_path.exists():
                    raise ConfigurationException(
                        f"El archivo de certificado no existe: {self.certificado_archivo}"
                    )

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "SifenConfig":
        """
        Crea una instancia de SifenConfig desde un diccionario.

        Args:
            config_dict: Diccionario con la configuración.

        Returns:
            Instancia de SifenConfig.
        """
        # Convertir ambiente a enum si es string
        ambiente = config_dict.get("ambiente", "DEV")
        if isinstance(ambiente, str):
            ambiente = TipoAmbiente[ambiente.upper()]

        # Convertir tipo_certificado a enum si es string
        tipo_cert = config_dict.get("tipo_certificado", "PFX")
        if isinstance(tipo_cert, str):
            tipo_cert = TipoCertificado[tipo_cert.upper()]

        return cls(
            ambiente=ambiente,
            certificado_archivo=config_dict.get("certificado_archivo"),
            certificado_contrasena=config_dict.get("certificado_contrasena"),
            csc=config_dict.get("csc"),
            csc_id=config_dict.get("csc_id"),
            habilitar_nota_tecnica_13=config_dict.get(
                "habilitar_nota_tecnica_13", True
            ),
            usar_certificado_cliente=config_dict.get("usar_certificado_cliente", True),
            tipo_certificado=tipo_cert,
            http_connect_timeout=config_dict.get(
                "http_connect_timeout", HTTP_CONNECT_TIMEOUT
            ),
            http_read_timeout=config_dict.get("http_read_timeout", HTTP_READ_TIMEOUT),
        )

    @classmethod
    def from_env(cls) -> "SifenConfig":
        """
        Crea una instancia de SifenConfig desde variables de entorno.

        Variables de entorno esperadas:
            - SIFEN_AMBIENTE: DEV o PROD
            - SIFEN_CERTIFICADO_ARCHIVO: Ruta al certificado
            - SIFEN_CERTIFICADO_CONTRASENA: Contraseña del certificado
            - SIFEN_CSC: Código de Seguridad del Contribuyente
            - SIFEN_CSC_ID: ID del CSC
            - SIFEN_HABILITAR_NOTA_TECNICA_13: true/false

        Returns:
            Instancia de SifenConfig.
        """
        ambiente_str = os.getenv("SIFEN_AMBIENTE", "DEV")
        ambiente = TipoAmbiente[ambiente_str.upper()]

        habilitar_nt13 = (
            os.getenv("SIFEN_HABILITAR_NOTA_TECNICA_13", "true").lower() == "true"
        )

        return cls(
            ambiente=ambiente,
            certificado_archivo=os.getenv("SIFEN_CERTIFICADO_ARCHIVO"),
            certificado_contrasena=os.getenv("SIFEN_CERTIFICADO_CONTRASENA"),
            csc=os.getenv("SIFEN_CSC"),
            csc_id=os.getenv("SIFEN_CSC_ID"),
            habilitar_nota_tecnica_13=habilitar_nt13,
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la configuración a un diccionario.

        Returns:
            Diccionario con la configuración.
        """
        return {
            "ambiente": self.ambiente.value,
            "certificado_archivo": self.certificado_archivo,
            "csc_id": self.csc_id,
            "habilitar_nota_tecnica_13": self.habilitar_nota_tecnica_13,
            "usar_certificado_cliente": self.usar_certificado_cliente,
            "tipo_certificado": self.tipo_certificado.value,
            "url_base": self.url_base,
            "url_consulta_qr": self.url_consulta_qr,
        }
