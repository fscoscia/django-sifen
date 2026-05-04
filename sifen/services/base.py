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
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """
        Crea una sesión HTTP con configuración SSL.
        
        Returns:
            Sesión configurada.
        """
        session = requests.Session()
        
        # Configurar timeouts
        session.timeout = (
            self.config.timeout_conexion,
            self.config.timeout_lectura
        )
        
        # Configurar SSL si se usa certificado cliente
        if self.config.usar_certificado_cliente:
            # TODO: Configurar certificado cliente para mTLS si es necesario
            pass
        
        return session
    
    def _create_soap_envelope(self) -> etree.Element:
        """
        Crea el envelope SOAP base.
        
        Returns:
            Elemento Envelope.
        """
        nsmap = {
            'soap': NAMESPACE_SOAP,
            'sifen': NAMESPACE_SIFEN,
        }
        
        envelope = etree.Element(
            f"{{{NAMESPACE_SOAP}}}Envelope",
            nsmap=nsmap
        )
        
        # Header
        etree.SubElement(envelope, f"{{{NAMESPACE_SOAP}}}Header")
        
        # Body
        body = etree.SubElement(envelope, f"{{{NAMESPACE_SOAP}}}Body")
        
        return envelope, body
    
    def _make_request(
        self,
        url: str,
        soap_message: etree.Element,
        soap_action: Optional[str] = None
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
            soap_message,
            encoding='utf-8',
            xml_declaration=True,
            pretty_print=False
        )
        
        # Log del request
        logger.info(f"Enviando request a: {url}")
        logger.debug(f"SOAP Request:\n{xml_string.decode('utf-8')}")
        
        # Headers
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
        }
        
        if soap_action:
            headers['SOAPAction'] = soap_action
        
        try:
            # Realizar request
            response = self.session.post(
                url,
                data=xml_string,
                headers=headers,
                timeout=(
                    self.config.timeout_conexion,
                    self.config.timeout_lectura
                )
            )
            
            # Log de respuesta
            logger.info(f"Respuesta recibida. Status: {response.status_code}")
            logger.debug(f"SOAP Response:\n{response.text}")
            
            # Verificar status code
            response.raise_for_status()
            
            # Parsear respuesta
            response_xml = etree.fromstring(response.content)
            
            return response_xml
            
        except requests.exceptions.Timeout as e:
            raise CommunicationException(
                f"Timeout al conectar con SIFEN: {str(e)}"
            ) from e
        except requests.exceptions.ConnectionError as e:
            raise CommunicationException(
                f"Error de conexión con SIFEN: {str(e)}"
            ) from e
        except requests.exceptions.HTTPError as e:
            raise CommunicationException(
                f"Error HTTP {response.status_code}: {str(e)}"
            ) from e
        except etree.XMLSyntaxError as e:
            raise CommunicationException(
                f"Error al parsear respuesta XML: {str(e)}"
            ) from e
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
        body = soap_response.find(f'.//{{{NAMESPACE_SOAP}}}Body')
        
        if body is None:
            raise SifenException("No se encontró elemento Body en respuesta SOAP")
        
        # Verificar si hay Fault
        fault = body.find(f'.//{{{NAMESPACE_SOAP}}}Fault')
        if fault is not None:
            fault_string = fault.findtext(f'.//{{{NAMESPACE_SOAP}}}faultstring')
            fault_code = fault.findtext(f'.//{{{NAMESPACE_SOAP}}}faultcode')
            raise SifenException(
                f"SOAP Fault: [{fault_code}] {fault_string}"
            )
        
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
