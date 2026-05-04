"""
Modelos de datos para Eventos de Documentos Electrónicos.

Representa los diferentes tipos de eventos que se pueden enviar a SIFEN.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from sifen.models.base import SifenObject


@dataclass
class EventoCancelacion(SifenObject):
    """
    Evento de Cancelación de Documento Electrónico.
    
    Permite cancelar un DE previamente emitido.
    """
    
    mOtEve: str  # Motivo del evento (máx 500 caracteres)
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Valida el evento de cancelación."""
        if not self.mOtEve or not self.mOtEve.strip():
            return False, "El motivo de cancelación es requerido"
        
        if len(self.mOtEve) > 500:
            return False, "El motivo no puede exceder 500 caracteres"
        
        return True, None


@dataclass
class EventoConformidad(SifenObject):
    """
    Evento de Conformidad del Receptor.
    
    El receptor confirma que recibió el documento correctamente.
    """
    
    mOtEve: Optional[str] = None  # Motivo (opcional, máx 500 caracteres)
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Valida el evento de conformidad."""
        if self.mOtEve and len(self.mOtEve) > 500:
            return False, "El motivo no puede exceder 500 caracteres"
        
        return True, None


@dataclass
class EventoDisconformidad(SifenObject):
    """
    Evento de Disconformidad del Receptor.
    
    El receptor rechaza el documento por algún motivo.
    """
    
    mOtEve: str  # Motivo de disconformidad (requerido, máx 500 caracteres)
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Valida el evento de disconformidad."""
        if not self.mOtEve or not self.mOtEve.strip():
            return False, "El motivo de disconformidad es requerido"
        
        if len(self.mOtEve) > 500:
            return False, "El motivo no puede exceder 500 caracteres"
        
        return True, None


@dataclass
class EventoDesconocimiento(SifenObject):
    """
    Evento de Desconocimiento del Receptor.
    
    El receptor indica que desconoce el documento.
    """
    
    mOtEve: str  # Motivo de desconocimiento (requerido, máx 500 caracteres)
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Valida el evento de desconocimiento."""
        if not self.mOtEve or not self.mOtEve.strip():
            return False, "El motivo de desconocimiento es requerido"
        
        if len(self.mOtEve) > 500:
            return False, "El motivo no puede exceder 500 caracteres"
        
        return True, None


@dataclass
class EventoInutilizacion(SifenObject):
    """
    Evento de Inutilización de Numeración.
    
    Permite inutilizar rangos de numeración no utilizados.
    """
    
    mOtEve: str  # Motivo de inutilización (requerido, máx 500 caracteres)
    dNumTim: int  # Número de timbrado
    dEst: str  # Establecimiento (3 dígitos)
    dPunExp: str  # Punto de expedición (3 dígitos)
    dNumIn: str  # Número inicial (7 dígitos)
    dNumFin: str  # Número final (7 dígitos)
    iTiDE: int  # Tipo de documento electrónico
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Valida el evento de inutilización."""
        if not self.mOtEve or not self.mOtEve.strip():
            return False, "El motivo de inutilización es requerido"
        
        if len(self.mOtEve) > 500:
            return False, "El motivo no puede exceder 500 caracteres"
        
        if len(self.dEst) != 3 or not self.dEst.isdigit():
            return False, "El establecimiento debe tener 3 dígitos"
        
        if len(self.dPunExp) != 3 or not self.dPunExp.isdigit():
            return False, "El punto de expedición debe tener 3 dígitos"
        
        if len(self.dNumIn) != 7 or not self.dNumIn.isdigit():
            return False, "El número inicial debe tener 7 dígitos"
        
        if len(self.dNumFin) != 7 or not self.dNumFin.isdigit():
            return False, "El número final debe tener 7 dígitos"
        
        if int(self.dNumIn) > int(self.dNumFin):
            return False, "El número inicial no puede ser mayor al final"
        
        return True, None


@dataclass
class EventoNotificacionNoRecepcion(SifenObject):
    """
    Evento de Notificación de No Recepción.
    
    El receptor notifica que no recibió el documento.
    """
    
    mOtEve: str  # Motivo (requerido, máx 500 caracteres)
    dNumDE: str  # Número del documento (formato: 001-001-0000001)
    dFeEmiDE: datetime  # Fecha de emisión del DE
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Valida el evento de notificación de no recepción."""
        if not self.mOtEve or not self.mOtEve.strip():
            return False, "El motivo es requerido"
        
        if len(self.mOtEve) > 500:
            return False, "El motivo no puede exceder 500 caracteres"
        
        # Validar formato de número de documento
        partes = self.dNumDE.split('-')
        if len(partes) != 3:
            return False, "Formato de número de documento inválido (debe ser 001-001-0000001)"
        
        return True, None


@dataclass
class GestionEvento(SifenObject):
    """
    Gestión de Evento.
    
    Agrupa la información del evento a enviar.
    """
    
    Id: str  # ID del evento
    dFecFirma: datetime  # Fecha y hora de firma
    iTipEve: int  # Tipo de evento (1-14)
    dDesTipEve: str  # Descripción del tipo de evento
    Id_CDC: str  # CDC del documento al que aplica el evento
    mOtEve: Optional[str] = None  # Motivo del evento
    
    # Eventos específicos (solo uno debe estar presente)
    gGroupGesEve: Optional[SifenObject] = None
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Valida la gestión de evento."""
        if not self.Id or not self.Id.strip():
            return False, "El ID del evento es requerido"
        
        if not self.Id_CDC or len(self.Id_CDC) != 44:
            return False, "El CDC debe tener 44 caracteres"
        
        if self.iTipEve < 1 or self.iTipEve > 14:
            return False, "Tipo de evento inválido (debe estar entre 1 y 14)"
        
        if self.gGroupGesEve:
            is_valid, error = self.gGroupGesEve.validate()
            if not is_valid:
                return False, error
        
        return True, None
