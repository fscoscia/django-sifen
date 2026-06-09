# Gestión de Eventos en SIFEN

Los eventos permiten gestionar el ciclo de vida de los documentos electrónicos después de su emisión. SIFEN define diferentes tipos de eventos según el actor (emisor o receptor) y la situación.

## Tabla de Contenidos

- [Tipos de Eventos](#tipos-de-eventos)
- [Eventos del Emisor](#eventos-del-emisor)
- [Eventos del Receptor](#eventos-del-receptor)
- [Eventos Automáticos](#eventos-automáticos)
- [Envío de Lotes de Eventos](#envío-de-lotes-de-eventos)
- [Especificaciones Técnicas](#especificaciones-técnicas)

## Tipos de Eventos

### Eventos del Emisor (Registro Requerido)

| Código | Evento | Plazo | Descripción |
|--------|--------|-------|-------------|
| 1 | Cancelación del DTE | 48 horas desde aprobación | Cancela un DE cuando es igual a FE |
| 2 | Inutilización de número de DE | 15 días desde acaecimiento | Inutiliza rangos de numeración no utilizados |

### Eventos del Receptor (Registro Requerido)

| Código | Evento | Plazo | Descripción |
|--------|--------|-------|-------------|
| 10 | Notificación de recepción DE o DTE | 45 días desde emisión | Notifica la recepción del documento |
| 11 | Conformidad DTE | 45 días desde emisión | Confirma total o parcialmente el documento |
| 12 | Disconformidad DTE | 45 días desde emisión | Rechaza el documento con justificación |
| 13 | Desconocimiento DE o DTE | 45 días desde emisión | Indica desconocimiento del documento |

### Eventos Automáticos

| Código | Evento | Generado por | Descripción |
|--------|--------|--------------|-------------|
| 14 | Devolución y Ajuste de precios | SIFEN | Ajusta operación de una FE aprobada |
| 16 | Asociación | SIFEN | Asocia documentos (retención, anticipos, etc.) |
| 17-19 | Créditos Fiscales | SET | Transferencia y devolución de créditos |
| 20 | Anticipo | SIFEN | Evento de anticipo |
| 21 | Remisión | SIFEN | Evento de remisión |
| 22 | Transporte | Emisor/Receptor | Actualización de datos del transporte |

## Eventos del Emisor

### 1. Cancelación de DTE

Permite cancelar un documento electrónico dentro de las 48 horas de su aprobación.

**Condiciones:**
- Hubo errores en la emisión del DE
- La mercadería no fue entregada al cliente
- El servicio no ha sido realizado al cliente

**Ejemplo:**

```python
from sifen import SifenClient

client = SifenClient(config)

# Cancelar un documento
respuesta = client.cancelar_documento(
    cdc="01001001000000112024050412300080012345601",
    motivo="Error en el monto facturado. Se emitirá nuevo documento."
)

if respuesta.aprobado:
    print(f"Documento cancelado. Protocolo: {respuesta.numero_protocolo}")
```

### 2. Inutilización de Numeración

Permite inutilizar rangos de numeración no utilizados (hasta 1000 números por solicitud).

**Condiciones:**
- Saltos de numeración por errores técnicos
- Errores de llenado del DE
- No existe el generador del impuesto

**Ejemplo:**

```python
respuesta = client.inutilizar_numeracion(
    motivo="Error en sistema de facturación",
    timbrado=12345678,
    establecimiento="001",
    punto_expedicion="001",
    numero_inicial="0000100",
    numero_final="0000110",
    tipo_documento=1  # Factura electrónica
)
```

## Eventos del Receptor

### 10. Notificación de Recepción

El receptor notifica que recibió el documento.

```python
from sifen.models.eventos import EventoNotificacionRecepcion
from datetime import datetime

evento = EventoNotificacionRecepcion(
    Id="01001001000000112024050412300080012345601",
    dFecEmi=datetime(2024, 5, 4),
    dFecRecep=datetime.now(),
    iTipRec=1,  # 1=Contribuyente, 2=No Contribuyente
    dNomRec="Empresa Receptora S.A.",
    dRucRec="80000002",
    dDVRec=5,
    iTotalGs=1000000
)
```

### 11. Conformidad (Total o Parcial)

El receptor confirma que el documento es correcto.

```python
# Conformidad total
respuesta = client.enviar_conformidad(
    cdc="01001001000000112024050412300080012345601"
)

# Conformidad parcial (con fecha estimada de recepción)
from sifen.models.eventos import EventoConformidadParcial

evento = EventoConformidadParcial(
    Id="01001001000000112024050412300080012345601",
    iTipConf=2,  # 2=Parcial
    dFecRecep=datetime(2024, 6, 1)
)
```

### 12. Disconformidad

El receptor rechaza el documento por algún motivo.

```python
respuesta = client.enviar_disconformidad(
    cdc="01001001000000112024050412300080012345601",
    motivo="La mercadería recibida no coincide con la facturada"
)
```

### 13. Desconocimiento

El receptor indica que desconoce el documento.

```python
respuesta = client.enviar_desconocimiento(
    cdc="01001001000000112024050412300080012345601",
    motivo="No se recibió el documento electrónico ni la mercadería"
)
```

## Eventos Automáticos

### 16. Asociación de Retención

Asocia un DTE con un documento de retención.

```python
from sifen.models.eventos import EventoAsociacionRetencion

evento = EventoAsociacionRetencion(
    Id="01001001000000112024050412300080012345601",
    dNumTimRet=12345678,
    dEstRet="001",
    dPunExpRet="001",
    dNumDocRet="0000001",
    dCodConRet="RET-2024-001",
    dFeEmiRet=datetime(2024, 5, 4)
)
```

### 22. Actualización de Datos del Transporte

Permite actualizar información del transporte.

```python
from sifen.models.eventos import EventoTransporte

evento = EventoTransporte(
    Id="01001001000000112024050412300080012345601",
    dMotEv=1,  # 1=Cambio local entrega, 2=Cambio chofer, 3=Cambio transportista, 4=Cambio vehículo
    dNomChof="Juan Pérez",
    dNumIDChof="1234567",
    # ... otros campos según el motivo
)
```

## Envío de Lotes de Eventos

SIFEN permite enviar hasta **15 eventos** de cualquier tipo en un solo lote.

**Ejemplo:**

```python
# Preparar eventos
eventos_xml = []

# Evento 1: Cancelación
evento1_xml = preparar_evento_cancelacion(cdc1, motivo1)
eventos_xml.append(evento1_xml)

# Evento 2: Conformidad
evento2_xml = preparar_evento_conformidad(cdc2)
eventos_xml.append(evento2_xml)

# ... hasta 15 eventos

# Enviar lote
respuesta = client.enviar_lote_eventos(eventos_xml)

if respuesta.aprobado:
    print(f"Lote aprobado: {respuesta.numero_lote}")
    
    # Revisar cada evento
    for evento in respuesta.eventos:
        if evento.aprobado:
            print(f"✓ Evento {evento.tipo_evento} aprobado")
        else:
            print(f"✗ Evento {evento.tipo_evento} rechazado: {evento.mensaje}")
```

## Especificaciones Técnicas

### Estructura XML de Eventos

Todos los eventos siguen el formato XML definido en el schema `v150.xsd`:

```xml
<rGesEve Id="EVE20240504123000">
  <dFecFirma>2024-05-04T12:30:00</dFecFirma>
  <gGroupTiEvt>
    <iTipEve>1</iTipEve>
    <dDesTipEve>Cancelación</dDesTipEve>
    <Id_CDC>01001001000000112024050412300080012345601</Id_CDC>
    <mOtEve>Motivo de la cancelación</mOtEve>
  </gGroupTiEvt>
  <Signature>...</Signature>
</rGesEve>
```

### Firma Digital

Todos los eventos deben estar firmados digitalmente con el certificado del emisor o receptor según corresponda.

### Códigos de Respuesta

| Código | Descripción |
|--------|-------------|
| 0600 | Evento aprobado |
| 0601 | Lote de eventos aprobado |
| 0260 | Evento rechazado - Fuera de plazo |
| 0261 | Evento rechazado - Documento no existe |
| 0262 | Evento rechazado - Evento duplicado |

### Relaciones entre Eventos

Algunos eventos no pueden realizarse después de otros:

| Evento Previo | Eventos Bloqueados |
|---------------|-------------------|
| Cancelación | Todos los eventos del receptor |
| Conformidad Total | Conformidad Parcial, Disconformidad |
| Disconformidad | Conformidad (Total o Parcial) |
| Desconocimiento | Todos los eventos del receptor |

## Buenas Prácticas

1. **Validar antes de enviar**: Usa el método `validate()` de cada evento antes de enviarlo.

```python
evento = EventoCancelacion(mOtEve="Motivo")
is_valid, error = evento.validate()
if not is_valid:
    print(f"Error: {error}")
```

2. **Gestionar errores**: Siempre verifica la respuesta de SIFEN.

```python
try:
    respuesta = client.cancelar_documento(cdc, motivo)
    if not respuesta.aprobado:
        # Manejar rechazo
        log_error(respuesta.codigo, respuesta.mensaje)
except Exception as e:
    # Manejar error de comunicación
    log_exception(e)
```

3. **Respetar plazos**: Envía los eventos dentro de los plazos establecidos.

4. **Usar lotes**: Para múltiples eventos, usa el envío por lotes para optimizar.

5. **Guardar comprobantes**: Almacena los números de protocolo y fechas de recepción.

## Referencias

- [Manual Técnico SIFEN v150](https://www.set.gov.py/portal/PARAGUAY-SET/detail?folder-id=repository:collaboration:/sites/PARAGUAY-SET/categories/SET/Ekuatia/Manuales&content-id=/repository/collaboration/sites/PARAGUAY-SET/categories/SET/Ekuatia/Manuales/Manual%20T%C3%A9cnico%20Versi%C3%B3n%20150.pdf)
- [Documentación de Eventos](./EVENTOS_DETALLE.md)
- [Ejemplos de Código](../examples/)

## Soporte

Para consultas sobre eventos:
- Email: soporte@set.gov.py
- Mesa de ayuda: https://ekuatia.set.gov.py
