"""
Modelos para Nota de Remisión Electrónica.

Grupo E6 - Campos específicos para NRE según Manual Técnico v150.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional, Tuple

from .base import SifenObject


@dataclass
class NotaRemision(SifenObject):
    """
    Grupo E6 - Campos de la Nota de Remisión Electrónica (gCamNRE).

    Obligatorio si iTiDE = 7 (Nota de Remisión).
    No informar si iTiDE ≠ 7.

    La nota de remisión se emite para documentar el traslado de mercaderías
    sin que implique una venta inmediata.

    Según Manual Técnico v150, sección E6 (E500-E599).
    """

    # E501 - Motivo de emisión
    iMotEmiNR: int = field(metadata={"required": True})

    # E502 - Descripción del motivo de emisión
    dDesMotEmiNR: str = field(metadata={"required": True})

    # E503 - Responsable de la emisión de la Nota de Remisión Electrónica
    iRespEmiNR: int = field(metadata={"required": True})

    # E504 - Descripción del responsable de la emisión de la Nota de Remisión Electrónica
    dDesRespEmiNR: str = field(metadata={"required": True})

    # E505 - Kilómetros estimados de recorrido (opcional)
    dKmR: Optional[str] = field(default=None, metadata={"required": False})

    # E506 - Fecha futura de emisión de la factura (opcional)
    dFecEm: Optional[date] = field(default=None, metadata={"required": False})

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Valida los campos de nota de remisión."""
        # Validar motivo de emisión (1-14, 99)
        valid_motivos = list(range(1, 15)) + [99]
        if self.iMotEmiNR not in valid_motivos:
            return False, f"Motivo de emisión inválido: {self.iMotEmiNR}"

        # Validar descripción según motivo
        if self.dDesMotEmiNR != DESCRIPCIONES_MOTIVO.get(self.iMotEmiNR):
            return (
                False,
                f"Descripción de motivo no corresponde al código {self.iMotEmiNR}. Debe ser: {DESCRIPCIONES_MOTIVO.get(self.iMotEmiNR)}",
            )

        # Validar responsable de emisión (1-5)
        if self.iRespEmiNR not in [1, 2, 3, 4, 5]:
            return False, f"Responsable de emisión inválido: {self.iRespEmiNR}"

        # Validar descripción según responsable
        if self.dDesRespEmiNR != DESCRIPCIONES_RESPONSABLE.get(self.iRespEmiNR):
            return (
                False,
                f"Descripción del responsable no corresponde al código {self.iRespEmiNR}. Debe ser: {DESCRIPCIONES_RESPONSABLE.get(self.iRespEmiNR)}",
            )

        # Validar longitud de kilómetros (1-5 caracteres)
        if self.dKmR is not None:
            if len(self.dKmR) < 1 or len(self.dKmR) > 5:
                return False, "Kilómetros debe tener entre 1 y 5 caracteres"

        # Validar fecha futura de emisión
        # Obs: Informar cuando no se ha emitido aún la factura electrónica, en caso que corresponda
        if self.dFecEm is not None:
            # La fecha debe ser válida (el tipo date ya valida esto)
            pass

        return True, None


# Constantes para motivo de emisión (E501)
MOTIVO_TRASLADO_VENTA = 1
MOTIVO_TRASLADO_CONSIGNACION = 2
MOTIVO_EXPORTACION = 3
MOTIVO_TRASLADO_COMPRA = 4
MOTIVO_IMPORTACION = 5
MOTIVO_TRASLADO_DEVOLUCION = 6
MOTIVO_TRASLADO_LOCALES = 7
MOTIVO_TRASLADO_TRANSFORMACION = 8
MOTIVO_TRASLADO_REPARACION = 9
MOTIVO_TRASLADO_EMISOR_MOVIL = 10
MOTIVO_EXHIBICION_DEMOSTRACION = 11
MOTIVO_PARTICIPACION_FERIAS = 12
MOTIVO_TRASLADO_ENCOMIENDA = 13
MOTIVO_DECOMISO = 14
MOTIVO_OTRO = 99

# Descripciones de motivo de emisión
DESCRIPCIONES_MOTIVO = {
    MOTIVO_TRASLADO_VENTA: "Traslado por venta",
    MOTIVO_TRASLADO_CONSIGNACION: "Traslado por consignación",
    MOTIVO_EXPORTACION: "Exportación",
    MOTIVO_TRASLADO_COMPRA: "Traslado por compra",
    MOTIVO_IMPORTACION: "Importación",
    MOTIVO_TRASLADO_DEVOLUCION: "Traslado por devolución",
    MOTIVO_TRASLADO_LOCALES: "Traslado entre locales de la empresa",
    MOTIVO_TRASLADO_TRANSFORMACION: "Traslado de bienes por transformación",
    MOTIVO_TRASLADO_REPARACION: "Traslado de bienes por reparación",
    MOTIVO_TRASLADO_EMISOR_MOVIL: "Traslado por emisor móvil",
    MOTIVO_EXHIBICION_DEMOSTRACION: "Exhibición o demostración",
    MOTIVO_PARTICIPACION_FERIAS: "Participación en ferias",
    MOTIVO_TRASLADO_ENCOMIENDA: "Traslado de encomienda",
    MOTIVO_DECOMISO: "Decomiso",
    MOTIVO_OTRO: "Otro",
}

# Constantes para responsable de emisión (E503)
RESPONSABLE_EMISOR = 1
RESPONSABLE_POSEEDOR = 2
RESPONSABLE_EMPRESA_TRANSPORTISTA = 3
RESPONSABLE_DESPACHANTE_ADUANAS = 4
RESPONSABLE_AGENTE_TRANSPORTE = 5

# Descripciones de responsable de emisión
DESCRIPCIONES_RESPONSABLE = {
    RESPONSABLE_EMISOR: "Emisor de la factura",
    RESPONSABLE_POSEEDOR: "Poseedor de la factura y bienes",
    RESPONSABLE_EMPRESA_TRANSPORTISTA: "Empresa transportista",
    RESPONSABLE_DESPACHANTE_ADUANAS: "Despachante de Aduanas",
    RESPONSABLE_AGENTE_TRANSPORTE: "Agente de transporte o intermediario",
}
