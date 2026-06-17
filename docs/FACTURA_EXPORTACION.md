# Factura de Exportación

Guía completa para implementar Facturas de Exportación usando django-sifen.

## ⚠️ Importante

La **Factura de Exportación** NO es un tipo de documento separado en SIFEN. Se implementa como:

- **Tipo de documento**: `iTiDE=1` (Factura Electrónica normal)
- **Campo especial**: `dInfoFisc` (B006) con información de exportación
- **Base legal**: Art. 20 numeral 15 del Decreto Nº 10797/2013

## 📋 Formato del campo dInfoFisc

Según el manual técnico de SIFEN, el campo `dInfoFisc` debe contener los siguientes datos **separados por coma (,) y espacio**:

```
a) Tipo de Operación: valor,
b) Condición de Negociación: valor (CIF, FOB, otros),
c) País de Destino: valor,
d) Empresa Fletera o Exportador Nacional: valor,
e) Agente de Transporte: valor,
f) Instrucciones de Pago para el cliente: valor (Beneficiario, Banco, Nº de cuenta, Código SWIFT, Cartas de Crédito, otro),
g) Número/s de Conocimiento/s de Embarque: valor,
h) Número/s de Manifiesto/s Internacional/es de Carga: valor,
i) Número de barcaza o remolcador: descripción y cantidad del bien transportado,
j) Las demás informaciones que sean fijadas por la Administración Tributaria
```

## 🚀 Uso Básico

### 1. Instalación

```bash
pip install django-sifen
```

### 2. Ejemplo Mínimo

```python
from datetime import datetime, date
from decimal import Decimal
from sifen.client import SifenClient
from sifen.config import SifenConfig, TipoAmbiente
from sifen.models import (
    DocumentoElectronico,
    IdentificacionDE,
    DatosGeneralesDE,
    Emisor,
    Receptor,
    Item,
)
from sifen.utils import calcular_valor_item, calcular_totales
from sifen.models.totales import CondicionOperacion, Pago

# 1. Preparar información de exportación
info_exportacion = (
    "a) Tipo de Operación: Exportación Definitiva, "
    "b) Condición de Negociación: FOB, "
    "c) País de Destino: Brasil, "
    "d) Empresa Fletera o Exportador Nacional: NAVIERA SA, "
    "e) Agente de Transporte: LOGISTICA SRL, "
    "f) Instrucciones de Pago: Beneficiario: MI EMPRESA SA, "
    "Banco: BANCO ITAU, Nº de cuenta: 1234567890, Código SWIFT: ITAUPYPA, "
    "g) Conocimiento de Embarque: BL-2026-001234, "
    "h) Manifiesto Internacional: MIC-2026-005678, "
    "i) Barcaza: N/A, "
    "j) Conforme Decreto 10797/2013"
)

# 2. Crear documento (iTiDE=1, NO iTiDE=2)
documento = DocumentoElectronico(
    dVerFor=150,
    gTimb=IdentificacionDE(
        iTiDE=1,  # ← Factura Electrónica (NO usar iTiDE=2)
        dNumTim=12345678,
        dEst="001",
        dPunExp="001",
        dNumDoc="0000001",
        dFeIniT=date.today(),
    ),
    gDatGralOpe=DatosGeneralesDE(
        dFeEmiDE=datetime.now(),
        iTipEmi=1,
        dCodSeg="123456789",
        dInfoFisc=info_exportacion,  # ← AQUÍ va la info de exportación
        iTipTra=1,
        iTImp=1,
        cMoneOpe="USD",  # Moneda de exportación
    ),
    gEmis=Emisor(
        dRucEm="80012345-6",
        dDVEmi=6,
        iTipCont=1,
        dNomEmi="MI EMPRESA EXPORTADORA SA",
        # ... resto de campos del emisor
    ),
    gDatRec=Receptor(
        iNatRec=2,  # No residente
        iTiOpe=2,   # B2B con no residente
        cPaisRec="BRA",  # País destino
        dNomRec="EMPRESA IMPORTADORA LTDA",
        # ... resto de campos del receptor
    ),
    gCamItem=[
        Item(
            dCodInt="PROD-001",
            dDesProSer="Producto para exportación",
            cUniMed=77,
            dCantProSer=Decimal("100"),
            cPaisOrig="PRY",
            gValorItem=calcular_valor_item(
                precio_unitario=Decimal("50"),
                cantidad=Decimal("100"),
                tasa_iva=0,  # Exonerado
                afectacion_iva=3,  # 3 = Exonerado
            ),
        )
    ],
    gTotSub=calcular_totales([item]),
    gPaConEIni=CondicionOperacion(
        iCondOpe=1,
        gPaConEIni=[Pago(iTiPago=4, dMonTiPag=Decimal("5000"))]
    ),
)

# 3. Configurar cliente
config = SifenConfig(
    ambiente=TipoAmbiente.DEV,
    certificado_archivo="/path/to/cert.pfx",
    certificado_contrasena="password",
    csc="ABCD0000000000000000000000000000",
    csc_id="0001",
)

client = SifenClient(config)

# 4. Enviar (sincrónico - respuesta inmediata)
respuesta = client.enviar_documento(documento)

if respuesta.aprobado:
    print(f"✓ Aprobado! Protocolo: {respuesta.numero_protocolo}")
else:
    print(f"✗ Rechazado: {respuesta.mensaje}")
```

## 📝 Campos Importantes

### Identificación del Documento

```python
IdentificacionDE(
    iTiDE=1,  # ← IMPORTANTE: usar 1, NO 2
    dDesTiDE="Factura Electrónica",
    # ... resto de campos
)
```

### Datos Generales

```python
DatosGeneralesDE(
    dFeEmiDE=datetime.now(),
    dInfoFisc=info_exportacion,  # ← Campo clave para exportación
    cMoneOpe="USD",  # Moneda extranjera
    # ... resto de campos
)
```

### Receptor (Importador Extranjero)

```python
Receptor(
    iNatRec=2,  # 2 = No residente
    iTiOpe=2,   # 2 = B2B con no residente
    cPaisRec="BRA",  # Código del país (ISO 3166-1 alpha-3)
    dNomRec="EMPRESA IMPORTADORA LTDA",
    dNumIDRec="12.345.678/0001-90",  # Documento extranjero
)
```

### Items (Productos Exportados)

```python
Item(
    dCodInt="PROD-001",
    dDesProSer="Producto para exportación",
    cPaisOrig="PRY",  # País de origen
    gValorItem=calcular_valor_item(
        precio_unitario=Decimal("50"),
        cantidad=Decimal("100"),
        tasa_iva=0,  # Exonerado de IVA
        afectacion_iva=3,  # 3 = Exonerado
    ),
)
```

### Totales

```python
totales = calcular_totales([item])
totales.cMoneOpe = "USD"
totales.dTiCam = Decimal("7000")  # Tipo de cambio Gs/USD
```

## 🔧 Función Helper (Opcional)

Puedes crear una función helper para generar el campo `dInfoFisc`:

```python
def generar_info_exportacion(
    tipo_operacion: str,
    condicion_negociacion: str,
    pais_destino: str,
    empresa_fletera: str,
    agente_transporte: str,
    beneficiario: str,
    banco: str,
    numero_cuenta: str,
    codigo_swift: str,
    conocimiento_embarque: str = "",
    manifiesto_carga: str = "",
    **kwargs
) -> str:
    """Genera el campo dInfoFisc para Factura de Exportación."""
    return (
        f"a) Tipo de Operación: {tipo_operacion}, "
        f"b) Condición de Negociación: {condicion_negociacion}, "
        f"c) País de Destino: {pais_destino}, "
        f"d) Empresa Fletera o Exportador Nacional: {empresa_fletera}, "
        f"e) Agente de Transporte: {agente_transporte}, "
        f"f) Instrucciones de Pago para el cliente: "
        f"Beneficiario: {beneficiario}, Banco: {banco}, "
        f"Nº de cuenta: {numero_cuenta}, Código SWIFT: {codigo_swift}, "
        f"g) Número/s de Conocimiento/s de Embarque: {conocimiento_embarque}, "
        f"h) Número/s de Manifiesto/s Internacional/es de Carga: {manifiesto_carga}, "
        f"i) Número de barcaza o remolcador: N/A, "
        f"j) Conforme Decreto 10797/2013"
    )

# Uso:
info_exp = generar_info_exportacion(
    tipo_operacion="Exportación Definitiva",
    condicion_negociacion="FOB",
    pais_destino="Brasil",
    empresa_fletera="NAVIERA SA",
    agente_transporte="LOGISTICA SRL",
    beneficiario="MI EMPRESA SA",
    banco="BANCO ITAU",
    numero_cuenta="1234567890",
    codigo_swift="ITAUPYPA",
    conocimiento_embarque="BL-2026-001234",
    manifiesto_carga="MIC-2026-005678",
)
```

## ✅ Checklist de Implementación

- [ ] Usar `iTiDE=1` (Factura Electrónica)
- [ ] Completar campo `dInfoFisc` con información de exportación
- [ ] Usar moneda extranjera (USD, EUR, etc.) en `cMoneOpe`
- [ ] Configurar receptor como no residente (`iNatRec=2`)
- [ ] Configurar operación B2B con no residente (`iTiOpe=2`)
- [ ] Especificar país de destino en `cPaisRec`
- [ ] Marcar items como exonerados de IVA (`afectacion_iva=3`)
- [ ] Incluir tipo de cambio en totales (`dTiCam`)
- [ ] Especificar país de origen en items (`cPaisOrig`)

## 🔍 Validaciones de SIFEN

SIFEN validará:

1. **RUC habilitado**: El RUC del emisor debe estar habilitado para exportación
2. **Formato del campo dInfoFisc**: Debe seguir el formato especificado
3. **Moneda**: Debe ser una moneda válida (USD, EUR, etc.)
4. **País destino**: Código ISO válido
5. **IVA**: Items deben estar exonerados (afectación 3)

## 📚 Referencias

- **Manual Técnico SIFEN v150**: Campo B006 (dInfoFisc)
- **Decreto Nº 10797/2013**: Art. 20 numeral 15
- **Ejemplos**: Ver `examples/ejemplo_factura_exportacion.py`

## ❓ Preguntas Frecuentes

### ¿Por qué usar iTiDE=1 y no iTiDE=2?

El tipo de documento iTiDE=2 (Factura de Exportación) está definido en el schema XSD pero **comentado/inactivo**. SIFEN decidió usar el enfoque de campo de texto (`dInfoFisc`) en lugar de campos XML estructurados.

### ¿Qué monedas puedo usar?

Las monedas más comunes para exportación son:
- `USD`: Dólar Americano
- `EUR`: Euro
- `BRL`: Real Brasileño
- `ARS`: Peso Argentino

### ¿Cómo manejo el tipo de cambio?

```python
totales.dTiCam = Decimal("7000")  # 1 USD = 7000 Gs
```

El tipo de cambio debe ser el vigente al momento de la emisión.

### ¿Los items deben estar exonerados de IVA?

Sí, las exportaciones están exoneradas de IVA según la legislación paraguaya:

```python
gValorItem=calcular_valor_item(
    precio_unitario=Decimal("50"),
    cantidad=Decimal("100"),
    tasa_iva=0,
    afectacion_iva=3,  # 3 = Exonerado
)
```

## 🆘 Soporte

Para más información:
- Ver ejemplos en `examples/`
- Consultar documentación de SIFEN: https://ekuatia.set.gov.py
- Issues: https://github.com/tu-repo/django-sifen/issues
