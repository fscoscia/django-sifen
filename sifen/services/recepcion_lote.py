"""
Servicio de Recepción de Lote de Documentos Electrónicos.

Permite enviar múltiples DEs en una sola petición SOAP.
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from lxml import etree
import gzip
import base64
import io

from sifen.config import SifenConfig
from sifen.constants import PATH_RECIBE_LOTE
from sifen.services.base import SifenServiceBase
from sifen.exceptions import SifenException


@dataclass
class DetalleDocumentoLote:
    """Detalle de un documento en el lote."""

    cdc: str
    codigo: str
    mensaje: str
    aprobado: bool
    numero_protocolo: Optional[str] = None
    fecha_recepcion: Optional[datetime] = None


@dataclass
class RespuestaRecepcionLote:
    """
    Respuesta del servicio de recepción de lote.

    Attributes:
        codigo: Código de respuesta del lote.
        mensaje: Mensaje de respuesta.
        numero_lote: Número de lote asignado por SIFEN.
        cantidad_documentos: Total de documentos en el lote.
        documentos_aprobados: Cantidad de documentos aprobados.
        documentos_rechazados: Cantidad de documentos rechazados.
        detalles: Lista con el detalle de cada documento.
    """

    codigo: str
    mensaje: str
    numero_lote: Optional[str] = None
    cantidad_documentos: int = 0
    documentos_aprobados: int = 0
    documentos_rechazados: int = 0
    detalles: List[DetalleDocumentoLote] = None

    def __post_init__(self):
        """Inicializa detalles si es None."""
        if self.detalles is None:
            self.detalles = []

    @property
    def exitoso(self) -> bool:
        """Retorna True si el lote fue procesado exitosamente."""
        return self.codigo in ["0300", "0301", "0302"]


class RecepcionLoteService(SifenServiceBase):
    """
    Servicio de recepción de lote de documentos electrónicos.

    Permite enviar múltiples DEs en una sola petición.
    """

    def recibir_lote(self, documentos_xml: List[str]) -> RespuestaRecepcionLote:
        """
        Envía un lote de documentos electrónicos a SIFEN.

        Args:
            documentos_xml: Lista de XMLs de documentos firmados.

        Returns:
            Respuesta con el estado del lote.

        Raises:
            SifenException: Si hay error en la comunicación.
            ValueError: Si la lista está vacía o tiene más de 50 documentos.
        """
        # Validar cantidad de documentos
        if not documentos_xml:
            raise ValueError("La lista de documentos no puede estar vacía")

        if len(documentos_xml) > 50:
            raise ValueError("El lote no puede contener más de 50 documentos")

        # Construir petición SOAP
        soap_body = self._build_request_body(documentos_xml)

        # Realizar petición
        response_xml = self._make_request(PATH_RECIBE_LOTE, soap_body, "rEnviLoteDe")

        # Procesar respuesta
        return self._parse_response(response_xml)

    def _build_request_body(self, documentos_xml: List[str]) -> etree.Element:
        """
        Construye el cuerpo de la petición SOAP con compresión ZIP.

        Similar a la implementación Java, comprime los XMLs en un archivo ZIP
        y lo codifica en Base64 para reducir el tamaño de la petición.

        Args:
            documentos_xml: Lista de XMLs firmados.

        Returns:
            Elemento XML del body.
        """
        # Crear elemento raíz de la petición
        body = etree.Element("rEnviLoteDe")

        # Crear elemento dId (ID de la petición)
        did_elem = etree.SubElement(body, "dId")
        did_elem.text = "1"

        # Crear contenedor rLoteDE con todos los documentos
        lote_root = etree.Element("rLoteDE")

        for xml_string in documentos_xml:
            # Parsear el XML del documento
            doc_element = etree.fromstring(xml_string.encode("utf-8"))
            # Agregar al lote
            lote_root.append(doc_element)

        # Convertir el lote a string XML
        lote_xml_string = etree.tostring(
            lote_root, encoding="unicode", xml_declaration=False
        )

        # Comprimir con GZIP
        lote_xml_bytes = lote_xml_string.encode("utf-8")
        compressed = gzip.compress(lote_xml_bytes)

        # Codificar en Base64
        lote_base64 = base64.b64encode(compressed).decode("utf-8")

        # Agregar al body como xDE (XML comprimido)
        xde_elem = etree.SubElement(body, "xDE")
        xde_elem.text = lote_base64

        return body

    def _parse_response(self, response_xml: str) -> RespuestaRecepcionLote:
        """
        Procesa la respuesta del servicio.

        Args:
            response_xml: XML de respuesta.

        Returns:
            Objeto RespuestaRecepcionLote.
        """
        try:
            root = etree.fromstring(response_xml.encode("utf-8"))

            # Extraer datos generales del lote
            codigo = self._get_text(root, ".//dCodRes")
            mensaje = self._get_text(root, ".//dMsgRes")
            numero_lote = self._get_text(root, ".//dNumLote")

            # Extraer detalles de cada documento
            detalles = []
            documentos_aprobados = 0
            documentos_rechazados = 0

            for item in root.findall(".//gResProc"):
                cdc = self._get_text(item, ".//Id")
                codigo_doc = self._get_text(item, ".//dCodRes")
                mensaje_doc = self._get_text(item, ".//dMsgRes")
                protocolo = self._get_text(item, ".//dProtAut")
                fecha_str = self._get_text(item, ".//dFecProc")

                # Determinar si fue aprobado
                aprobado = codigo_doc == "0260"

                if aprobado:
                    documentos_aprobados += 1
                else:
                    documentos_rechazados += 1

                # Parsear fecha
                fecha_recepcion = None
                if fecha_str:
                    try:
                        fecha_recepcion = datetime.fromisoformat(fecha_str)
                    except ValueError:
                        pass

                detalles.append(
                    DetalleDocumentoLote(
                        cdc=cdc,
                        codigo=codigo_doc,
                        mensaje=mensaje_doc,
                        aprobado=aprobado,
                        numero_protocolo=protocolo,
                        fecha_recepcion=fecha_recepcion,
                    )
                )

            return RespuestaRecepcionLote(
                codigo=codigo,
                mensaje=mensaje,
                numero_lote=numero_lote,
                cantidad_documentos=len(detalles),
                documentos_aprobados=documentos_aprobados,
                documentos_rechazados=documentos_rechazados,
                detalles=detalles,
            )

        except Exception as e:
            raise SifenException(f"Error al procesar respuesta de lote: {str(e)}")


def recibir_lote(
    config: SifenConfig, documentos_xml: List[str]
) -> RespuestaRecepcionLote:
    """
    Función helper para enviar un lote de documentos.

    Args:
        config: Configuración de SIFEN.
        documentos_xml: Lista de XMLs firmados.

    Returns:
        Respuesta del lote.
    """
    service = RecepcionLoteService(config)
    return service.recibir_lote(documentos_xml)
