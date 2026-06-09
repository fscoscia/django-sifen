"""
Servicio de Recepción de Lote de Eventos de Documentos Electrónicos.

Permite enviar lotes de hasta 15 eventos de cualquier tipo (emisor y/o receptor).
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from lxml import etree

from sifen.config import SifenConfig
from sifen.constants import PATH_EVENTO_LOTE
from sifen.services.base import SifenServiceBase
from sifen.exceptions import SifenException


@dataclass
class DetalleEventoLote:
    """
    Detalle de un evento en el lote.

    Attributes:
        id_evento: ID del evento.
        cdc: CDC del documento al que aplica el evento.
        tipo_evento: Tipo de evento.
        aprobado: Si el evento fue aprobado.
        codigo: Código de respuesta.
        mensaje: Mensaje de respuesta.
    """

    id_evento: str
    cdc: str
    tipo_evento: int
    aprobado: bool
    codigo: str
    mensaje: str


@dataclass
class RespuestaRecepcionLoteEventos:
    """
    Respuesta del servicio de recepción de lote de eventos.

    Attributes:
        codigo: Código de respuesta general.
        mensaje: Mensaje de respuesta general.
        numero_lote: Número de lote asignado por SIFEN.
        aprobado: Si el lote fue aprobado.
        fecha_recepcion: Fecha y hora de recepción.
        eventos: Lista de detalles de cada evento procesado.
    """

    codigo: str
    mensaje: str
    numero_lote: Optional[str] = None
    aprobado: bool = False
    fecha_recepcion: Optional[datetime] = None
    eventos: List[DetalleEventoLote] = None


class RecepcionLoteEventosService(SifenServiceBase):
    """
    Servicio de recepción de lotes de eventos de documentos electrónicos.

    Permite enviar hasta 15 eventos de cualquier tipo en un solo lote.
    """

    def recibir_lote_eventos(
        self, eventos_xml: List[str]
    ) -> RespuestaRecepcionLoteEventos:
        """
        Envía un lote de eventos a SIFEN.

        Args:
            eventos_xml: Lista de XMLs de eventos firmados digitalmente (máximo 15).

        Returns:
            Respuesta con el estado del lote.

        Raises:
            SifenException: Si hay error en la comunicación o validación.
        """
        # Validar cantidad de eventos
        if not eventos_xml or len(eventos_xml) == 0:
            raise SifenException("El lote debe contener al menos un evento")

        if len(eventos_xml) > 15:
            raise SifenException("El lote no puede contener más de 15 eventos")

        # Construir petición SOAP
        soap_envelope, soap_body = self._create_soap_envelope()

        # Construir body del request
        request_body = self._build_request_body(eventos_xml)
        soap_body.append(request_body)

        # Construir URL completa
        url = self._get_full_url(PATH_EVENTO_LOTE)

        # Realizar petición
        response_xml = self._make_request(url, soap_envelope, "rEnviLoteEve")

        # Procesar respuesta
        return self._parse_response(response_xml)

    def _build_request_body(self, eventos_xml: List[str]) -> etree.Element:
        """
        Construye el cuerpo de la petición SOAP.

        Args:
            eventos_xml: Lista de XMLs de eventos.

        Returns:
            Elemento XML del body.
        """
        # Crear elemento raíz de la petición
        body = etree.Element("rEnviLoteEve")

        # Agregar cada evento
        for evento_xml in eventos_xml:
            evento_element = etree.fromstring(evento_xml.encode("utf-8"))
            body.append(evento_element)

        return body

    def _parse_response(self, response_xml) -> RespuestaRecepcionLoteEventos:
        """
        Procesa la respuesta del servicio.

        Args:
            response_xml: XML de respuesta como etree.Element.

        Returns:
            Objeto RespuestaRecepcionLoteEventos.
        """
        try:
            # response_xml ya es un etree.Element, no necesita parsing
            root = response_xml

            # Extraer datos generales de la respuesta
            codigo = root.findtext(".//dCodRes", "")
            mensaje = root.findtext(".//dMsgRes", "")
            numero_lote = root.findtext(".//dNumLote", "")
            fecha_str = root.findtext(".//dFecProc", "")

            # Determinar si fue aprobado
            # Código 0601 = Lote de eventos aprobado
            aprobado = codigo == "0601"

            # Parsear fecha
            fecha_recepcion = None
            if fecha_str:
                try:
                    fecha_recepcion = datetime.fromisoformat(fecha_str)
                except ValueError:
                    pass

            # Extraer detalles de cada evento
            eventos = []
            for evento_elem in root.findall(".//gResProEve"):
                id_evento = evento_elem.findtext(".//Id", "")
                cdc = evento_elem.findtext(".//Id_CDC", "")
                tipo_evento_str = evento_elem.findtext(".//iTipEve", "")
                codigo_evento = evento_elem.findtext(".//dCodRes", "")
                mensaje_evento = evento_elem.findtext(".//dMsgRes", "")

                tipo_evento = int(tipo_evento_str) if tipo_evento_str else 0
                aprobado_evento = codigo_evento == "0600"

                eventos.append(
                    DetalleEventoLote(
                        id_evento=id_evento,
                        cdc=cdc,
                        tipo_evento=tipo_evento,
                        aprobado=aprobado_evento,
                        codigo=codigo_evento,
                        mensaje=mensaje_evento,
                    )
                )

            return RespuestaRecepcionLoteEventos(
                codigo=codigo,
                mensaje=mensaje,
                numero_lote=numero_lote,
                aprobado=aprobado,
                fecha_recepcion=fecha_recepcion,
                eventos=eventos,
            )

        except Exception as e:
            raise SifenException(
                f"Error al procesar respuesta de lote de eventos: {str(e)}"
            )


def recibir_lote_eventos(
    config: SifenConfig, eventos_xml: List[str]
) -> RespuestaRecepcionLoteEventos:
    """
    Función helper para enviar un lote de eventos.

    Args:
        config: Configuración de SIFEN.
        eventos_xml: Lista de XMLs de eventos firmados (máximo 15).

    Returns:
        Respuesta del lote de eventos.
    """
    service = RecepcionLoteEventosService(config)
    return service.recibir_lote_eventos(eventos_xml)
