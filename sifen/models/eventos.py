"""
Modelos de datos para Eventos de Documentos Electrónicos.

Representa los diferentes tipos de eventos que se pueden enviar a SIFEN.
"""

from dataclasses import dataclass, field
from typing import Optional, Tuple
from datetime import datetime

from sifen.models.base import SifenObject


@dataclass
class EventoCancelacion(SifenObject):
    """
    Evento de Cancelación de Documento Electrónico.

    Permite cancelar un DE previamente emitido.
    """

    mOtEve: str  # Motivo del evento (máx 500 caracteres)

    def validate(self) -> Tuple[bool, Optional[str]]:
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

    def validate(self) -> Tuple[bool, Optional[str]]:
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

    def validate(self) -> Tuple[bool, Optional[str]]:
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

    def validate(self) -> Tuple[bool, Optional[str]]:
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

    def validate(self) -> Tuple[bool, Optional[str]]:
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
class EventoNotificacionRecepcion(SifenObject):
    """
    Evento de Notificación de Recepción (Evento 10).

    El receptor notifica que recibió el documento.
    """

    Id: str  # CDC del DE/DTE
    dFecEmi: datetime  # Fecha de emisión del DE/DTE
    dFecRecep: datetime  # Fecha de recepción del DE
    iTipRec: int  # Tipo de receptor (1=Contribuyente, 2=No Contribuyente)
    dNomRec: str  # Nombre o razón social del receptor (4-60 caracteres)
    iTotalGs: int  # Total general de la operación en Guaraníes (1-15 dígitos)
    dRucRec: Optional[str] = None  # RUC del receptor (3-8 dígitos, solo si iTipRec=1)
    dDVRec: Optional[int] = None  # DV del RUC (solo si iTipRec=1)
    dTipIDRec: Optional[int] = (
        None  # Tipo de documento de identidad (solo si iTipRec=2)
    )
    dNumID: Optional[str] = (
        None  # Número de documento de identidad (1-20, solo si iTipRec=2)
    )

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida el evento de notificación de recepción."""
        if len(self.Id) != 44:
            return False, "El CDC debe tener 44 caracteres"

        if self.iTipRec not in [1, 2]:
            return (
                False,
                "Tipo de receptor inválido (1=Contribuyente, 2=No Contribuyente)",
            )

        if len(self.dNomRec) < 4 or len(self.dNomRec) > 60:
            return False, "El nombre del receptor debe tener entre 4 y 60 caracteres"

        if self.iTipRec == 1:
            if not self.dRucRec or len(self.dRucRec) < 3 or len(self.dRucRec) > 8:
                return (
                    False,
                    "El RUC es requerido y debe tener entre 3 y 8 dígitos para contribuyentes",
                )
            if self.dDVRec is None:
                return False, "El DV del RUC es requerido para contribuyentes"

        if self.iTipRec == 2:
            if self.dTipIDRec and self.dTipIDRec not in [1, 2, 3, 4]:
                return False, "Tipo de documento de identidad inválido"

        return True, None


@dataclass
class EventoConformidadParcial(SifenObject):
    """
    Evento de Conformidad Parcial (Evento 11).

    El receptor confirma parcialmente el documento.
    """

    Id: str  # CDC del DTE
    iTipConf: int  # Tipo de conformidad (1=Total, 2=Parcial)
    dFecRecep: Optional[datetime] = (
        None  # Fecha estimada de recepción (obligatorio si iTipConf=2)
    )

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida el evento de conformidad parcial."""
        if len(self.Id) != 44:
            return False, "El CDC debe tener 44 caracteres"

        if self.iTipConf not in [1, 2]:
            return False, "Tipo de conformidad inválido (1=Total, 2=Parcial)"

        if self.iTipConf == 2 and not self.dFecRecep:
            return (
                False,
                "La fecha estimada de recepción es obligatoria para conformidad parcial",
            )

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

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida el evento de notificación de no recepción."""
        if not self.mOtEve or not self.mOtEve.strip():
            return False, "El motivo es requerido"

        if len(self.mOtEve) > 500:
            return False, "El motivo no puede exceder 500 caracteres"

        # Validar formato de número de documento
        partes = self.dNumDE.split("-")
        if len(partes) != 3:
            return (
                False,
                "Formato de número de documento inválido (debe ser 001-001-0000001)",
            )

        return True, None


@dataclass
class EventoAsociacionRetencion(SifenObject):
    """
    Evento Automático de Asociación de Retención (Evento 16).

    Asocia un DTE con un documento de retención.
    """

    Id: str  # CDC del DE/DTE asociado
    dNumTimRet: int  # Número de timbrado del documento de retención
    dEstRet: str  # Establecimiento (3 dígitos)
    dPunExpRet: str  # Punto de expedición (3 dígitos)
    dNumDocRet: str  # Número del documento (7 dígitos)
    dCodConRet: str  # Identificador de la retención (máx 40 caracteres)
    dFeEmiRet: datetime  # Fecha de emisión de la retención

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida el evento de asociación de retención."""
        if len(self.Id) != 44:
            return False, "El CDC debe tener 44 caracteres"

        if len(self.dEstRet) != 3 or not self.dEstRet.isdigit():
            return False, "El establecimiento debe tener 3 dígitos"

        if len(self.dPunExpRet) != 3 or not self.dPunExpRet.isdigit():
            return False, "El punto de expedición debe tener 3 dígitos"

        if len(self.dNumDocRet) != 7 or not self.dNumDocRet.isdigit():
            return False, "El número de documento debe tener 7 dígitos"

        if len(self.dCodConRet) > 40:
            return False, "El identificador de retención no puede exceder 40 caracteres"

        return True, None


@dataclass
class EventoAnulacionRetencion(SifenObject):
    """
    Evento Automático de Anulación de Retención.

    Anula una asociación de retención previamente registrada.
    """

    Id: str  # CDC del DE/DTE asociado
    dNumTimRet: int  # Número de timbrado del documento de retención
    dEstRet: str  # Establecimiento (3 dígitos)
    dPunExpRet: str  # Punto de expedición (3 dígitos)
    dNumDocRet: str  # Número del documento (7 dígitos)
    dCodConRet: str  # Identificador de la retención (máx 40 caracteres)
    dFeEmiRet: datetime  # Fecha de emisión de la retención
    dFecAnRet: datetime  # Fecha de anulación de la retención

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida el evento de anulación de retención."""
        if len(self.Id) != 44:
            return False, "El CDC debe tener 44 caracteres"

        if len(self.dEstRet) != 3 or not self.dEstRet.isdigit():
            return False, "El establecimiento debe tener 3 dígitos"

        if len(self.dPunExpRet) != 3 or not self.dPunExpRet.isdigit():
            return False, "El punto de expedición debe tener 3 dígitos"

        if len(self.dNumDocRet) != 7 or not self.dNumDocRet.isdigit():
            return False, "El número de documento debe tener 7 dígitos"

        return True, None


@dataclass
class EventoCreditosFiscales(SifenObject):
    """
    Evento Automático de Transferencia de Créditos Fiscales.

    Registra la transferencia de créditos fiscales.
    """

    Id: str  # CDC del DE/DTE asociado
    dNumTraCCFF: str  # Número de transferencia de créditos fiscales (máx 10 caracteres)
    dFeAceTraCCFF: datetime  # Fecha de aceptación del crédito fiscal

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida el evento de créditos fiscales."""
        if len(self.Id) != 44:
            return False, "El CDC debe tener 44 caracteres"

        if len(self.dNumTraCCFF) > 10:
            return False, "El número de transferencia no puede exceder 10 caracteres"

        return True, None


@dataclass
class EventoDevolucionCreditosFiscales(SifenObject):
    """
    Evento Automático de Devolución de Créditos Fiscales.

    Registra la devolución de créditos fiscales (cuestionado o devuelto).
    """

    Id: str  # CDC del DE/DTE asociado
    dNumDevSol: str  # Número DIR (máx 10 caracteres)
    dNumDevInf: str  # Número de informe (máx 10 caracteres)
    dNumDevRes: str  # Número de resolución de la devolución (máx 10 caracteres)
    dFeEmiSol: datetime  # Fecha de emisión de DIR
    dFeEmiInf: datetime  # Fecha de emisión del informe
    dFeEmiRes: datetime  # Fecha de emisión de la resolución

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida el evento de devolución de créditos fiscales."""
        if len(self.Id) != 44:
            return False, "El CDC debe tener 44 caracteres"

        if len(self.dNumDevSol) > 10:
            return False, "El número DIR no puede exceder 10 caracteres"

        if len(self.dNumDevInf) > 10:
            return False, "El número de informe no puede exceder 10 caracteres"

        if len(self.dNumDevRes) > 10:
            return False, "El número de resolución no puede exceder 10 caracteres"

        return True, None


@dataclass
class EventoAnticipo(SifenObject):
    """
    Evento Automático por SIFEN: Anticipo.

    Evento generado automáticamente por SIFEN.
    """

    Id: str  # CDC del DTE asociado

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida el evento de anticipo."""
        if len(self.Id) != 44:
            return False, "El CDC debe tener 44 caracteres"

        return True, None


@dataclass
class EventoRemision(SifenObject):
    """
    Evento Automático por SIFEN: Remisión.

    Evento generado automáticamente por SIFEN.
    """

    Id: str  # CDC del DTE asociado

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida el evento de remisión."""
        if len(self.Id) != 44:
            return False, "El CDC debe tener 44 caracteres"

        return True, None


@dataclass
class EventoTransporte(SifenObject):
    """
    Evento por Actualización de Datos: Datos del Transporte.

    Permite actualizar información del transporte.
    """

    Id: str  # CDC del DTE
    dMotEv: int  # Motivo del evento (1-4)
    cDepEnt: Optional[str] = None  # Código del departamento del local de entrega
    dDesDepEnt: Optional[str] = None  # Descripción del departamento (6-16 caracteres)
    cDisEnt: Optional[str] = None  # Código del distrito (1-4 dígitos)
    dDesDisEnt: Optional[str] = None  # Descripción del distrito (1-30 caracteres)
    cCiuEnt: Optional[str] = None  # Código de la ciudad (1-5 dígitos)
    dDesCiuEnt: Optional[str] = None  # Descripción de la ciudad (1-30 caracteres)
    dDirEnt: Optional[str] = None  # Dirección del local de entrega (1-255 caracteres)
    dNumCas: Optional[str] = None  # Número de casa (1-6 dígitos)
    dCompDir1: Optional[str] = None  # Complemento de dirección (1-255 caracteres)
    dNomChof: Optional[str] = None  # Nombre del chofer (4-60 caracteres)
    dNumIDChof: Optional[str] = None  # Número de documento del chofer (1-20 caracteres)
    iNatTrans: Optional[int] = (
        None  # Naturaleza del transportista (1=Contribuyente, 2=No contribuyente)
    )
    dRucTrans: Optional[str] = None  # RUC del transportista (3-8 dígitos)
    dDVTrans: Optional[int] = None  # DV del RUC del transportista
    dNomTrans: Optional[str] = None  # Nombre del transportista (4-60 caracteres)
    iTipIDTrans: Optional[int] = (
        None  # Tipo de documento de identidad del transportista
    )
    dDTipIDTrans: Optional[str] = (
        None  # Descripción del tipo de documento (9-20 caracteres)
    )
    dNumIDTrans: Optional[str] = (
        None  # Número de documento del transportista (1-20 caracteres)
    )
    iTipTrans: Optional[int] = None  # Tipo de transporte (1=Propio, 2=Tercero)
    dDesTipTrans: Optional[str] = (
        None  # Descripción del tipo de transporte (6-7 caracteres)
    )
    iModTrans: Optional[int] = None  # Modalidad del transporte (1-4)
    dDesModTrans: Optional[str] = None  # Descripción de la modalidad (5-10 caracteres)
    dTiVehTras: Optional[str] = None  # Tipo de vehículo (4-10 caracteres)
    dMarVeh: Optional[str] = None  # Marca del vehículo (1-10 caracteres)
    dTipIdenVeh: Optional[int] = None  # Tipo de identificación del vehículo
    dNroIDVeh: Optional[str] = (
        None  # Número de identificación del vehículo (1-20 caracteres)
    )
    dNroMatVeh: Optional[str] = None  # Número de matrícula del vehículo (6 caracteres)

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida el evento de transporte."""
        if len(self.Id) != 44:
            return False, "El CDC debe tener 44 caracteres"

        if self.dMotEv not in [1, 2, 3, 4]:
            return False, "Motivo del evento inválido (debe ser 1-4)"

        return True, None


@dataclass
class GestionEvento(SifenObject):
    """
    Gestión de Evento.

    Agrupa la información del evento a enviar.
    """

    Id: str  # ID del evento
    dFecFirma: datetime  # Fecha y hora de firma
    iTipEve: int  # Tipo de evento (1-16)
    dDesTipEve: str  # Descripción del tipo de evento
    Id_CDC: str  # CDC del documento al que aplica el evento
    mOtEve: Optional[str] = None  # Motivo del evento

    # Eventos específicos (solo uno debe estar presente)
    gGroupGesEve: Optional[SifenObject] = None

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida la gestión de evento."""
        if not self.Id or not self.Id.strip():
            return False, "El ID del evento es requerido"

        if not self.Id_CDC or len(self.Id_CDC) != 44:
            return False, "El CDC debe tener 44 caracteres"

        if self.iTipEve < 1 or self.iTipEve > 16:
            return False, "Tipo de evento inválido (debe estar entre 1 y 16)"

        if self.gGroupGesEve:
            is_valid, error = self.gGroupGesEve.validate()
            if not is_valid:
                return False, error

        return True, None
