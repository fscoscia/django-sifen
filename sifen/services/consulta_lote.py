"""
Servicio de Consulta de Lote de Documentos Electrónicos.

Permite consultar el estado de un lote previamente enviado.
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from lxml import etree

from sifen.config import SifenConfig
from sifen.constants import PATH_CONSULTA_LOTE, NAMESPACE_SIFEN
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

        # 1. Crear SOAP envelope
        soap_envelope, soap_body_container = self._create_soap_envelope()

        # 2. Construir el contenido del body
        request_body = self._build_request_body(numero_lote)

        # 3. Agregar el contenido al body del envelope
        soap_body_container.append(request_body)

        # 4. Construir URL completa
        url = self._get_full_url(PATH_CONSULTA_LOTE)

        # 5. Realizar petición con el envelope completo
        response_xml = self._make_request(url, soap_envelope, "rEnviConsLoteDe")

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
        import time

        nsmap = {None: NAMESPACE_SIFEN}
        body = etree.Element(f"{{{NAMESPACE_SIFEN}}}rEnviConsLoteDe", nsmap=nsmap)

        did_elem = etree.SubElement(body, f"{{{NAMESPACE_SIFEN}}}dId")
        did_elem.text = str(int(time.time() * 1000) % 100000)

        prot_elem = etree.SubElement(body, f"{{{NAMESPACE_SIFEN}}}dProtConsLote")
        prot_elem.text = numero_lote

        return body

    def _parse_response(
        self, response_xml: str, numero_lote: str
    ) -> RespuestaConsultaLote:
        """
        Procesa la respuesta del servicio.

        Args:
            response_xml: XML de respuesta.
            numero_lote: Número de lote consultado.

        Returns:
            Objeto RespuestaConsultaLote.
        """
        try:
            root = response_xml
            NS = NAMESPACE_SIFEN

            codigo = root.findtext(f".//{{{NS}}}dCodResLot", "")
            mensaje = root.findtext(f".//{{{NS}}}dMsgResLot", "")

            documentos = []
            for item in root.findall(f".//{{{NS}}}gResProcLote"):
                cdc = item.findtext(f"{{{NS}}}id", "")
                estado_doc = item.findtext(f"{{{NS}}}dEstRes", "")
                protocolo = item.findtext(f"{{{NS}}}dProtAut", "")
                fecha_str = item.findtext(f"{{{NS}}}dFecProc", "")

                gres = item.find(f"{{{NS}}}gResProc")
                codigo_doc = gres.findtext(f"{{{NS}}}dCodRes", "") if gres is not None else ""
                mensaje_doc = gres.findtext(f"{{{NS}}}dMsgRes", "") if gres is not None else ""

                fecha_aprobacion = None
                if fecha_str:
                    try:
                        fecha_aprobacion = datetime.fromisoformat(fecha_str)
                    except ValueError:
                        pass

                documentos.append(
                    DocumentoLote(
                        cdc=cdc,
                        estado=estado_doc or "Desconocido",
                        codigo=codigo_doc,
                        mensaje=mensaje_doc,
                        numero_protocolo=protocolo,
                        fecha_aprobacion=fecha_aprobacion,
                    )
                )

            return RespuestaConsultaLote(
                codigo=codigo,
                mensaje=mensaje,
                numero_lote=numero_lote,
                encontrado=codigo == "0362" or bool(documentos),
                estado=None,
                cantidad_documentos=len(documentos),
                documentos=documentos,
            )

        except Exception as e:
            raise SifenException(
                f"Error al procesar respuesta de consulta de lote: {str(e)}"
            )


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
