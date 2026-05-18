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
        # Estructura: rEnviDe > dId + xDE > rDE (firmado)
        r_envi_de = etree.SubElement(
            soap_body,
            f"{{{NAMESPACE_SIFEN}}}rEnviDe",
            nsmap={None: NAMESPACE_SIFEN},
        )

        # dId: identificador de transacción (siempre 1 para envíos individuales)
        d_id = etree.SubElement(r_envi_de, f"{{{NAMESPACE_SIFEN}}}dId")
        d_id.text = "1"

        # xDE: wrapper requerido por el esquema SIFEN
        x_de = etree.SubElement(r_envi_de, f"{{{NAMESPACE_SIFEN}}}xDE")

        # Parsear el DE firmado y agregarlo dentro de xDE
        de_element = etree.fromstring(de_xml_firmado.encode('utf-8'))
        x_de.append(de_element)
        
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
        
        NS = NAMESPACE_SIFEN

        # Buscar elemento de respuesta
        resp_elem = body.find(f".//{{{NS}}}rRetEnviDe")

        if resp_elem is None:
            raise SifenException(
                "No se encontró elemento rRetEnviDe en la respuesta"
            )

        # Extraer datos de respuesta
        # gResProc - Resultado del procesamiento
        g_res_proc = resp_elem.find(f".//{{{NS}}}gResProc")

        if g_res_proc is None:
            raise SifenException(
                "No se encontró elemento gResProc en la respuesta"
            )

        # Código y mensaje
        codigo = g_res_proc.findtext(f".//{{{NS}}}dCodRes", '')
        mensaje = g_res_proc.findtext(f".//{{{NS}}}dMsgRes", '')

        # Datos adicionales (si fue aprobado)
        cdc = None
        numero_protocolo = None
        fecha_recepcion = None

        # rProtDe - Protocolo de procesamiento del DE (según XSD protProcesDE_v150)
        r_prot_de = resp_elem.find(f".//{{{NS}}}rProtDe")

        if r_prot_de is not None:
            cdc = r_prot_de.findtext(f"{{{NS}}}Id")
            numero_protocolo = r_prot_de.findtext(f"{{{NS}}}dProtAut")

            fecha_str = r_prot_de.findtext(f"{{{NS}}}dFecProc")
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
