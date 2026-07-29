"""
Servicio de Consulta de Documentos Electrónicos.

Permite consultar el estado de un DE por su CDC.
"""

from typing import Optional
from dataclasses import dataclass
from lxml import etree
from datetime import datetime

from sifen.services.base import SifenServiceBase
from sifen.config import SifenConfig
from sifen.constants import NAMESPACE_SIFEN, PATH_CONSULTA
from sifen.exceptions import SifenException


@dataclass
class RespuestaConsultaDE:
    """
    Respuesta del servicio de consulta de DE.
    """
    # Código de respuesta
    codigo: str
    
    # Mensaje de respuesta
    mensaje: str
    
    # CDC consultado
    cdc: Optional[str] = None
    
    # Estado del DE
    estado: Optional[str] = None
    
    # Fecha de aprobación
    fecha_aprobacion: Optional[datetime] = None
    
    # XML del DE (si está disponible)
    xml_de: Optional[str] = None
    
    # XML de respuesta completo
    xml_respuesta: Optional[str] = None

    # Número de protocolo de autorización
    numero_protocolo: Optional[str] = None

    @property
    def encontrado(self) -> bool:
        """Indica si se encontró el DE."""
        return self.estado is not None
    
    @property
    def aprobado(self) -> bool:
        """Indica si el DE está aprobado."""
        return self.estado == 'Aprobado' if self.estado else False


class ConsultaDEService(SifenServiceBase):
    """
    Servicio para consulta de Documentos Electrónicos.
    
    Permite verificar el estado de un DE ya enviado.
    """
    
    def consultar_de(self, cdc: str) -> RespuestaConsultaDE:
        """
        Consulta un DE por su CDC.
        
        Args:
            cdc: Código de Control del documento (44 caracteres).
        
        Returns:
            Respuesta de SIFEN.
            
        Raises:
            SifenException: Si hay error en el proceso.
        """
        # Validar CDC
        if not cdc or len(cdc) != 44:
            raise SifenException(
                f"CDC inválido. Debe tener 44 caracteres. Recibido: {len(cdc) if cdc else 0}"
            )
        
        # 1. Crear mensaje SOAP
        soap_envelope, soap_body = self._create_soap_envelope()
        
        # 2. Crear request de consulta
        r_cons_de = etree.SubElement(
            soap_body,
            f"{{{NAMESPACE_SIFEN}}}rEnviConsDeRequest",
            nsmap={None: NAMESPACE_SIFEN},
        )

        # dId - Identificador de la consulta
        d_id = etree.SubElement(r_cons_de, f"{{{NAMESPACE_SIFEN}}}dId")
        d_id.text = "1"

        # dCDC - CDC a consultar
        d_cdc = etree.SubElement(r_cons_de, f"{{{NAMESPACE_SIFEN}}}dCDC")
        d_cdc.text = cdc
        
        # 3. Construir URL
        url = self._get_full_url(PATH_CONSULTA)
        
        # 4. Hacer request
        response_xml = self._make_request(url, soap_envelope)
        
        # 5. Procesar respuesta
        return self._process_response(response_xml, cdc)
    
    def _process_response(
        self,
        soap_response: etree.Element,
        cdc: str
    ) -> RespuestaConsultaDE:
        """
        Procesa la respuesta SOAP de consulta de DE.
        
        Args:
            soap_response: Respuesta SOAP.
            cdc: CDC consultado.
        
        Returns:
            Respuesta procesada.
        """
        # Extraer body
        body = self._extract_soap_body(soap_response)
        
        NS = NAMESPACE_SIFEN

        # Buscar elemento de respuesta
        resp_elem = body.find(f".//{{{NS}}}rEnviConsDeResponse")

        if resp_elem is None:
            raise SifenException(
                "No se encontró elemento rEnviConsDeResponse en la respuesta"
            )

        # Extraer código y mensaje (hijos directos de rEnviConsDeResponse)
        codigo = resp_elem.findtext(f"{{{NS}}}dCodRes", '')
        mensaje = resp_elem.findtext(f"{{{NS}}}dMsgRes", '')

        # Fecha de procesamiento (hijo directo de rEnviConsDeResponse)
        fecha_aprobacion = None
        fecha_str = resp_elem.findtext(f"{{{NS}}}dFecProc")
        if fecha_str:
            try:
                fecha_aprobacion = datetime.fromisoformat(fecha_str)
            except ValueError:
                pass

        # Datos del DE (si se encontró)
        estado = None
        xml_de = None
        numero_protocolo = None

        # xContenDE - Contenido del DE (contiene rDE y dProtAut)
        x_conten_de = resp_elem.find(f"{{{NS}}}xContenDE")

        if x_conten_de is not None:
            # XML del DE (si está incluido)
            de_elem = x_conten_de.find(f".//{{{NS}}}rDE")
            if de_elem is not None:
                xml_de = etree.tostring(
                    de_elem,
                    encoding='unicode',
                    pretty_print=True
                )
            # Número de protocolo de autorización
            numero_protocolo = x_conten_de.findtext(f"{{{NS}}}dProtAut")
            # Estado derivado del código de respuesta
            estado = 'Aprobado' if codigo in ('0260', '0261') else codigo
        
        # XML de respuesta
        xml_respuesta = etree.tostring(
            soap_response,
            encoding='unicode',
            pretty_print=True
        )
        
        return RespuestaConsultaDE(
            codigo=codigo,
            mensaje=mensaje,
            cdc=cdc,
            estado=estado,
            fecha_aprobacion=fecha_aprobacion,
            xml_de=xml_de,
            xml_respuesta=xml_respuesta,
            numero_protocolo=numero_protocolo,
        )


def consultar_de(config: SifenConfig, cdc: str) -> RespuestaConsultaDE:
    """
    Función helper para consultar un DE.
    
    Args:
        config: Configuración de SIFEN.
        cdc: Código de Control del documento.
    
    Returns:
        Respuesta de SIFEN.
    """
    service = ConsultaDEService(config)
    return service.consultar_de(cdc)
