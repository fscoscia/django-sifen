# Notas de Débito Electrónicas - Guía Completa

## ¿Qué es una Nota de Débito?

Una **Nota de Débito Electrónica** (iTiDE=6) es un documento que se emite para **aumentar el monto** de una factura previamente emitida. Se utiliza para:

- **Recupero de costos**: Gastos de flete, embalaje, seguros
- **Recupero de gastos**: Gastos administrativos adicionales
- **Ajustes de precio**: Correcciones al alza en el precio
- **Intereses**: Por mora en el pago

## Diferencias con Nota de Crédito

| Aspecto | Nota de Crédito | Nota de Débito |
|---------|----------------|----------------|
| **Efecto** | Disminuye el monto | Aumenta el monto |
| **Uso típico** | Devoluciones, descuentos | Cargos adicionales, intereses |
| **Saldo final** | Factura - NC | Factura + ND |

## Requisitos Obligatorios

1. **Documento Asociado** (`gCamDEAsoc`): Referencia a la factura original
2. **Grupo NC/DE** (`gCamNCDE`): Motivo de emisión de la nota
3. **iTiDE**: Debe ser 6 (Nota de débito electrónica)
4. **iTiOpe**: Debe ser 1 (venta)
5. **iTipTra**: NO se incluye (a diferencia de facturas)

## Motivos de Emisión

```python
from sifen.models.nota_credito_debito import (
    MOTIVO_DEVOLUCION_AJUSTE,
    MOTIVO_DEVOLUCION,
    MOTIVO_DESCUENTO,
    MOTIVO_BONIFICACION,
    MOTIVO_CREDITO_INCOBRABLE,
    MOTIVO_RECUPERO_COSTO,      # ← Común para ND
    MOTIVO_RECUPERO_GASTO,      # ← Común para ND
    MOTIVO_AJUSTE_PRECIO,       # ← Común para ND
    DESCRIPCIONES_MOTIVOS,
)
```

### Motivos más comunes para Notas de Débito:

- **Motivo 6** - Recupero de costo: Cargos por flete, embalaje, seguros
- **Motivo 7** - Recupero de gasto: Gastos administrativos
- **Motivo 8** - Ajuste de precio: Correcciones al alza

## Ejemplo Completo

```python
from decimal import Decimal
from datetime import datetime
from sifen.client import SifenClient
from sifen.config import SifenConfig, TipoAmbiente
from sifen.models import (
    DocumentoElectronico,
    IdentificacionDE,
    DatosGeneralesDE,
    Emisor,
    Receptor,
    Item,
    NotaCreditoDebito,
    DocumentoAsociado,
)
from sifen.utils import calcular_valor_item, calcular_totales
from sifen.models.nota_credito_debito import MOTIVO_RECUPERO_COSTO, DESCRIPCIONES_MOTIVOS
from sifen.models.documento_asociado import (
    TIPO_DOC_ASOCIADO_ELECTRONICO,
    DESCRIPCIONES_TIPO_DOC_ASOCIADO,
)
from sifen.constants import TIPO_NOTA_DEBITO_ELECTRONICA

# 1. Configurar cliente
config = SifenConfig(
    ambiente=TipoAmbiente.DEV,
    certificado_archivo="certificado.pfx",
    certificado_contrasena="password",
    csc="ABCD0000000000000000000000000000",
    csc_id="0001",
)
client = SifenClient(config)

# 2. Obtener CDC de la factura original
# (Debe haberse enviado previamente y estar aprobada)
cdc_factura = "01800159272001001000000462026041612345678901234567890123"

# 3. Crear item de cargo adicional
item_cargo = Item(
    dCodInt="CARGO001",
    dDesProSer="CARGO POR FLETE - ENVÍO ESPECIAL",
    cUniMed=77,  # Unidad
    dCantProSer=Decimal("1"),
    gValorItem=calcular_valor_item(
        precio_unitario=Decimal("50000"),
        cantidad=Decimal("1"),
        tasa_iva=10,
    ),
)

totales = calcular_totales([item_cargo])

# 4. Crear grupo de Nota de Débito
nota_debito = NotaCreditoDebito(
    iMotEmi=MOTIVO_RECUPERO_COSTO,
    dDesMotEmi=DESCRIPCIONES_MOTIVOS[MOTIVO_RECUPERO_COSTO],
)

# 5. Referenciar la factura original
doc_asociado = DocumentoAsociado(
    iTipDocAso=TIPO_DOC_ASOCIADO_ELECTRONICO,
    dDesTipDocAso=DESCRIPCIONES_TIPO_DOC_ASOCIADO[TIPO_DOC_ASOCIADO_ELECTRONICO],
    dCdCDERef=cdc_factura,
)

# 6. Crear la nota de débito
nd = DocumentoElectronico(
    dVerFor=150,
    gTimb=IdentificacionDE(
        iTiDE=TIPO_NOTA_DEBITO_ELECTRONICA,  # 6
        dDesTiDE="Nota de débito electrónica",
        dNumTim=80159272,
        dEst="001",
        dPunExp="001",
        dNumDoc="0000050",
        dFeIniT=datetime.strptime("2026-04-16", "%Y-%m-%d").date(),
    ),
    gDatGralOpe=DatosGeneralesDE(
        dFeEmiDE=datetime.now(),
        iTipEmi=1,
        dDesTipEmi="Normal",
        dCodSeg="123456789",
        dInfoEmi="Nota de débito por cargo de flete",
        dInfoFisc="Información de interés del Fisco",
        # NO incluir iTipTra ni dDesTipTra
        iTImp=1,
        dDesTImp="IVA",
        cMoneOpe="PYG",
        dDesMoneOpe="guarani",
    ),
    gEmis=Emisor(...),  # Mismo emisor que la factura
    gDatRec=Receptor(...),  # Mismo receptor que la factura
    gCamItem=[item_cargo],
    gTotSub=totales,
    gCamNCDE=nota_debito,  # ← Grupo de NC/DE
    gCamDEAsoc=doc_asociado,  # ← Referencia a factura
)

# 7. Enviar la nota de débito
respuesta = client.enviar_documento(nd)

if respuesta.aprobado:
    print(f"✓ Nota de Débito aprobada!")
    print(f"  CDC: {respuesta.cdc}")
    print(f"  Protocolo: {respuesta.numero_protocolo}")
else:
    print(f"✗ Rechazada: {respuesta.mensaje}")
```

## Flujo de Trabajo

```
1. Factura Original
   ├─ Total: Gs. 500.000
   └─ CDC: 01800159272...
   
2. Nota de Débito
   ├─ Cargo adicional: Gs. 50.000
   ├─ Motivo: Recupero de costo
   └─ Referencia: CDC de factura
   
3. Saldo Final
   └─ Total: Gs. 550.000 (500.000 + 50.000)
```

## Casos de Uso Comunes

### 1. Cargo por Flete

```python
item = Item(
    dCodInt="FLETE001",
    dDesProSer="CARGO POR FLETE - ENVÍO EXPRESS",
    cUniMed=77,
    dCantProSer=Decimal("1"),
    gValorItem=calcular_valor_item(
        precio_unitario=Decimal("30000"),
        cantidad=Decimal("1"),
        tasa_iva=10,
    ),
)

nota_debito = NotaCreditoDebito(
    iMotEmi=MOTIVO_RECUPERO_COSTO,
    dDesMotEmi=DESCRIPCIONES_MOTIVOS[MOTIVO_RECUPERO_COSTO],
)
```

### 2. Intereses por Mora

```python
item = Item(
    dCodInt="INTERES001",
    dDesProSer="INTERESES POR MORA - PAGO FUERA DE TÉRMINO",
    cUniMed=77,
    dCantProSer=Decimal("1"),
    gValorItem=calcular_valor_item(
        precio_unitario=Decimal("25000"),
        cantidad=Decimal("1"),
        tasa_iva=10,
    ),
)

nota_debito = NotaCreditoDebito(
    iMotEmi=MOTIVO_RECUPERO_GASTO,
    dDesMotEmi=DESCRIPCIONES_MOTIVOS[MOTIVO_RECUPERO_GASTO],
)
```

### 3. Ajuste de Precio

```python
item = Item(
    dCodInt="AJUSTE001",
    dDesProSer="AJUSTE DE PRECIO - CORRECCIÓN AL ALZA",
    cUniMed=77,
    dCantProSer=Decimal("1"),
    gValorItem=calcular_valor_item(
        precio_unitario=Decimal("20000"),
        cantidad=Decimal("1"),
        tasa_iva=10,
    ),
)

nota_debito = NotaCreditoDebito(
    iMotEmi=MOTIVO_AJUSTE_PRECIO,
    dDesMotEmi=DESCRIPCIONES_MOTIVOS[MOTIVO_AJUSTE_PRECIO],
)
```

## Validaciones Importantes

### ✓ Campos Obligatorios

- `gCamNCDE`: Grupo de NC/DE con motivo
- `gCamDEAsoc`: Documento asociado con CDC de factura
- `iTiDE=6`: Tipo de documento
- `iTiOpe=1`: Tipo de operación (venta)

### ✗ Campos NO Permitidos

- `iTipTra`: No se incluye en notas de débito
- `dDesTipTra`: No se incluye en notas de débito
- `gPaConEIni`: Condición de pago (opcional, generalmente no se usa)

### Validación del CDC

El CDC de la factura original debe:
- Tener exactamente 44 caracteres
- Corresponder a un documento aprobado en SIFEN
- Ser del mismo emisor que emite la ND

## Errores Comunes

### Error: "Documento asociado es obligatorio"

**Causa**: No se incluyó `gCamDEAsoc`  
**Solución**: Agregar la referencia al documento original

```python
# ✗ Incorrecto
nd = DocumentoElectronico(
    gCamNCDE=nota_debito,
    # falta gCamDEAsoc
)

# ✓ Correcto
nd = DocumentoElectronico(
    gCamNCDE=nota_debito,
    gCamDEAsoc=doc_asociado,  # ← Agregar referencia
)
```

### Error: "Grupo NC/DE es obligatorio"

**Causa**: No se incluyó `gCamNCDE`  
**Solución**: Agregar el grupo con el motivo

```python
# ✓ Correcto
nd = DocumentoElectronico(
    gCamNCDE=NotaCreditoDebito(
        iMotEmi=MOTIVO_RECUPERO_COSTO,
        dDesMotEmi=DESCRIPCIONES_MOTIVOS[MOTIVO_RECUPERO_COSTO],
    ),
    gCamDEAsoc=doc_asociado,
)
```

### Error: "iTipTra no debe estar presente"

**Causa**: Se incluyó `iTipTra` en `gDatGralOpe`  
**Solución**: Remover `iTipTra` y `dDesTipTra`

```python
# ✗ Incorrecto
gDatGralOpe=DatosGeneralesDE(
    iTipTra=1,  # ← NO incluir
    dDesTipTra="Venta de mercadería",  # ← NO incluir
)

# ✓ Correcto
gDatGralOpe=DatosGeneralesDE(
    # No incluir iTipTra ni dDesTipTra
    iTImp=1,
    dDesTImp="IVA",
)
```

## Ejemplo Ejecutable

Ver el archivo completo en:
```
examples/flujo_completo_nd.py
```

Para ejecutarlo:
```bash
python examples/flujo_completo_nd.py
```

## Resumen

1. **Crear factura** y guardar su CDC
2. **Crear NotaCreditoDebito** con motivo apropiado
3. **Crear DocumentoAsociado** con CDC de factura
4. **Crear DocumentoElectronico** con:
   - `iTiDE=6`
   - `gCamNCDE` (grupo NC/DE)
   - `gCamDEAsoc` (documento asociado)
   - Items con cargos adicionales
5. **Enviar** con `client.enviar_documento(nd)`

## Constantes Disponibles

```python
from sifen.constants import TIPO_NOTA_DEBITO_ELECTRONICA  # 6

from sifen.models.nota_credito_debito import (
    MOTIVO_DEVOLUCION_AJUSTE,      # 1
    MOTIVO_DEVOLUCION,             # 2
    MOTIVO_DESCUENTO,              # 3
    MOTIVO_BONIFICACION,           # 4
    MOTIVO_CREDITO_INCOBRABLE,     # 5
    MOTIVO_RECUPERO_COSTO,         # 6 ← Común para ND
    MOTIVO_RECUPERO_GASTO,         # 7 ← Común para ND
    MOTIVO_AJUSTE_PRECIO,          # 8 ← Común para ND
    DESCRIPCIONES_MOTIVOS,
)

from sifen.models.documento_asociado import (
    TIPO_DOC_ASOCIADO_ELECTRONICO,  # 1
    DESCRIPCIONES_TIPO_DOC_ASOCIADO,
)
```
