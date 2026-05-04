"""
Servicio de Consulta de Lote de Documentos Electrónicos.

Permite consultar el estado de un lote previamente enviado.
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from lxml import etree

from sifen.config import SifenConfig
from sifen.constants import PATH_CONSULTA_LOTE
from sifen.services.base import SifenServiceBase
from sifen.exceptions import SifenException


@dataclass
class DocumentoLote:
    """Información de un documento en el lote."""
    
    cdc: str
    estado: str
    codigo: str
    mensaje: str
    numero_protocolo: Optional[str] = None
    fecha_aprobacion: Optional[datetime] = None


@dataclass
class RespuestaConsultaLote:
    """
    Respuesta del servicio de consulta de lote.
    
    Attributes:
        codigo: Código de respuesta.
        mensaje: Mensaje de respuesta.
        numero_lote: Número de lote consultado.
        encontrado: Si el lote fue encontrado.
        estado: Estado del lote (procesado, pendiente, etc.).
        cantidad_documentos: Total de documentos en el lote.
        documentos: Lista de documentos con su estado.
    """
    
    codigo: str
    mensaje: str
    numero_lote: str
    encontrado: bool = False
    estado: Optional[str] = None
    cantidad_documentos: int = 0
    documentos: Optional[List[DocumentoLote]] = None
    
    def __post_init__(self):
        """Inicializa documentos si es None."""
        if self.documentos is None:
            self.documentos = []


class ConsultaLoteService(SifenServiceBase):
    """
    Servicio de consulta de lote de documentos electrónicos.
    
    Permite consultar el estado de procesamiento de un lote.
    """
    
    def consultar_lote(self, numero_lote: str) -> RespuestaConsultaLote:
        """
        Consulta el estado de un lote en SIFEN.
        
        Args:
            numero_lote: Número de lote a consultar.
        
        Returns:
            Respuesta con el estado del lote.
            
        Raises:
            SifenException: Si hay error en la comunicación.
            ValueError: Si el número de lote es inválido.
        """
        if not numero_lote or not numero_lote.strip():
            raise ValueError("El número de lote no puede estar vacío")
        
        # Construir petición SOAP
        soap_body = self._build_request_body(numero_lote)
        
        # Realizar petición
        response_xml = self._make_request(
            PATH_CONSULTA_LOTE,
            soap_body,
            'rConsLoteDe'
        )
        
        # Procesar respuesta
        return self._parse_response(response_xml, numero_lote)
    
    def _build_request_body(self, numero_lote: str) -> etree.Element:
        """
        Construye el cuerpo de la petición SOAP.
        
        Args:
            numero_lote: Número de lote.
        
        Returns:
            Elemento XML del body.
        """
        body = etree.Element('rConsLoteDe')
        
        # Agregar número de lote
        lote_elem = etree.SubElement(body, 'dNumLote')
        lote_elem.text = numero_lote
        
        return body
    
    def _parse_response(self, response_xml: str, numero_lote: str) -> RespuestaConsultaLote:
        """
        Procesa la respuesta del servicio.
        
        Args:
            response_xml: XML de respuesta.
            numero_lote: Número de lote consultado.
        
        Returns:
            Objeto RespuestaConsultaLote.
        """
        try:
            root = etree.fromstring(response_xml.encode('utf-8'))
            
            # Extraer datos generales
            codigo = self._get_text(root, './/dCodRes')
            mensaje = self._get_text(root, './/dMsgRes')
            estado = self._get_text(root, './/dEstRes')
            
            # Determinar si fue encontrado
            encontrado = codigo in ['0300', '0301', '0302']
            
            # Extraer documentos
            documentos = []
            for item in root.findall('.//gResProc'):
                cdc = self._get_text(item, './/Id')
                estado_doc = self._get_text(item, './/dEstRes')
                codigo_doc = self._get_text(item, './/dCodRes')
                mensaje_doc = self._get_text(item, './/dMsgRes')
                protocolo = self._get_text(item, './/dProtAut')
                fecha_str = self._get_text(item, './/dFecProc')
                
                # Parsear fecha
                fecha_aprobacion = None
                if fecha_str:
                    try:
                        fecha_aprobacion = datetime.fromisoformat(fecha_str)
                    except ValueError:
                        pass
                
                documentos.append(DocumentoLote(
                    cdc=cdc,
                    estado=estado_doc or 'Desconocido',
                    codigo=codigo_doc,
                    mensaje=mensaje_doc,
                    numero_protocolo=protocolo,
                    fecha_aprobacion=fecha_aprobacion,
                ))
            
            return RespuestaConsultaLote(
                codigo=codigo,
                mensaje=mensaje,
                numero_lote=numero_lote,
                encontrado=encontrado,
                estado=estado,
                cantidad_documentos=len(documentos),
                documentos=documentos,
            )
            
        except Exception as e:
            raise SifenException(f"Error al procesar respuesta de consulta de lote: {str(e)}")


def consultar_lote(config: SifenConfig, numero_lote: str) -> RespuestaConsultaLote:
    """
    Función helper para consultar un lote.
    
    Args:
        config: Configuración de SIFEN.
        numero_lote: Número de lote a consultar.
    
    Returns:
        Respuesta de la consulta.
    """
    service = ConsultaLoteService(config)
    return service.consultar_lote(numero_lote)
