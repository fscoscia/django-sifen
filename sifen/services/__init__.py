"""
Servicios web SIFEN.

Proporciona clientes para los 6 servicios web de SIFEN:
1. Recepción de DE (síncrono)
2. Recepción de Lote de DEs (asíncrono)
3. Consulta de DE
4. Consulta de Lote
5. Consulta de RUC
6. Recepción de Eventos
"""

from sifen.services.recepcion_de import (
    RecepcionDEService,
    RespuestaRecepcionDE,
    recibir_de,
)

from sifen.services.consulta_ruc import (
    ConsultaRUCService,
    RespuestaConsultaRUC,
    DatosContribuyente,
    consultar_ruc,
)

from sifen.services.consulta_de import (
    ConsultaDEService,
    RespuestaConsultaDE,
    consultar_de,
)

from sifen.services.recepcion_lote import (
    RecepcionLoteService,
    RespuestaRecepcionLote,
    DetalleDocumentoLote,
    recibir_lote,
)

from sifen.services.consulta_lote import (
    ConsultaLoteService,
    RespuestaConsultaLote,
    DocumentoLote,
    consultar_lote,
)

from sifen.services.recepcion_evento import (
    RecepcionEventoService,
    RespuestaRecepcionEvento,
    recibir_evento,
    TIPO_EVENTO_CANCELACION,
    TIPO_EVENTO_INUTILIZACION,
    TIPO_EVENTO_NOTIFICACION_RECEPCION,
    TIPO_EVENTO_CONFORMIDAD,
    TIPO_EVENTO_DISCONFORMIDAD,
    TIPO_EVENTO_DESCONOCIMIENTO,
    TIPO_EVENTO_DEVOLUCION_AJUSTE_PRECIOS,
    TIPO_EVENTO_ASOCIACION,
    TIPO_EVENTO_ASOCIACION_RETENCION,
    TIPO_EVENTO_CREDITOS_FISCALES,
    TIPO_EVENTO_DEVOLUCION_CREDITOS_FISCALES_CUESTIONADO,
    TIPO_EVENTO_DEVOLUCION_CREDITOS_FISCALES_DEVUELTO,
    TIPO_EVENTO_ANTICIPO,
    TIPO_EVENTO_REMISION,
    TIPO_EVENTO_TRANSPORTE,
)

from sifen.services.recepcion_lote_eventos import (
    RecepcionLoteEventosService,
    RespuestaRecepcionLoteEventos,
    DetalleEventoLote,
    recibir_lote_eventos,
)


__all__ = [
    # Recepción DE
    "RecepcionDEService",
    "RespuestaRecepcionDE",
    "recibir_de",
    # Consulta RUC
    "ConsultaRUCService",
    "RespuestaConsultaRUC",
    "DatosContribuyente",
    "consultar_ruc",
    # Consulta DE
    "ConsultaDEService",
    "RespuestaConsultaDE",
    "consultar_de",
    # Recepción Lote
    "RecepcionLoteService",
    "RespuestaRecepcionLote",
    "DetalleDocumentoLote",
    "recibir_lote",
    # Consulta Lote
    "ConsultaLoteService",
    "RespuestaConsultaLote",
    "DocumentoLote",
    "consultar_lote",
    # Recepción Evento
    "RecepcionEventoService",
    "RespuestaRecepcionEvento",
    "recibir_evento",
    "TIPO_EVENTO_CANCELACION",
    "TIPO_EVENTO_INUTILIZACION",
    "TIPO_EVENTO_NOTIFICACION_RECEPCION",
    "TIPO_EVENTO_CONFORMIDAD",
    "TIPO_EVENTO_DISCONFORMIDAD",
    "TIPO_EVENTO_DESCONOCIMIENTO",
    "TIPO_EVENTO_DEVOLUCION_AJUSTE_PRECIOS",
    "TIPO_EVENTO_ASOCIACION",
    "TIPO_EVENTO_ASOCIACION_RETENCION",
    "TIPO_EVENTO_CREDITOS_FISCALES",
    "TIPO_EVENTO_DEVOLUCION_CREDITOS_FISCALES_CUESTIONADO",
    "TIPO_EVENTO_DEVOLUCION_CREDITOS_FISCALES_DEVUELTO",
    "TIPO_EVENTO_ANTICIPO",
    "TIPO_EVENTO_REMISION",
    "TIPO_EVENTO_TRANSPORTE",
    # Recepción Lote Eventos
    "RecepcionLoteEventosService",
    "RespuestaRecepcionLoteEventos",
    "DetalleEventoLote",
    "recibir_lote_eventos",
]
