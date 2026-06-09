"""
Generador de XML para Eventos de Documentos Electrónicos.
"""

from datetime import datetime
from lxml import etree

from sifen.constants import NAMESPACE_SIFEN
from sifen.models.eventos import (
    GestionEvento,
    EventoCancelacion,
    EventoConformidad,
    EventoDisconformidad,
    EventoDesconocimiento,
    EventoInutilizacion,
    EventoNotificacionRecepcion,
    EventoConformidadParcial,
    EventoNotificacionNoRecepcion,
    EventoAsociacionRetencion,
    EventoAnulacionRetencion,
    EventoCreditosFiscales,
    EventoDevolucionCreditosFiscales,
    EventoAnticipo,
    EventoRemision,
    EventoTransporte,
)


class XMLEventoGenerator:
    """Generador de XML para eventos."""

    def __init__(self):
        """Inicializa el generador."""
        self.namespace = NAMESPACE_SIFEN

    def generate(self, evento: GestionEvento) -> str:
        """
        Genera el XML de un evento según schema SIFEN v150.

        Args:
            evento: Objeto GestionEvento.

        Returns:
            XML como string.
        """
        # Crear elemento raíz rGesEve con namespace SIFEN
        # NO declarar xmlns:ds porque la firma no usa prefijo según ejemplo oficial
        root = etree.Element("rGesEve", nsmap={None: self.namespace})

        # Crear elemento rEve con Id como atributo
        r_eve = etree.SubElement(root, "rEve", Id=evento.Id)

        # Agregar fecha de firma
        fecha_elem = etree.SubElement(r_eve, "dFecFirma")
        fecha_elem.text = evento.dFecFirma.strftime("%Y-%m-%dT%H:%M:%S")

        # Agregar versión del formato (150)
        ver_for = etree.SubElement(r_eve, "dVerFor")
        ver_for.text = "150"

        # Crear gGroupTiEvt
        g_group_ti_evt = etree.SubElement(r_eve, "gGroupTiEvt")

        # Agregar datos específicos del evento según tipo
        if evento.gGroupGesEve:
            self._add_evento_especifico(
                g_group_ti_evt, evento.gGroupGesEve, evento.iTipEve, evento.Id_CDC
            )

        # Convertir a string con formato legible
        xml_string = etree.tostring(
            root, encoding="unicode", pretty_print=True, xml_declaration=False
        )

        return xml_string

    def _add_evento_especifico(
        self, parent: etree.Element, evento_obj: object, tipo_evento: int, cdc: str
    ):
        """
        Agrega los datos específicos de cada tipo de evento.

        Args:
            parent: Elemento padre.
            evento_obj: Objeto del evento específico.
            tipo_evento: Tipo de evento.
        """
        if tipo_evento == 1:  # Cancelación
            self._add_cancelacion(parent, evento_obj, cdc)
        elif tipo_evento == 2:  # Inutilización
            self._add_inutilizacion(parent, evento_obj)
        elif tipo_evento == 10:  # Notificación de Recepción
            self._add_notificacion_recepcion(parent, evento_obj)
        elif tipo_evento == 11:  # Conformidad (Total o Parcial)
            self._add_conformidad_parcial(parent, evento_obj)
        elif tipo_evento == 12:  # Disconformidad
            self._add_disconformidad(parent, evento_obj)
        elif tipo_evento == 13:  # Desconocimiento
            self._add_desconocimiento(parent, evento_obj)
        elif tipo_evento == 16:  # Asociación de Retención
            self._add_asociacion_retencion(parent, evento_obj)

    def _add_cancelacion(
        self, parent: etree.Element, evento: EventoCancelacion, cdc: str
    ):
        """Agrega datos de cancelación."""
        grupo_canc = etree.SubElement(parent, "rGeVeCan")

        # Id es el CDC del documento a cancelar
        id_elem = etree.SubElement(grupo_canc, "Id")
        id_elem.text = cdc

        # Motivo de cancelación
        motivo = etree.SubElement(grupo_canc, "mOtEve")
        motivo.text = evento.mOtEve

    def _add_inutilizacion(self, parent: etree.Element, evento: EventoInutilizacion):
        """Agrega datos de inutilización."""
        grupo = etree.SubElement(parent, "gGroupGesEve")
        grupo_inu = etree.SubElement(grupo, "rGeVeInu")

        motivo = etree.SubElement(grupo_inu, "mOtEve")
        motivo.text = evento.mOtEve

        timbrado = etree.SubElement(grupo_inu, "dNumTim")
        timbrado.text = str(evento.dNumTim)

        est = etree.SubElement(grupo_inu, "dEst")
        est.text = evento.dEst

        punto = etree.SubElement(grupo_inu, "dPunExp")
        punto.text = evento.dPunExp

        num_in = etree.SubElement(grupo_inu, "dNumIn")
        num_in.text = evento.dNumIn

        num_fin = etree.SubElement(grupo_inu, "dNumFin")
        num_fin.text = evento.dNumFin

        tipo = etree.SubElement(grupo_inu, "iTiDE")
        tipo.text = str(evento.iTiDE)

    def _add_conformidad(self, parent: etree.Element, evento: EventoConformidad):
        """Agrega datos de conformidad."""
        grupo = etree.SubElement(parent, "gGroupGesEve")
        grupo_conf = etree.SubElement(grupo, "rGeVeConf")

        if evento.mOtEve:
            motivo = etree.SubElement(grupo_conf, "mOtEve")
            motivo.text = evento.mOtEve

    def _add_disconformidad(self, parent: etree.Element, evento: EventoDisconformidad):
        """Agrega datos de disconformidad."""
        grupo = etree.SubElement(parent, "gGroupGesEve")
        grupo_disconf = etree.SubElement(grupo, "rGeVeDisconf")

        motivo = etree.SubElement(grupo_disconf, "mOtEve")
        motivo.text = evento.mOtEve

    def _add_desconocimiento(
        self, parent: etree.Element, evento: EventoDesconocimiento
    ):
        """Agrega datos de desconocimiento."""
        grupo = etree.SubElement(parent, "gGroupGesEve")
        grupo_desc = etree.SubElement(grupo, "rGeVeDescon")

        motivo = etree.SubElement(grupo_desc, "mOtEve")
        motivo.text = evento.mOtEve

    def _add_notificacion_recepcion(
        self, parent: etree.Element, evento: EventoNotificacionRecepcion
    ):
        """Agrega datos de notificación de recepción."""
        grupo = etree.SubElement(parent, "rGeVeNotRec")

        id_elem = etree.SubElement(grupo, "Id")
        id_elem.text = evento.Id

        fec_emi = etree.SubElement(grupo, "dFecEmi")
        fec_emi.text = evento.dFecEmi.strftime("%Y-%m-%d")

        fec_recep = etree.SubElement(grupo, "dFecRecep")
        fec_recep.text = evento.dFecRecep.strftime("%Y-%m-%d")

        tip_rec = etree.SubElement(grupo, "iTipRec")
        tip_rec.text = str(evento.iTipRec)

        nom_rec = etree.SubElement(grupo, "dNomRec")
        nom_rec.text = evento.dNomRec

        if evento.iTipRec == 1 and evento.dRucRec:
            ruc_rec = etree.SubElement(grupo, "dRucRec")
            ruc_rec.text = evento.dRucRec

            dv_rec = etree.SubElement(grupo, "dDVRec")
            dv_rec.text = str(evento.dDVRec)

        if evento.iTipRec == 2:
            if evento.dTipIDRec:
                tip_id = etree.SubElement(grupo, "dTipIDRec")
                tip_id.text = str(evento.dTipIDRec)

            if evento.dNumID:
                num_id = etree.SubElement(grupo, "dNumID")
                num_id.text = evento.dNumID

        total = etree.SubElement(grupo, "iTotalGs")
        total.text = str(evento.iTotalGs)

    def _add_conformidad_parcial(
        self, parent: etree.Element, evento: EventoConformidadParcial
    ):
        """Agrega datos de conformidad parcial."""
        grupo = etree.SubElement(parent, "rGeVeConf")

        id_elem = etree.SubElement(grupo, "Id")
        id_elem.text = evento.Id

        tip_conf = etree.SubElement(grupo, "iTipConf")
        tip_conf.text = str(evento.iTipConf)

        if evento.iTipConf == 2 and evento.dFecRecep:
            fec_recep = etree.SubElement(grupo, "dFecRecep")
            fec_recep.text = evento.dFecRecep.strftime("%Y-%m-%d")

    def _add_asociacion_retencion(
        self, parent: etree.Element, evento: EventoAsociacionRetencion
    ):
        """Agrega datos de asociación de retención."""
        grupo = etree.SubElement(parent, "rGeVeRetAce")

        id_elem = etree.SubElement(grupo, "Id")
        id_elem.text = evento.Id

        num_tim = etree.SubElement(grupo, "dNumTimRet")
        num_tim.text = str(evento.dNumTimRet)

        est = etree.SubElement(grupo, "dEstRet")
        est.text = evento.dEstRet

        pun_exp = etree.SubElement(grupo, "dPunExpRet")
        pun_exp.text = evento.dPunExpRet

        num_doc = etree.SubElement(grupo, "dNumDocRet")
        num_doc.text = evento.dNumDocRet

        cod_con = etree.SubElement(grupo, "dCodConRet")
        cod_con.text = evento.dCodConRet

        fec_emi = etree.SubElement(grupo, "dFeEmiRet")
        fec_emi.text = evento.dFeEmiRet.strftime("%Y-%m-%d")

    def _add_notificacion_no_recepcion(
        self, parent: etree.Element, evento: EventoNotificacionNoRecepcion
    ):
        """Agrega datos de notificación de no recepción."""
        grupo = etree.SubElement(parent, "gGroupGesEve")
        grupo_not = etree.SubElement(grupo, "rGeVeNotRec")

        motivo = etree.SubElement(grupo_not, "mOtEve")
        motivo.text = evento.mOtEve

        num_de = etree.SubElement(grupo_not, "dNumDE")
        num_de.text = evento.dNumDE

        fecha = etree.SubElement(grupo_not, "dFeEmiDE")
        if isinstance(evento.dFeEmiDE, datetime):
            fecha.text = evento.dFeEmiDE.strftime("%Y-%m-%d")
        else:
            fecha.text = str(evento.dFeEmiDE)


def generate_evento_xml(evento: GestionEvento) -> str:
    """
    Genera el XML de un evento.

    Args:
        evento: Objeto GestionEvento.

    Returns:
        XML como string.
    """
    generator = XMLEventoGenerator()
    return generator.generate(evento)
