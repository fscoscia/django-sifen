"""
Servicio de Consulta de RUC.

Permite consultar datos de un contribuyente por su RUC.
"""

from typing import Optional
from dataclasses import dataclass
from lxml import etree

from sifen.services.base import SifenServiceBase
from sifen.config import SifenConfig
from sifen.constants import NAMESPACE_SIFEN, PATH_CONSULTA_RUC
from sifen.exceptions import SifenException


@dataclass
class DatosContribuyente:
    """Datos de un contribuyente."""

    ruc: str
    dv: str
    nombre: str
    tipo_contribuyente: Optional[str] = None
    estado: Optional[str] = None


@dataclass
class RespuestaConsultaRUC:
    """
    Respuesta del servicio de consulta de RUC.
    """

    # Código de respuesta
    codigo: str

    # Mensaje de respuesta
    mensaje: str

    # Datos del contribuyente (si se encontró)
    contribuyente: Optional[DatosContribuyente] = None

    # XML de respuesta completo
    xml_respuesta: Optional[str] = None

    @property
    def encontrado(self) -> bool:
        """Indica si se encontró el RUC."""
        return self.contribuyente is not None


class ConsultaRUCService(SifenServiceBase):
    """
    Servicio para consulta de RUC.

    Permite verificar la existencia y datos de un contribuyente.
    """

    def consultar_ruc(self, ruc: str, dv: str) -> RespuestaConsultaRUC:
        """
        Consulta un RUC en SIFEN.

        Args:
            ruc: RUC sin dígito verificador (ej: "80012345").
            dv: Dígito verificador (ej: "6").

        Returns:
            Respuesta de SIFEN.

        Raises:
            SifenException: Si hay error en el proceso.
        """
        # 1. Crear mensaje SOAP
        soap_envelope, soap_body = self._create_soap_envelope()

        # 2. Crear request de consulta
        r_envi_cons_ruc = etree.SubElement(
            soap_body,
            f"{{{NAMESPACE_SIFEN}}}rEnviConsRUC",
            nsmap={None: NAMESPACE_SIFEN},
        )

        # dId - Identificador de la consulta
        d_id = etree.SubElement(r_envi_cons_ruc, f"{{{NAMESPACE_SIFEN}}}dId")
        d_id.text = "1"

        # dRUCCons - RUC a consultar (sin dígito verificador según manual técnico)
        d_ruc_cons = etree.SubElement(r_envi_cons_ruc, f"{{{NAMESPACE_SIFEN}}}dRUCCons")
        d_ruc_cons.text = ruc

        # 3. Construir URL
        url = self._get_full_url(PATH_CONSULTA_RUC)

        # 4. Hacer request
        response_xml = self._make_request(url, soap_envelope)
        # print(etree.tostring(response_xml, pretty_print=True).decode())
        # 5. Procesar respuesta
        return self._process_response(response_xml)

    def _process_response(self, soap_response: etree.Element) -> RespuestaConsultaRUC:
        """
        Procesa la respuesta SOAP de consulta de RUC.

        Args:
            soap_response: Respuesta SOAP.

        Returns:
            Respuesta procesada.
        """
        # Extraer body
        body = self._extract_soap_body(soap_response)

        # Buscar elemento de respuesta usando namespace
        resp_elem = body.find(f".//{{{NAMESPACE_SIFEN}}}rResEnviConsRUC")

        if resp_elem is None:
            raise SifenException(
                "No se encontró elemento rResEnviConsRUC en la respuesta"
            )

        # Extraer código y mensaje
        codigo = resp_elem.findtext(f".//{{{NAMESPACE_SIFEN}}}dCodRes", "")
        mensaje = resp_elem.findtext(f".//{{{NAMESPACE_SIFEN}}}dMsgRes", "")

        # Datos del contribuyente (si se encontró)
        contribuyente = None

        # xContRUC - Datos del contribuyente
        x_cont_ruc = resp_elem.find(f".//{{{NAMESPACE_SIFEN}}}xContRUC")

        if x_cont_ruc is not None:
            ruc_text = x_cont_ruc.findtext(f".//{{{NAMESPACE_SIFEN}}}dRUCCons", "")

            # Separar RUC y DV
            if "-" in ruc_text:
                ruc, dv = ruc_text.split("-", 1)
            else:
                ruc = ruc_text[:-1] if len(ruc_text) > 1 else ruc_text
                dv = ruc_text[-1] if len(ruc_text) > 1 else ""

            contribuyente = DatosContribuyente(
                ruc=ruc,
                dv=dv,
                nombre=x_cont_ruc.findtext(f".//{{{NAMESPACE_SIFEN}}}dNombCons", ""),
                tipo_contribuyente=x_cont_ruc.findtext(
                    f".//{{{NAMESPACE_SIFEN}}}dTipCont"
                ),
                estado=x_cont_ruc.findtext(f".//{{{NAMESPACE_SIFEN}}}dEstCont"),
            )

        # XML de respuesta
        xml_respuesta = etree.tostring(
            soap_response, encoding="unicode", pretty_print=True
        )

        return RespuestaConsultaRUC(
            codigo=codigo,
            mensaje=mensaje,
            contribuyente=contribuyente,
            xml_respuesta=xml_respuesta,
        )


def consultar_ruc(config: SifenConfig, ruc: str, dv: str) -> RespuestaConsultaRUC:
    """
    Función helper para consultar un RUC.

    Args:
        config: Configuración de SIFEN.
        ruc: RUC sin dígito verificador.
        dv: Dígito verificador.

    Returns:
        Respuesta de SIFEN.
    """
    service = ConsultaRUCService(config)
    return service.consultar_ruc(ruc, dv)
