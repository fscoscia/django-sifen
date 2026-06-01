# Autofacturas Electrónicas - Guía Completa

## ¿Qué es una Autofactura?

Una **Autofactura Electrónica (AFE)** es un documento que el **comprador** emite para registrar compras a proveedores que **no emiten factura**. Es común en transacciones con:

- **Productores agrícolas** que no son contribuyentes
- **Microproductores** sin RUC
- **No contribuyentes** en general
- **Proveedores extranjeros** sin representación fiscal

### Diferencia clave

| Factura Normal | Autofactura |
|----------------|-------------|
| El **vendedor** emite la factura | El **comprador** emite la autofactura |
| Vendedor = Emisor | Comprador = Emisor |
| Comprador = Receptor | **Comprador = Receptor** (mismo RUC) |

## Características Especiales

### 1. RUC del Receptor = RUC del Emisor

**IMPORTANTE**: En autofacturas, el RUC del receptor **debe ser el mismo** que el RUC del emisor.

```python
gEmis=Emisor(
    dRucEm="80159272-0",  # RUC del comprador
    # ...
),
gDatRec=Receptor(
    dRucRec="80159272",   # ¡Mismo RUC! (sin guión ni DV)
    dDVRec="0",
    iTiContRec=2,         # Contribuyente (el comprador)
    # ...
),
```

### 2. Datos del Vendedor en gCamAE

Los datos del vendedor real (no contribuyente) van en el grupo **gCamAE** (Campos de Autofactura Electrónica):

```python
from sifen.models import Autofactura
from sifen.models.autofactura import (
    NATURALEZA_NO_CONTRIBUYENTE,
    TIPO_DOC_CEDULA_PARAGUAYA,
    DESCRIPCIONES_NATURALEZA,
    DESCRIPCIONES_TIPO_DOC,
)

autofactura = Autofactura(
    # Naturaleza del vendedor
    iNatVen=NATURALEZA_NO_CONTRIBUYENTE,  # 1=No contribuyente, 2=Extranjero
    dDesNatVen=DESCRIPCIONES_NATURALEZA[NATURALEZA_NO_CONTRIBUYENTE],
    
    # Documento de identidad del vendedor
    iTipIDVen=TIPO_DOC_CEDULA_PARAGUAYA,
    dDTipIDVen=DESCRIPCIONES_TIPO_DOC[TIPO_DOC_CEDULA_PARAGUAYA],
    dNumIDVen="1234567",  # Cédula del vendedor
    
    # Datos del vendedor
    dNomVen="Juan Pérez Productor",
    dDirVen="Ruta 9 Km 45, Colonia Agrícola",
    
    # Ubicación del vendedor (opcional)
    cDepVen=16,
    dDesDepVen="BOQUERON",
    cDisVen=259,
    dDesDisVen="FILADELFIA",
    
    # Lugar donde se realizó la transacción
    dDirProv="Ruta 9 Km 45, Colonia Agrícola",
    cDepProv=16,
    dDesDepProv="BOQUERON",
)
```

### 3. Documento Asociado Obligatorio

Las autofacturas **requieren** un documento asociado, típicamente una **constancia electrónica**:

```python
from sifen.models import DocumentoAsociado
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
    # dNumCons y dNumControl son opcionales
)
```

## Constantes Disponibles

### Naturaleza del Vendedor

```python
from sifen.models.autofactura import (
    NATURALEZA_NO_CONTRIBUYENTE,  # 1
    NATURALEZA_EXTRANJERO,         # 2
    DESCRIPCIONES_NATURALEZA,
)
```

### Tipo de Documento de Identidad

```python
from sifen.models.autofactura import (
    TIPO_DOC_CEDULA_PARAGUAYA,     # 1
    TIPO_DOC_PASAPORTE,            # 2
    TIPO_DOC_CEDULA_EXTRANJERA,    # 3
    TIPO_DOC_CARNET_RESIDENCIA,    # 4
    TIPO_DOC_INNOMINADO,           # 5
    TIPO_DOC_TARJETA_DIPLOMATICA,  # 6
    TIPO_DOC_OTRO,                 # 9
    DESCRIPCIONES_TIPO_DOC,
)
```

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
    ActividadEconomica,
    Receptor,
    Item,
    Autofactura,
    DocumentoAsociado,
)
from sifen.utils import calcular_valor_item, calcular_totales
from sifen.models.totales import CondicionOperacion, Pago
from sifen.models.autofactura import (
    NATURALEZA_NO_CONTRIBUYENTE,
    TIPO_DOC_CEDULA_PARAGUAYA,
    DESCRIPCIONES_NATURALEZA,
    DESCRIPCIONES_TIPO_DOC,
)
from sifen.models.documento_asociado import (
    TIPO_DOC_ASOCIADO_CONSTANCIA,
    TIPO_CONSTANCIA_NO_CONTRIBUYENTE,
    DESCRIPCIONES_TIPO_DOC_ASOCIADO,
    DESCRIPCIONES_TIPO_CONSTANCIA,
)
from sifen.constants import TIPO_AUTOFACTURA_ELECTRONICA
import random

# Configurar cliente
config = SifenConfig(
    ambiente=TipoAmbiente.DEV,
    certificado_archivo="certificado.pfx",
    certificado_contrasena="password",
    csc="ABCD0000000000000000000000000000",
    csc_id="0001",
)
client = SifenClient(config)

# Crear item
item = Item(
    dCodInt="PROD001",
    dDesProSer="COMPRA DE PRODUCTOS AGRÍCOLAS",
    cUniMed=77,
    dCantProSer=Decimal("100"),
    gValorItem=calcular_valor_item(
        precio_unitario=Decimal("5000"),
        cantidad=Decimal("100"),
        tasa_iva=10,
    ),
)

totales = calcular_totales([item])

# Crear grupo de Autofactura con datos del vendedor
autofactura = Autofactura(
    iNatVen=NATURALEZA_NO_CONTRIBUYENTE,
    dDesNatVen=DESCRIPCIONES_NATURALEZA[NATURALEZA_NO_CONTRIBUYENTE],
    iTipIDVen=TIPO_DOC_CEDULA_PARAGUAYA,
    dDTipIDVen=DESCRIPCIONES_TIPO_DOC[TIPO_DOC_CEDULA_PARAGUAYA],
    dNumIDVen="1234567",
    dNomVen="Juan Pérez Productor",
    dDirVen="Ruta 9 Km 45, Colonia Agrícola",
    dDirProv="Ruta 9 Km 45, Colonia Agrícola",
)

# Crear documento asociado
doc_asociado = DocumentoAsociado(
    iTipDocAso=TIPO_DOC_ASOCIADO_CONSTANCIA,
    dDesTipDocAso=DESCRIPCIONES_TIPO_DOC_ASOCIADO[TIPO_DOC_ASOCIADO_CONSTANCIA],
    iTipCons=TIPO_CONSTANCIA_NO_CONTRIBUYENTE,
    dDesTipCons=DESCRIPCIONES_TIPO_CONSTANCIA[TIPO_CONSTANCIA_NO_CONTRIBUYENTE],
)

# Crear la autofactura
afe = DocumentoElectronico(
    dVerFor=150,
    gTimb=IdentificacionDE(
        iTiDE=TIPO_AUTOFACTURA_ELECTRONICA,  # 4
        dDesTiDE="Autofactura electrónica",
        dNumTim=12345678,
        dEst="001",
        dPunExp="001",
        dNumDoc="0000001",
        dFeIniT=datetime.strptime("2024-01-01", "%Y-%m-%d").date(),
    ),
    gDatGralOpe=DatosGeneralesDE(
        dFeEmiDE=datetime.now(),
        iTipEmi=1,
        dDesTipEmi="Normal",
        dCodSeg=str(random.randint(100000000, 999999999)),
        iTipTra=1,  # Requerido para autofacturas
        dDesTipTra="Venta de mercadería",
        iTImp=1,
        dDesTImp="IVA",
        cMoneOpe="PYG",
        dDesMoneOpe="guarani",
    ),
    gEmis=Emisor(
        # El emisor es quien COMPRA (el que emite la autofactura)
        dRucEm="80000000-0",
        dDVEmi=0,
        iTipCont=2,
        cTipReg=8,
        dNomEmi="MI EMPRESA S.A.",
        dDirEmi="Av. Principal 123",
        dTelEmi="021123456",
        dEmailE="contacto@miempresa.com.py",
        gActEco=[
            ActividadEconomica(
                cActEco="47111",
                dDesActEco="Venta al por menor en comercios no especializados",
            )
        ],
    ),
    gDatRec=Receptor(
        # IMPORTANTE: Mismo RUC que el emisor
        iNatRec=1,
        iTiOpe=2,  # 2 = Compra
        iTiContRec=2,  # Contribuyente (el comprador)
        dRucRec="80000000",  # Mismo RUC (sin guión ni DV)
        dDVRec="0",
        dNomRec="MI EMPRESA S.A.",
    ),
    gCamItem=[item],
    gTotSub=totales,
    gCamAE=autofactura,  # ← Datos del vendedor
    gCamDEAsoc=doc_asociado,  # ← Constancia
    gPaConEIni=CondicionOperacion(
        iCondOpe=1,
        dDesCondOpe="Contado",
        gPaConEIni=[
            Pago(
                iTiPago=1,
                dDesTiPag="Efectivo",
                dMonTiPag=totales.dTotGralOpe,
            )
        ],
    ),
)

# Enviar autofactura
respuesta = client.enviar_documento(afe)

if respuesta.aprobado:
    print(f"✓ Autofactura aprobada!")
    print(f"  CDC: {respuesta.cdc}")
else:
    print(f"✗ Autofactura rechazada: {respuesta.mensaje}")
```

## Casos de Uso Comunes

### 1. Compra a Productor Agrícola

```python
autofactura = Autofactura(
    iNatVen=NATURALEZA_NO_CONTRIBUYENTE,
    dDesNatVen="No contribuyente",
    iTipIDVen=TIPO_DOC_CEDULA_PARAGUAYA,
    dDTipIDVen="Cédula paraguaya",
    dNumIDVen="1234567",
    dNomVen="Pedro González",
    dDirVen="Compañía San José, Distrito de Caaguazú",
    dDirProv="Compañía San José, Distrito de Caaguazú",
)
```

### 2. Compra a Proveedor Extranjero

```python
autofactura = Autofactura(
    iNatVen=NATURALEZA_EXTRANJERO,
    dDesNatVen="Extranjero",
    iTipIDVen=TIPO_DOC_PASAPORTE,
    dDTipIDVen="Pasaporte",
    dNumIDVen="AB123456",
    dNomVen="John Smith",
    dDirVen="123 Main Street, Buenos Aires, Argentina",
    dDirProv="Asunción, Paraguay",  # Donde se realizó la transacción
)
```

### 3. Compra a Microproductor

```python
# Documento asociado para microproductores
doc_asociado = DocumentoAsociado(
    iTipDocAso=TIPO_DOC_ASOCIADO_CONSTANCIA,
    dDesTipDocAso="Constancia Electrónica",
    iTipCons=TIPO_CONSTANCIA_MICROPRODUCTORES,  # 2
    dDesTipCons="Constancia de microproductores",
)
```

## Validaciones Importantes

### ✓ Campos Obligatorios

- `iTiDE = 4` (Autofactura)
- `gCamAE` (Grupo de autofactura con datos del vendedor)
- `gCamDEAsoc` (Documento asociado - constancia)
- `iTipTra` (Tipo de transacción - requerido para autofacturas)
- RUC del receptor = RUC del emisor

### ✗ Errores Comunes

1. **RUC del receptor diferente al emisor**
   - Error: "El RUC del Receptor debe ser el mismo que el RUC del Emisor"
   - Solución: Usar el mismo RUC en ambos

2. **Falta el grupo gCamAE**
   - Error: "Campos de autofactura obligatorios"
   - Solución: Incluir el objeto `Autofactura` en `gCamAE`

3. **Falta documento asociado**
   - Error: "Documento asociado obligatorio"
   - Solución: Incluir `DocumentoAsociado` en `gCamDEAsoc`

4. **Vendedor es contribuyente**
   - Error: "El vendedor no debe ser contribuyente"
   - Solución: Verificar que `iTiContRec` sea correcto

## Referencias

- **Manual Técnico SIFEN v150** - Sección E4 (Campos de Autofactura)
- **Manual Técnico SIFEN v150** - Sección H (Documento Asociado)
- Ver también: [Documento Asociado](DOCUMENTO_ASOCIADO.md)
- Ver también: [Tipos de Documentos](TIPOS_DOCUMENTOS.md)

## Ejemplo Completo Ejecutable

Consulta el archivo `examples/flujo_completo_autofactura.py` para un ejemplo completo y funcional.
