"""
Servicio de Recepción de Documentos Electrónicos (DE).

Implementa el servicio web para enviar DEs a SIFEN de forma síncrona.
"""

from typing import Optional
from dataclasses import dataclass
from lxml import etree
from datetime import datetime

from sifen.services.base import SifenServiceBase
from sifen.config import SifenConfig
from sifen.constants import NAMESPACE_SIFEN, PATH_RECIBE
from sifen.exceptions import SifenException


@dataclass
class RespuestaRecepcionDE:
    """
    Respuesta del servicio de recepción de DE.
    """
    # Código de respuesta
    codigo: str
    
    # Mensaje de respuesta
    mensaje: str
    
    # CDC del documento
    cdc: Optional[str] = None
    
    # Número de protocolo
    numero_protocolo: Optional[str] = None
    
    # Fecha y hora de recepción
    fecha_recepcion: Optional[datetime] = None
    
    # XML de respuesta completo
    xml_respuesta: Optional[str] = None
    
    # XML de request enviado
    xml_request: Optional[str] = None
    
    @property
    def aprobado(self) -> bool:
        """Indica si el DE fue aprobado."""
        return self.codigo in ['0260', '0261']
    
    @property
    def rechazado(self) -> bool:
        """Indica si el DE fue rechazado."""
        return not self.aprobado


class RecepcionDEService(SifenServiceBase):
    """
    Servicio para recepción de Documentos Electrónicos.
    
    Permite enviar un DE firmado a SIFEN y obtener la respuesta.
    """
    
    def recibir_de(self, de_xml_firmado: str) -> RespuestaRecepcionDE:
        """
        Envía un DE firmado a SIFEN.
        
        Args:
            de_xml_firmado: XML del DE ya firmado digitalmente.
        
        Returns:
            Respuesta de SIFEN.
            
        Raises:
            SifenException: Si hay error en el proceso.
        """
        # 1. Crear mensaje SOAP
        soap_envelope, soap_body = self._create_soap_envelope()
        
        # 2. Agregar el DE al body
        # El DE firmado va dentro del elemento rEnviDe
        r_envi_de = etree.SubElement(
            soap_body,
            f"{{{NAMESPACE_SIFEN}}}rEnviDe"
        )
        
        # Parsear el DE firmado y agregarlo
        de_element = etree.fromstring(de_xml_firmado.encode('utf-8'))
        r_envi_de.append(de_element)
        
        # 3. Construir URL
        url = self._get_full_url(PATH_RECIBE)
        
        # 4. Hacer request
        response_xml = self._make_request(url, soap_envelope)
        
        # 5. Procesar respuesta
        return self._process_response(
            response_xml,
            etree.tostring(soap_envelope, encoding='unicode')
        )
    
    def _process_response(
        self,
        soap_response: etree.Element,
        request_xml: str
    ) -> RespuestaRecepcionDE:
        """
        Procesa la respuesta SOAP de recepción de DE.
        
        Args:
            soap_response: Respuesta SOAP.
            request_xml: XML del request enviado.
        
        Returns:
            Respuesta procesada.
        """
        # Extraer body
        body = self._extract_soap_body(soap_response)
        
        # Buscar elemento de respuesta
        # Namespace puede variar, buscar sin namespace específico
        resp_elem = body.find('.//*[local-name()="rRetEnviDe"]')
        
        if resp_elem is None:
            raise SifenException(
                "No se encontró elemento rRetEnviDe en la respuesta"
            )
        
        # Extraer datos de respuesta
        # gResProc - Resultado del procesamiento
        g_res_proc = resp_elem.find('.//*[local-name()="gResProc"]')
        
        if g_res_proc is None:
            raise SifenException(
                "No se encontró elemento gResProc en la respuesta"
            )
        
        # Código y mensaje
        codigo = g_res_proc.findtext('.//*[local-name()="dCodRes"]', '')
        mensaje = g_res_proc.findtext('.//*[local-name()="dMsgRes"]', '')
        
        # Datos adicionales (si fue aprobado)
        cdc = None
        numero_protocolo = None
        fecha_recepcion = None
        
        # gResProcDe - Resultado del procesamiento del DE
        g_res_proc_de = resp_elem.find('.//*[local-name()="gResProcDe"]')
        
        if g_res_proc_de is not None:
            cdc = g_res_proc_de.findtext('.//*[local-name()="dId"]')
            numero_protocolo = g_res_proc_de.findtext('.//*[local-name()="dProtAut"]')
            
            fecha_str = g_res_proc_de.findtext('.//*[local-name()="dFecProc"]')
            if fecha_str:
                try:
                    fecha_recepcion = datetime.fromisoformat(fecha_str)
                except ValueError:
                    pass
        
        # XML de respuesta
        xml_respuesta = etree.tostring(
            soap_response,
            encoding='unicode',
            pretty_print=True
        )
        
        return RespuestaRecepcionDE(
            codigo=codigo,
            mensaje=mensaje,
            cdc=cdc,
            numero_protocolo=numero_protocolo,
            fecha_recepcion=fecha_recepcion,
            xml_respuesta=xml_respuesta,
            xml_request=request_xml,
        )


def recibir_de(config: SifenConfig, de_xml_firmado: str) -> RespuestaRecepcionDE:
    """
    Función helper para recibir un DE.
    
    Args:
        config: Configuración de SIFEN.
        de_xml_firmado: XML del DE firmado.
    
    Returns:
        Respuesta de SIFEN.
    """
    service = RecepcionDEService(config)
    return service.recibir_de(de_xml_firmado)
