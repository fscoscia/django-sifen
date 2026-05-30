# Documento Asociado - Guía de Uso

## ¿Qué es un Documento Asociado?

El **Documento Asociado** (`gCamDEAsoc`) es una referencia a un documento previamente emitido que se está modificando o relacionando. Es **obligatorio** para:

- **Notas de Crédito** (iTiDE=5): Referencian la factura que se está anulando o devolviendo
- **Notas de Débito** (iTiDE=6): Referencian la factura a la que se le agregan cargos
- **Autofacturas** (iTiDE=4): Referencian el documento de compra

## Tipos de Documento Asociado

### 1. Documento Electrónico (iTipDocAso=1)

Cuando la factura original fue enviada electrónicamente a SIFEN:

```python
from sifen.models import DocumentoAsociado
from sifen.models.documento_asociado import (
    TIPO_DOC_ASOCIADO_ELECTRONICO,
    DESCRIPCIONES_TIPO_DOC_ASOCIADO,
)

# Ejemplo: Nota de crédito para una factura electrónica
doc_asociado = DocumentoAsociado(
    iTipDocAso=TIPO_DOC_ASOCIADO_ELECTRONICO,
    dDesTipDocAso=DESCRIPCIONES_TIPO_DOC_ASOCIADO[TIPO_DOC_ASOCIADO_ELECTRONICO],
    dCdCDERef="01800159272001001000000342026041612345678901234567890123",  # CDC de 44 caracteres
)
```

**¿Cómo obtener el CDC?**
- El CDC se obtiene cuando envías una factura exitosamente
- Está en `respuesta.cdc` después de `client.enviar_documento()`
- También puedes consultarlo con `client.consultar_documento(cdc)`

### 2. Documento Impreso (iTipDocAso=2)

Cuando la factura original fue emitida en papel (timbrado físico):

```python
from sifen.models.documento_asociado import (
    TIPO_DOC_ASOCIADO_IMPRESO,
    TIPO_DOC_IMPRESO_FACTURA,
    DESCRIPCIONES_TIPO_DOC_ASOCIADO,
    DESCRIPCIONES_TIPO_DOC_IMPRESO,
)

doc_asociado = DocumentoAsociado(
    iTipDocAso=TIPO_DOC_ASOCIADO_IMPRESO,
    dDesTipDocAso=DESCRIPCIONES_TIPO_DOC_ASOCIADO[TIPO_DOC_ASOCIADO_IMPRESO],
    # Datos del timbrado impreso
    dNTimDI="80159272",           # Número de timbrado
    dEstDocAso="001",              # Establecimiento (3 dígitos)
    dPExpDocAso="001",             # Punto de expedición (3 dígitos)
    dNumDocAso="0000025",          # Número del documento (7 dígitos)
    # Tipo de documento impreso
    iTipoDocAso=TIPO_DOC_IMPRESO_FACTURA,  # 1=Factura, 2=NC, 3=ND, 4=Remisión, 5=Retención
    dDTipoDocAso=DESCRIPCIONES_TIPO_DOC_IMPRESO[TIPO_DOC_IMPRESO_FACTURA],
)
```

### 3. Constancia Electrónica (iTipDocAso=3)

Para autofacturas basadas en constancias:

```python
from sifen.models.documento_asociado import (
    TIPO_DOC_ASOCIADO_CONSTANCIA,
    TIPO_CONSTANCIA_NO_CONTRIBUYENTE,
    DESCRIPCIONES_TIPO_DOC_ASOCIADO,
    DESCRIPCIONES_TIPO_CONSTANCIA,
)

doc_asociado = DocumentoAsociado(
    iTipDocAso=TIPO_DOC_ASOCIADO_CONSTANCIA,
    dDesTipDocAso=DESCRIPCIONES_TIPO_DOC_ASOCIADO[TIPO_DOC_ASOCIADO_CONSTANCIA],
    iTipCons=TIPO_CONSTANCIA_NO_CONTRIBUYENTE,  # 1=No contribuyente, 2=Microproductores
    dDesTipCons=DESCRIPCIONES_TIPO_CONSTANCIA[TIPO_CONSTANCIA_NO_CONTRIBUYENTE],
)
```

## Ejemplo Completo: Nota de Crédito

```python
from sifen.client import SifenClient
from sifen.config import SifenConfig, TipoAmbiente
from sifen.models import (
    DocumentoElectronico,
    NotaCreditoDebito,
    DocumentoAsociado,
)
from sifen.models.nota_credito_debito import MOTIVO_DEVOLUCION, DESCRIPCIONES_MOTIVOS
from sifen.models.documento_asociado import (
    TIPO_DOC_ASOCIADO_ELECTRONICO,
    DESCRIPCIONES_TIPO_DOC_ASOCIADO,
)

# 1. Primero, enviar una factura y guardar su CDC
config = SifenConfig(ambiente=TipoAmbiente.DEV, ...)
client = SifenClient(config)

factura = DocumentoElectronico(...)  # Crear factura normal
respuesta_factura = client.enviar_documento(factura)

if respuesta_factura.aprobado:
    cdc_factura = respuesta_factura.cdc  # Guardar este CDC
    print(f"Factura aprobada, CDC: {cdc_factura}")

# 2. Luego, crear una nota de crédito que referencia esa factura
nota_credito = NotaCreditoDebito(
    iMotEmi=MOTIVO_DEVOLUCION,
    dDesMotEmi=DESCRIPCIONES_MOTIVOS[MOTIVO_DEVOLUCION],
)

# Referenciar la factura original usando su CDC
doc_asociado = DocumentoAsociado(
    iTipDocAso=TIPO_DOC_ASOCIADO_ELECTRONICO,
    dDesTipDocAso=DESCRIPCIONES_TIPO_DOC_ASOCIADO[TIPO_DOC_ASOCIADO_ELECTRONICO],
    dCdCDERef=cdc_factura,  # Usar el CDC de la factura enviada anteriormente
)

# Crear la nota de crédito
nc = DocumentoElectronico(
    dVerFor=150,
    gTimb=IdentificacionDE(iTiDE=5, ...),  # 5 = Nota de Crédito
    gCamNCDE=nota_credito,
    gCamDEAsoc=doc_asociado,  # ← IMPORTANTE: Referencia al documento original
    # ... resto de campos
)

# Enviar la nota de crédito
respuesta_nc = client.enviar_documento(nc)
```

## Flujo de Trabajo Recomendado

1. **Enviar Factura Original**
   ```python
   respuesta = client.enviar_documento(factura)
   cdc = respuesta.cdc  # Guardar en base de datos
   ```

2. **Cuando necesites hacer una NC/ND**
   - Recuperar el CDC de la factura original de tu base de datos
   - Crear el `DocumentoAsociado` con ese CDC
   - Crear la NC/ND con el documento asociado

3. **Validación**
   - SIFEN validará que el CDC existe y corresponde a un documento válido
   - Si el CDC no existe o es inválido, rechazará la NC/ND

## Errores Comunes

### Error: "Documento asociado es obligatorio"
**Causa**: No incluiste `gCamDEAsoc` en una NC/ND/Autofactura  
**Solución**: Agregar el campo `gCamDEAsoc` al documento

### Error: "CDC del documento referenciado no existe"
**Causa**: El CDC no corresponde a un documento enviado previamente  
**Solución**: Verificar que el CDC sea correcto y que la factura original haya sido aprobada

### Error: "CDC debe tener 44 caracteres"
**Causa**: El CDC está incompleto o mal formado  
**Solución**: El CDC siempre tiene exactamente 44 caracteres

## Constantes Disponibles

```python
# Tipos de documento asociado
TIPO_DOC_ASOCIADO_ELECTRONICO = 1
TIPO_DOC_ASOCIADO_IMPRESO = 2
TIPO_DOC_ASOCIADO_CONSTANCIA = 3

# Tipos de documento impreso
TIPO_DOC_IMPRESO_FACTURA = 1
TIPO_DOC_IMPRESO_NOTA_CREDITO = 2
TIPO_DOC_IMPRESO_NOTA_DEBITO = 3
TIPO_DOC_IMPRESO_NOTA_REMISION = 4
TIPO_DOC_IMPRESO_COMPROBANTE_RETENCION = 5

# Tipos de constancia
TIPO_CONSTANCIA_NO_CONTRIBUYENTE = 1
TIPO_CONSTANCIA_MICROPRODUCTORES = 2
```
