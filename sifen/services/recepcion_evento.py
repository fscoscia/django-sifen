"""
Servicio de Recepción de Eventos de Documentos Electrónicos.

Permite enviar eventos relacionados a DEs (cancelación, conformidad, etc.).
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from lxml import etree

from sifen.config import SifenConfig
from sifen.constants import PATH_EVENTO
from sifen.services.base import SifenServiceBase
from sifen.exceptions import SifenException


# Tipos de eventos
TIPO_EVENTO_CANCELACION = 1
TIPO_EVENTO_INUTILIZACION = 2
TIPO_EVENTO_CONFORMIDAD = 3
TIPO_EVENTO_DISCONFORMIDAD = 4
TIPO_EVENTO_DESCONOCIMIENTO = 5
TIPO_EVENTO_NOTIFICACION_NO_RECEPCION = 6


@dataclass
class RespuestaRecepcionEvento:
    """
    Respuesta del servicio de recepción de evento.
    
    Attributes:
        codigo: Código de respuesta.
        mensaje: Mensaje de respuesta.
        id_evento: ID del evento procesado.
        cdc: CDC del documento al que aplica el evento.
        aprobado: Si el evento fue aprobado.
        numero_protocolo: Número de protocolo asignado.
        fecha_recepcion: Fecha y hora de recepción.
    """
    
    codigo: str
    mensaje: str
    id_evento: Optional[str] = None
    cdc: Optional[str] = None
    aprobado: bool = False
    numero_protocolo: Optional[str] = None
    fecha_recepcion: Optional[datetime] = None


class RecepcionEventoService(SifenServiceBase):
    """
    Servicio de recepción de eventos de documentos electrónicos.
    
    Permite enviar eventos como cancelación, conformidad, etc.
    """
    
    def recibir_evento(
        self,
        evento_xml: str
    ) -> RespuestaRecepcionEvento:
        """
        Envía un evento a SIFEN.
        
        Args:
            evento_xml: XML del evento firmado digitalmente.
        
        Returns:
            Respuesta con el estado del evento.
            
        Raises:
            SifenException: Si hay error en la comunicación.
        """
        # Construir petición SOAP
        soap_body = self._build_request_body(evento_xml)
        
        # Realizar petición
        response_xml = self._make_request(
            PATH_EVENTO,
            soap_body,
            'rEnviEventoDe'
        )
        
        # Procesar respuesta
        return self._parse_response(response_xml)
    
    def _build_request_body(self, evento_xml: str) -> etree.Element:
        """
        Construye el cuerpo de la petición SOAP.
        
        Args:
            evento_xml: XML del evento.
        
        Returns:
            Elemento XML del body.
        """
        # Parsear el XML del evento
        evento_element = etree.fromstring(evento_xml.encode('utf-8'))
        
        # Crear elemento raíz de la petición
        body = etree.Element('rEnviEventoDe')
        
        # Agregar el evento
        body.append(evento_element)
        
        return body
    
    def _parse_response(self, response_xml: str) -> RespuestaRecepcionEvento:
        """
        Procesa la respuesta del servicio.
        
        Args:
            response_xml: XML de respuesta.
        
        Returns:
            Objeto RespuestaRecepcionEvento.
        """
        try:
            root = etree.fromstring(response_xml.encode('utf-8'))
            
            # Extraer datos de la respuesta
            codigo = self._get_text(root, './/dCodRes')
            mensaje = self._get_text(root, './/dMsgRes')
            id_evento = self._get_text(root, './/Id')
            cdc = self._get_text(root, './/Id_CDC')
            protocolo = self._get_text(root, './/dProtAut')
            fecha_str = self._get_text(root, './/dFecProc')
            
            # Determinar si fue aprobado
            # Código 0600 = Evento aprobado
            aprobado = codigo == '0600'
            
            # Parsear fecha
            fecha_recepcion = None
            if fecha_str:
                try:
                    fecha_recepcion = datetime.fromisoformat(fecha_str)
                except ValueError:
                    pass
            
            return RespuestaRecepcionEvento(
                codigo=codigo,
                mensaje=mensaje,
                id_evento=id_evento,
                cdc=cdc,
                aprobado=aprobado,
                numero_protocolo=protocolo,
                fecha_recepcion=fecha_recepcion,
            )
            
        except Exception as e:
            raise SifenException(f"Error al procesar respuesta de evento: {str(e)}")


def recibir_evento(config: SifenConfig, evento_xml: str) -> RespuestaRecepcionEvento:
    """
    Función helper para enviar un evento.
    
    Args:
        config: Configuración de SIFEN.
        evento_xml: XML del evento firmado.
    
    Returns:
        Respuesta del evento.
    """
    service = RecepcionEventoService(config)
    return service.recibir_evento(evento_xml)
