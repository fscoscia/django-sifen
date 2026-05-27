"""
Servicio de Recepción de Lote de Documentos Electrónicos.

Permite enviar múltiples DEs en una sola petición SOAP.
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from lxml import etree
import zipfile
import base64
import io

from sifen.config import SifenConfig
from sifen.constants import PATH_RECIBE_LOTE, NAMESPACE_SIFEN
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
        """Retorna True si el lote fue encolado (0300) o procesado (0302)."""
        return self.codigo in ["0300", "0302"]


class RecepcionLoteService(SifenServiceBase):
    """
    Servicio de recepción de lote de documentos electrónicos.

    Permite enviar múltiples DEs en una sola petición.
    """

    def _create_soap_envelope_with_xsd(self):
        """
        Crea el envelope SOAP según el ejemplo que funciona.

        Formato esperado (ejemplo real):
        <env:Envelope xmlns:env="...">
          <env:Body>
            <rEnvioLote xmlns="...">
        """
        # Usa el envelope base, el namespace se declara en _build_request_body
        return self._create_soap_envelope()

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

        # 1. Crear SOAP envelope con namespace xsd
        soap_envelope, soap_body_container = self._create_soap_envelope_with_xsd()

        # 2. Construir el contenido del body (rEnvioLote)
        request_body = self._build_request_body(documentos_xml)

        # 3. Agregar el contenido al body del envelope
        soap_body_container.append(request_body)

        # 4. Construir URL completa
        url = self._get_full_url(PATH_RECIBE_LOTE)

        # 5. Realizar petición con el envelope completo
        response_xml = self._make_request(url, soap_envelope, "rEnvioLote")

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
        # Crear elemento raíz con namespace por defecto (sin prefijo)
        # Según ejemplo que funciona: <rEnvioLote xmlns="...">
        nsmap = {None: NAMESPACE_SIFEN}  # None = namespace por defecto
        body = etree.Element(f"{{{NAMESPACE_SIFEN}}}rEnvioLote", nsmap=nsmap)

        # Crear elemento dId sin prefijo (hereda namespace por defecto)
        # dId debe ser único para cada lote
        import time

        lote_id = str(int(time.time() * 1000) % 100000)  # ID único basado en timestamp
        did_elem = etree.SubElement(body, f"{{{NAMESPACE_SIFEN}}}dId")
        did_elem.text = lote_id

        from copy import deepcopy

        # rLoteDE sin namespace — cada rDE lleva su propio xmlns y xsi:schemaLocation
        lote_element = etree.Element("rLoteDE")

        for doc_xml in documentos_xml:
            doc_xml_limpio = doc_xml
            if doc_xml.strip().startswith("<?xml"):
                doc_xml_limpio = doc_xml.split("\n", 1)[1]

            rde_element = etree.fromstring(doc_xml_limpio.encode("utf-8"))
            lote_element.append(deepcopy(rde_element))

        lote_xml_bytes = etree.tostring(
            lote_element,
            encoding="UTF-8",
            xml_declaration=False,
            pretty_print=False,
        )

        # Crear archivo ZIP en memoria con compresión DEFLATED
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # Nombre del archivo = dId del lote
            file_name = f"{lote_id}.xml"
            zip_file.writestr(file_name, lote_xml_bytes)

        # Obtener bytes del ZIP
        compressed = zip_buffer.getvalue()

        # Codificar en Base64
        lote_base64 = base64.b64encode(compressed).decode("utf-8")

        # Agregar al body como xDE sin prefijo (hereda namespace por defecto)
        xde_elem = etree.SubElement(body, f"{{{NAMESPACE_SIFEN}}}xDE")
        xde_elem.text = lote_base64

        return body

    def _parse_response(self, response_xml) -> RespuestaRecepcionLote:
        """
        Procesa la respuesta del servicio.

        Args:
            response_xml: XML de respuesta como etree.Element.

        Returns:
            Objeto RespuestaRecepcionLote.
        """
        try:
            # response_xml ya es un etree.Element, no necesita parsing
            root = response_xml
            NS = NAMESPACE_SIFEN

            # Extraer datos generales del lote
            codigo = root.findtext(f".//{{{NS}}}dCodRes", "")
            mensaje = root.findtext(f".//{{{NS}}}dMsgRes", "")
            # El número de lote para consulta está en dProtConsLote
            numero_lote = root.findtext(f".//{{{NS}}}dProtConsLote", "")

            # Extraer detalles de cada documento
            detalles = []
            documentos_aprobados = 0
            documentos_rechazados = 0

            for item in root.findall(f".//{{{NS}}}gResProc"):
                cdc = item.findtext(f".//{{{NS}}}Id", "")
                codigo_doc = item.findtext(f".//{{{NS}}}dCodRes", "")
                mensaje_doc = item.findtext(f".//{{{NS}}}dMsgRes", "")
                protocolo = item.findtext(f".//{{{NS}}}dProtAut", "")
                fecha_str = item.findtext(f".//{{{NS}}}dFecProc", "")

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
