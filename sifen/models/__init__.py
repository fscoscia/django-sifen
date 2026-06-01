"""
Modelos de datos para documentos electrónicos SIFEN.

Proporciona clases Python para representar todos los campos
del Documento Electrónico según el Manual Técnico v150.
"""

# Clases base
from sifen.models.base import (
    SifenObject,
    IdentificacionDE,
    DatosGeneralesDE,
    Direccion,
    Telefono,
    ActividadEconomica,
)

# Emisor
from sifen.models.emisor import (
    Emisor,
    ResponsableDE,
)

# Receptor
from sifen.models.receptor import Receptor

# Items
from sifen.models.items import (
    Item,
    ValorItem,
    IVAItem,
)

# Totales y condiciones
from sifen.models.totales import (
    Totales,
    SubtotalIVA,
    CondicionOperacion,
    Pago,
    Cuota,
)

# Nota de Crédito/Débito
from sifen.models.nota_credito_debito import NotaCreditoDebito

# Autofactura
from sifen.models.autofactura import Autofactura

# Nota de Remisión
from sifen.models.nota_remision import NotaRemision

# Transporte
from sifen.models.transporte import (
    Transporte,
    LocalSalida,
    LocalEntrega,
    VehiculoTraslado,
    Transportista,
)

# Documento Asociado
from sifen.models.documento_asociado import DocumentoAsociado

# Documento principal
from sifen.models.documento import DocumentoElectronico


__all__ = [
    # Base
    "SifenObject",
    "IdentificacionDE",
    "DatosGeneralesDE",
    "Direccion",
    "Telefono",
    "ActividadEconomica",
    # Emisor
    "Emisor",
    "ResponsableDE",
    # Receptor
    "Receptor",
    # Items
    "Item",
    "ValorItem",
    "IVAItem",
    # Totales
    "Totales",
    "SubtotalIVA",
    "CondicionOperacion",
    "Pago",
    "Cuota",
    # Nota Crédito/Débito
    "NotaCreditoDebito",
    # Autofactura
    "Autofactura",
    # Nota de Remisión
    "NotaRemision",
    # Transporte
    "Transporte",
    "LocalSalida",
    "LocalEntrega",
    "VehiculoTraslado",
    "Transportista",
    # Documento Asociado
    "DocumentoAsociado",
    # Documento
    "DocumentoElectronico",
]
