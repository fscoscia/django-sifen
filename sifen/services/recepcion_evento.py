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


# Tipos de eventos del emisor
TIPO_EVENTO_CANCELACION = 1
TIPO_EVENTO_INUTILIZACION = 2

# Tipos de eventos del receptor
TIPO_EVENTO_NOTIFICACION_RECEPCION = 10
TIPO_EVENTO_CONFORMIDAD = 11
TIPO_EVENTO_DISCONFORMIDAD = 12
TIPO_EVENTO_DESCONOCIMIENTO = 13

# Eventos automáticos
TIPO_EVENTO_DEVOLUCION_AJUSTE_PRECIOS = 14
TIPO_EVENTO_ASOCIACION = 16

# Eventos automáticos por interoperabilidad
TIPO_EVENTO_ASOCIACION_RETENCION = 16
TIPO_EVENTO_CREDITOS_FISCALES = 17
TIPO_EVENTO_DEVOLUCION_CREDITOS_FISCALES_CUESTIONADO = 18
TIPO_EVENTO_DEVOLUCION_CREDITOS_FISCALES_DEVUELTO = 19
TIPO_EVENTO_ANTICIPO = 20
TIPO_EVENTO_REMISION = 21

# Eventos por actualización de datos
TIPO_EVENTO_TRANSPORTE = 22


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

    def recibir_evento(self, evento_xml: str) -> RespuestaRecepcionEvento:
        """
        Envía un evento a SIFEN.

        Args:
            evento_xml: XML del evento firmado digitalmente.

        Returns:
            Respuesta con el estado del evento.

        Raises:
            SifenException: Si hay error en la comunicación.
        """
        # Construir body del request como string
        request_body_str = self._build_request_body(evento_xml)

        # Construir SOAP envelope completo como string para preservar namespaces
        # Según ejemplo oficial: usar xmlns (namespace por defecto), xmlns:xsi y xsi:schemaLocation
        soap_envelope_str = f"""<?xml version="1.0" encoding="UTF-8"?>
<env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://ekuatia.set.gov.py/sifen/xsd" xsi:schemaLocation="http://ekuatia.set.gov.py/sifen/xsd https://ekuatia.set.gov.py/sifen/xsd/WS_SiRecepEvento_v150.xsd">
  <env:Header/>
  <env:Body>
    {request_body_str}
  </env:Body>
</env:Envelope>"""

        # Debug: mostrar SOAP request completo
        print("\n" + "=" * 70)
        print("DEBUG: SOAP Request completo")
        print("=" * 70)
        print(soap_envelope_str)
        print("=" * 70 + "\n")

        # Construir URL completa
        url = self._get_full_url(PATH_EVENTO)

        # Realizar petición con string
        response_xml = self._make_request(
            url, soap_envelope_str.encode("utf-8"), "rEnviEventoDe"
        )

        # Procesar respuesta
        return self._parse_response(response_xml)

    def _build_request_body(self, evento_xml: str) -> str:
        """
        Construye el cuerpo de la petición SOAP como string.

        Args:
            evento_xml: XML del evento.

        Returns:
            String XML del body.
        """
        from sifen.constants import NAMESPACE_SIFEN
        from datetime import datetime

        # Generar dId
        d_id = datetime.now().strftime("%Y%m%d%H%M%S%f")[:15]

        XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
        SCHEMA_LOCATION = "http://ekuatia.set.gov.py/sifen/xsd siRecepEvento_v150.xsd"

        # El evento_xml contiene <rGesEve>...</rGesEve> completo y firmado
        # NO debemos modificarlo para no invalidar la firma
        # Solo agregamos los namespaces en gGroupGesEve y agregamos xsi:schemaLocation a rGesEve
        from lxml import etree

        # Parsear el evento_xml
        evento_root = etree.fromstring(evento_xml.encode("utf-8"))

        # Recrear el elemento rGesEve con los namespaces correctos
        nsmap = {None: NAMESPACE_SIFEN, "xsi": XSI_NS}
        new_root = etree.Element(evento_root.tag, nsmap=nsmap)
        new_root.set(f"{{{XSI_NS}}}schemaLocation", SCHEMA_LOCATION)

        # Copiar todos los hijos del elemento original
        for child in evento_root:
            new_root.append(child)

        # Convertir de vuelta a string
        evento_xml_con_attrs = etree.tostring(
            new_root, encoding="unicode", pretty_print=True
        )

        # Construir el body según el XML de ejemplo oficial
        body_xml = f"""<rEnviEventoDe>
      <dId>{d_id}</dId>
        <dEvReg>
          <gGroupGesEve xmlns="{NAMESPACE_SIFEN}" xmlns:xsi="{XSI_NS}" xsi:schemaLocation="{SCHEMA_LOCATION}">
{evento_xml_con_attrs}
          </gGroupGesEve>
        </dEvReg>
    </rEnviEventoDe>"""

        return body_xml

    def _parse_response(self, response_xml) -> RespuestaRecepcionEvento:
        """
        Procesa la respuesta del servicio.

        Args:
            response_xml: XML de respuesta como etree.Element.

        Returns:
            Objeto RespuestaRecepcionEvento.
        """
        try:
            # response_xml ya es un etree.Element, no necesita parsing
            root = response_xml

            # Debug: imprimir XML de respuesta
            from lxml import etree

            print("\n" + "=" * 70)
            print("DEBUG: Respuesta XML de SIFEN")
            print("=" * 70)
            print(etree.tostring(root, pretty_print=True, encoding="unicode"))
            print("=" * 70 + "\n")

            # Extraer datos de la respuesta con namespace
            from sifen.constants import NAMESPACE_SIFEN

            NS = NAMESPACE_SIFEN

            # Buscar en gResProc (para errores) o rProtDe (para éxito)
            g_res_proc = root.find(f".//{{{NS}}}gResProc")
            r_prot_de = root.find(f".//{{{NS}}}rProtDe")

            if g_res_proc is not None:
                # Respuesta con código de error/éxito
                codigo = g_res_proc.findtext(f"{{{NS}}}dCodRes", "")
                mensaje = g_res_proc.findtext(f"{{{NS}}}dMsgRes", "")
                fecha_str = (
                    r_prot_de.findtext(f"{{{NS}}}dFecProc", "")
                    if r_prot_de is not None
                    else ""
                )
                id_evento = (
                    r_prot_de.findtext(f"{{{NS}}}Id", "")
                    if r_prot_de is not None
                    else ""
                )
                protocolo = (
                    r_prot_de.findtext(f"{{{NS}}}dProtAut", "")
                    if r_prot_de is not None
                    else ""
                )
                cdc = ""
            else:
                # Fallback sin namespace
                codigo = root.findtext(".//dCodRes", "")
                mensaje = root.findtext(".//dMsgRes", "")
                id_evento = root.findtext(".//Id", "")
                cdc = root.findtext(".//Id_CDC", "")
                protocolo = root.findtext(".//dProtAut", "")
                fecha_str = root.findtext(".//dFecProc", "")

            # Determinar si fue aprobado
            # Código 0600 = Evento aprobado
            aprobado = codigo == "0600"

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
