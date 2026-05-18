"""
Cliente base para servicios web SIFEN.

Proporciona funcionalidad común para todos los servicios SOAP.
"""

from typing import Optional, Dict, Any
import requests
from lxml import etree
import logging

from sifen.config import SifenConfig
from sifen.constants import NAMESPACE_SOAP, NAMESPACE_SIFEN
from sifen.exceptions import SifenException, CommunicationException


logger = logging.getLogger(__name__)


class SifenServiceBase:
    """
    Clase base para servicios web SIFEN.

    Proporciona funcionalidad común para crear y enviar requests SOAP.
    """

    def __init__(self, config: SifenConfig):
        """
        Inicializa el servicio.

        Args:
            config: Configuración de SIFEN.
        """
        self.config = config
        self._cert_files = None  # Guardar referencia a archivos temporales
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """
        Crea una sesión HTTP con configuración SSL.

        Returns:
            Sesión configurada.
        """
        session = requests.Session()

        # Configurar timeouts
        session.timeout = (self.config.timeout_conexion, self.config.timeout_lectura)

        # Configurar SSL si se usa certificado cliente
        if self.config.usar_certificado_cliente:
            # Configurar certificado cliente para mTLS
            try:
                from cryptography.hazmat.primitives.serialization import pkcs12
                from cryptography.hazmat.primitives import serialization
                import tempfile

                # Obtener bytes del certificado PFX
                pfx_bytes = self.config.get_certificado_bytes()
                password = (
                    self.config.certificado_contrasena.encode("utf-8")
                    if self.config.certificado_contrasena
                    else None
                )

                # Cargar el PFX
                private_key, certificate, _ = pkcs12.load_key_and_certificates(
                    pfx_bytes, password
                )

                # Crear archivos temporales para cert y key
                cert_file = tempfile.NamedTemporaryFile(
                    mode="wb", delete=False, suffix=".pem"
                )
                key_file = tempfile.NamedTemporaryFile(
                    mode="wb", delete=False, suffix=".pem"
                )

                # Escribir certificado
                cert_file.write(certificate.public_bytes(serialization.Encoding.PEM))
                cert_file.close()

                # Escribir clave privada
                key_file.write(
                    private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.TraditionalOpenSSL,
                        encryption_algorithm=serialization.NoEncryption(),
                    )
                )
                key_file.close()

                # Configurar certificado cliente en la sesión
                session.cert = (cert_file.name, key_file.name)

                # Guardar referencias para evitar que se eliminen los archivos temporales
                self._cert_files = (cert_file, key_file)

                logger.info("Certificado cliente configurado para mTLS")

            except Exception as e:
                logger.error(f"Error al configurar certificado cliente: {e}")
                raise CommunicationException(
                    f"No se pudo configurar el certificado cliente: {str(e)}"
                )

        return session

    def _create_soap_envelope(self) -> etree.Element:
        """
        Crea el envelope SOAP base.

        Returns:
            Elemento Envelope.
        """
        nsmap = {
            "soap": NAMESPACE_SOAP,
        }

        envelope = etree.Element(f"{{{NAMESPACE_SOAP}}}Envelope", nsmap=nsmap)

        # Header
        etree.SubElement(envelope, f"{{{NAMESPACE_SOAP}}}Header")

        # Body
        body = etree.SubElement(envelope, f"{{{NAMESPACE_SOAP}}}Body")

        return envelope, body

    def _make_request(
        self, url: str, soap_message: etree.Element, soap_action: Optional[str] = None
    ) -> etree.Element:
        """
        Realiza una petición SOAP.

        Args:
            url: URL del servicio.
            soap_message: Mensaje SOAP a enviar.
            soap_action: SOAPAction header (opcional).

        Returns:
            Respuesta SOAP como elemento XML.

        Raises:
            CommunicationException: Si hay error en la comunicación.
        """
        # Convertir a string XML
        xml_string = etree.tostring(
            soap_message, encoding="utf-8", xml_declaration=True, pretty_print=False
        )

        # Log del request
        logger.info(f"Enviando request a: {url}")
        logger.debug(f"SOAP Request:\n{xml_string.decode('utf-8')}")

        # Headers
        headers = {
            "Content-Type": "application/soap+xml; charset=utf-8",
        }

        if soap_action:
            headers["SOAPAction"] = soap_action

        # Intentar hasta 3 veces en caso de errores de conexión
        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                # Crear una nueva sesión para cada request para evitar problemas de estado
                session = self._create_session()

                # Realizar request
                response = session.post(
                    url,
                    data=xml_string,
                    headers=headers,
                    timeout=(self.config.timeout_conexion, self.config.timeout_lectura),
                )

                # Si llegamos aquí, el request fue exitoso
                break

            except requests.exceptions.ConnectionError as e:
                last_error = e
                logger.warning(f"Intento {attempt + 1}/{max_retries} falló: {e}")
                if attempt < max_retries - 1:
                    import time

                    time.sleep(2)  # Esperar 2 segundos antes de reintentar
                    continue
                else:
                    # Si fue el último intento, lanzar el error
                    raise

        try:

            # Log de respuesta
            logger.info(f"Respuesta recibida. Status: {response.status_code}")
            logger.debug(f"SOAP Response:\n{response.text}")

            # SIFEN devuelve HTTP 400 para rechazos de negocio (ej: código 0160)
            # al igual que para aprobaciones (200). Intentamos parsear el SOAP
            # body siempre, igual que hace la librería Java con getErrorStream().
            if response.status_code not in (200, 202):
                logger.warning(
                    f"SIFEN devolvió HTTP {response.status_code}, "
                    f"intentando parsear SOAP body de todas formas"
                )

            # Parsear respuesta (independientemente del status code)
            try:
                response_xml = etree.fromstring(response.content)
                return response_xml
            except etree.XMLSyntaxError:
                pass

            # Si falla el parseo y el status no es exitoso, lanzar error HTTP
            if response.status_code not in (200, 202):
                raise CommunicationException(
                    f"Error HTTP {response.status_code}: respuesta no es XML válido\n"
                    f"Respuesta del servidor:\n{response.text[:2000]}"
                )

            # Status exitoso pero XML inválido — intentar recuperar
            try:
                parser = etree.XMLParser(recover=True, encoding="utf-8")
                response_xml = etree.fromstring(response.content, parser=parser)
                logger.warning("XML parseado con recuperación de errores")
                return response_xml
            except Exception as e:
                raise CommunicationException(
                    f"Error al parsear respuesta XML: {str(e)}"
                ) from e

        except requests.exceptions.Timeout as e:
            raise CommunicationException(
                f"Timeout al conectar con SIFEN: {str(e)}"
            ) from e
        except requests.exceptions.ConnectionError as e:
            raise CommunicationException(
                f"Error de conexión con SIFEN: {str(e)}"
            ) from e
        except CommunicationException:
            raise
        except Exception as e:
            raise CommunicationException(
                f"Error inesperado en comunicación: {str(e)}"
            ) from e

    def _extract_soap_body(self, soap_response: etree.Element) -> etree.Element:
        """
        Extrae el Body del SOAP response.

        Args:
            soap_response: Respuesta SOAP completa.

        Returns:
            Elemento Body.

        Raises:
            SifenException: Si no se encuentra el Body.
        """
        # Buscar Body
        body = soap_response.find(f".//{{{NAMESPACE_SOAP}}}Body")

        if body is None:
            raise SifenException("No se encontró elemento Body en respuesta SOAP")

        # Verificar si hay Fault
        fault = body.find(f".//{{{NAMESPACE_SOAP}}}Fault")
        if fault is not None:
            fault_string = fault.findtext(f".//{{{NAMESPACE_SOAP}}}faultstring")
            fault_code = fault.findtext(f".//{{{NAMESPACE_SOAP}}}faultcode")
            raise SifenException(f"SOAP Fault: [{fault_code}] {fault_string}")

        return body

    def _get_full_url(self, path: str) -> str:
        """
        Construye la URL completa del servicio.

        Args:
            path: Path del servicio.

        Returns:
            URL completa.
        """
        return self.config.url_base + path
