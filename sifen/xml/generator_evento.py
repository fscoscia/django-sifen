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
    EventoNotificacionNoRecepcion,
)


class XMLEventoGenerator:
    """Generador de XML para eventos."""
    
    def __init__(self):
        """Inicializa el generador."""
        self.namespace = NAMESPACE_SIFEN
    
    def generate(self, evento: GestionEvento) -> str:
        """
        Genera el XML de un evento.
        
        Args:
            evento: Objeto GestionEvento.
        
        Returns:
            XML como string.
        """
        # Crear elemento raíz
        root = etree.Element(
            'rGesEve',
            nsmap={None: self.namespace},
            Id=evento.Id
        )
        
        # Agregar fecha de firma
        fecha_elem = etree.SubElement(root, 'dFecFirma')
        fecha_elem.text = evento.dFecFirma.strftime('%Y-%m-%dT%H:%M:%S')
        
        # Agregar tipo de evento
        tipo_elem = etree.SubElement(root, 'gGroupTiEvt')
        
        itipeve_elem = etree.SubElement(tipo_elem, 'iTipEve')
        itipeve_elem.text = str(evento.iTipEve)
        
        destipeve_elem = etree.SubElement(tipo_elem, 'dDesTipEve')
        destipeve_elem.text = evento.dDesTipEve
        
        # Agregar CDC del documento
        cdc_elem = etree.SubElement(tipo_elem, 'Id_CDC')
        cdc_elem.text = evento.Id_CDC
        
        # Agregar motivo si existe
        if evento.mOtEve:
            motivo_elem = etree.SubElement(tipo_elem, 'mOtEve')
            motivo_elem.text = evento.mOtEve
        
        # Agregar datos específicos del evento
        if evento.gGroupGesEve:
            self._add_evento_especifico(tipo_elem, evento.gGroupGesEve, evento.iTipEve)
        
        # Convertir a string
        xml_string = etree.tostring(
            root,
            encoding='unicode',
            pretty_print=True,
            xml_declaration=True
        )
        
        return xml_string
    
    def _add_evento_especifico(
        self,
        parent: etree.Element,
        evento_obj: object,
        tipo_evento: int
    ):
        """
        Agrega los datos específicos de cada tipo de evento.
        
        Args:
            parent: Elemento padre.
            evento_obj: Objeto del evento específico.
            tipo_evento: Tipo de evento.
        """
        if tipo_evento == 1:  # Cancelación
            self._add_cancelacion(parent, evento_obj)
        elif tipo_evento == 2:  # Inutilización
            self._add_inutilizacion(parent, evento_obj)
        elif tipo_evento == 3:  # Conformidad
            self._add_conformidad(parent, evento_obj)
        elif tipo_evento == 4:  # Disconformidad
            self._add_disconformidad(parent, evento_obj)
        elif tipo_evento == 5:  # Desconocimiento
            self._add_desconocimiento(parent, evento_obj)
        elif tipo_evento == 6:  # Notificación no recepción
            self._add_notificacion_no_recepcion(parent, evento_obj)
    
    def _add_cancelacion(self, parent: etree.Element, evento: EventoCancelacion):
        """Agrega datos de cancelación."""
        grupo = etree.SubElement(parent, 'gGroupGesEve')
        grupo_canc = etree.SubElement(grupo, 'rGeVeCan')
        
        motivo = etree.SubElement(grupo_canc, 'mOtEve')
        motivo.text = evento.mOtEve
    
    def _add_inutilizacion(self, parent: etree.Element, evento: EventoInutilizacion):
        """Agrega datos de inutilización."""
        grupo = etree.SubElement(parent, 'gGroupGesEve')
        grupo_inu = etree.SubElement(grupo, 'rGeVeInu')
        
        motivo = etree.SubElement(grupo_inu, 'mOtEve')
        motivo.text = evento.mOtEve
        
        timbrado = etree.SubElement(grupo_inu, 'dNumTim')
        timbrado.text = str(evento.dNumTim)
        
        est = etree.SubElement(grupo_inu, 'dEst')
        est.text = evento.dEst
        
        punto = etree.SubElement(grupo_inu, 'dPunExp')
        punto.text = evento.dPunExp
        
        num_in = etree.SubElement(grupo_inu, 'dNumIn')
        num_in.text = evento.dNumIn
        
        num_fin = etree.SubElement(grupo_inu, 'dNumFin')
        num_fin.text = evento.dNumFin
        
        tipo = etree.SubElement(grupo_inu, 'iTiDE')
        tipo.text = str(evento.iTiDE)
    
    def _add_conformidad(self, parent: etree.Element, evento: EventoConformidad):
        """Agrega datos de conformidad."""
        grupo = etree.SubElement(parent, 'gGroupGesEve')
        grupo_conf = etree.SubElement(grupo, 'rGeVeConf')
        
        if evento.mOtEve:
            motivo = etree.SubElement(grupo_conf, 'mOtEve')
            motivo.text = evento.mOtEve
    
    def _add_disconformidad(self, parent: etree.Element, evento: EventoDisconformidad):
        """Agrega datos de disconformidad."""
        grupo = etree.SubElement(parent, 'gGroupGesEve')
        grupo_disconf = etree.SubElement(grupo, 'rGeVeDisconf')
        
        motivo = etree.SubElement(grupo_disconf, 'mOtEve')
        motivo.text = evento.mOtEve
    
    def _add_desconocimiento(self, parent: etree.Element, evento: EventoDesconocimiento):
        """Agrega datos de desconocimiento."""
        grupo = etree.SubElement(parent, 'gGroupGesEve')
        grupo_desc = etree.SubElement(grupo, 'rGeVeDescon')
        
        motivo = etree.SubElement(grupo_desc, 'mOtEve')
        motivo.text = evento.mOtEve
    
    def _add_notificacion_no_recepcion(
        self,
        parent: etree.Element,
        evento: EventoNotificacionNoRecepcion
    ):
        """Agrega datos de notificación de no recepción."""
        grupo = etree.SubElement(parent, 'gGroupGesEve')
        grupo_not = etree.SubElement(grupo, 'rGeVeNotRec')
        
        motivo = etree.SubElement(grupo_not, 'mOtEve')
        motivo.text = evento.mOtEve
        
        num_de = etree.SubElement(grupo_not, 'dNumDE')
        num_de.text = evento.dNumDE
        
        fecha = etree.SubElement(grupo_not, 'dFeEmiDE')
        if isinstance(evento.dFeEmiDE, datetime):
            fecha.text = evento.dFeEmiDE.strftime('%Y-%m-%d')
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
