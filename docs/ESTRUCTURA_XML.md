# Estructura XML de Documentos Electrónicos SIFEN

Este documento describe la estructura completa del XML generado para documentos electrónicos según el formato SIFEN v150.

## 📋 Tabla de Contenidos

- [Estructura General](#estructura-general)
- [Grupos Principales](#grupos-principales)
- [Dónde Modificar](#dónde-modificar)
- [Ejemplos de Cambios](#ejemplos-de-cambios)

---

## 🏗️ Estructura General

```xml
<rDE xmlns="http://ekuatia.set.gov.py/sifen/xsd">
    <DE Id="{CDC}">
        <dVerFor>150</dVerFor>
        
        <!-- A. IDENTIFICACIÓN -->
        <gTimb>...</gTimb>
        
        <!-- B. DATOS GENERALES -->
        <gDatGralOpe>...</gDatGralOpe>
        
        <!-- E. ÍTEMS -->
        <gDtipDE>...</gDtipDE>
        
        <!-- F. TOTALES -->
        <gTotSub>...</gTotSub>
        
        <!-- E600. CONDICIÓN -->
        <gCamCond>...</gCamCond>
    </DE>
</rDE>
```

---

## 📦 Grupos Principales

### A. Identificación del DE (gTimb)

**Ubicación en código:** `sifen/xml/generator.py` → `_generate_identificacion()`

**Estructura:**
```xml
<gTimb>
    <iTiDE>1</iTiDE>                          <!-- Tipo de documento -->
    <dDesTiDE>Factura electrónica</dDesTiDE>  <!-- Descripción -->
    <dNumTim>12345678</dNumTim>               <!-- Número de timbrado -->
    <dEst>001</dEst>                          <!-- Establecimiento -->
    <dPunExp>001</dPunExp>                    <!-- Punto de expedición -->
    <dNumDoc>0000001</dNumDoc>                <!-- Número de documento -->
    <dSerieNum>A001</dSerieNum>               <!-- Serie (opcional) -->
    <dFeIniT>2024-01-01T00:00:00</dFeIniT>    <!-- Fecha inicio timbrado -->
</gTimb>
```

**Campos:**
- `iTiDE`: Tipo de documento (1=Factura, 4=Autofactura, 5=Nota crédito, etc.)
- `dNumTim`: Número de timbrado otorgado por la SET
- `dEst`: Establecimiento (3 dígitos)
- `dPunExp`: Punto de expedición (3 dígitos)
- `dNumDoc`: Número correlativo del documento (7 dígitos)

---

### B. Datos Generales (gDatGralOpe)

**Ubicación en código:** `sifen/xml/generator.py` → `_generate_datos_generales()`

**Estructura:**
```xml
<gDatGralOpe>
    <dFeEmiDE>2024-05-04</dFeEmiDE>
    
    <!-- B1. Operación Comercial -->
    <gOpeCom>
        <iTipTra>1</iTipTra>                  <!-- Tipo de transacción -->
        <iTImp>1</iTImp>                      <!-- Tipo de impuesto -->
        <cMoneOpe>PYG</cMoneOpe>              <!-- Moneda -->
        <dCondTiCam>1</dCondTiCam>            <!-- Condición tipo cambio -->
        <dTiCam>1.00</dTiCam>                 <!-- Tipo de cambio -->
    </gOpeCom>
    
    <!-- D. Emisor -->
    <gEmis>
        <dRucEm>80012345-6</dRucEm>
        <dNomEmi>Empresa SA</dNomEmi>
        <dDirEmi>Av. Principal 123</dDirEmi>
        <cDepEmi>1</cDepEmi>
        <cDisEmi>1</cDisEmi>
        <cCiuEmi>1</cCiuEmi>
        <dTelEmi>021-123456</dTelEmi>
        <dEmailE>contacto@empresa.com.py</dEmailE>
        
        <!-- Actividades Económicas (repetible) -->
        <gActEco>
            <cActEco>47111</cActEco>
            <dDesActEco>Venta al por menor</dDesActEco>
        </gActEco>
    </gEmis>
    
    <!-- E. Receptor -->
    <gDatRec>
        <iNatRec>1</iNatRec>                  <!-- Naturaleza receptor -->
        <iTiOpe>1</iTiOpe>                    <!-- Tipo de operación -->
        <dNomRec>Cliente SRL</dNomRec>
        <dRucRec>80098765-4</dRucRec>
        <dDirRec>Calle Secundaria 456</dDirRec>
        <dTelRec>021-654321</dTelRec>
        <dEmailRec>cliente@empresa.com.py</dEmailRec>
    </gDatRec>
</gDatGralOpe>
```

---

### E. Ítems del Documento (gDtipDE → gCamItem)

**Ubicación en código:** `sifen/xml/generator.py` → `_generate_item()`

**Estructura:**
```xml
<gDtipDE>
    <!-- Ítem 1 -->
    <gCamItem>
        <dNroItem>1</dNroItem>                <!-- Número de ítem -->
        <dCodInt>PROD001</dCodInt>            <!-- Código interno -->
        <dDesProSer>Producto de Prueba</dDesProSer>
        <cUniMed>77</cUniMed>                 <!-- Unidad de medida -->
        <dDesUniMed>Unidades</dDesUniMed>
        <dCantProSer>10.00</dCantProSer>      <!-- Cantidad -->
        <cPaisOrig>PRY</cPaisOrig>            <!-- País origen -->
        
        <!-- E720. Valor del Ítem -->
        <gValorItem>
            <dPUniProSer>100000</dPUniProSer>  <!-- Precio unitario -->
            <dTiCamIt>1.00</dTiCamIt>          <!-- Tipo cambio ítem -->
            <dTotBruOpeItem>1000000</dTotBruOpeItem>  <!-- Total bruto -->
            
            <!-- E730. IVA del Ítem -->
            <gCamIVA>
                <iAfecIVA>1</iAfecIVA>         <!-- Afectación IVA -->
                <dDesAfecIVA>Gravado IVA 10%</dDesAfecIVA>
                <dPropIVA>100</dPropIVA>       <!-- Proporción IVA -->
                <dTasaIVA>10</dTasaIVA>        <!-- Tasa IVA -->
                <dBasGravIVA>909090.91</dBasGravIVA>  <!-- Base gravada -->
                <dLiqIVAItem>90909.09</dLiqIVAItem>   <!-- Liquidación IVA -->
                
                <!-- Solo si afectación = 4 y NT-13 habilitada -->
                <dBasExe>0</dBasExe>           <!-- Base exenta (NT-13) -->
            </gCamIVA>
        </gValorItem>
    </gCamItem>
    
    <!-- Ítem 2, 3, ... (repetible hasta 999) -->
</gDtipDE>
```

**Campos importantes:**
- `iAfecIVA`: Tipo de afectación IVA
  - 1 = Gravado IVA 10%
  - 2 = Gravado IVA 5%
  - 3 = Exento
  - 4 = Gravado Parcial
- `dBasExe`: Solo se incluye si `iAfecIVA = 4` y `habilitar_nota_tecnica_13 = True`

---

### F. Totales y Subtotales (gTotSub)

**Ubicación en código:** `sifen/xml/generator.py` → `_generate_totales()`

**Estructura:**
```xml
<gTotSub>
    <dSubExe>0</dSubExe>                      <!-- Subtotal exento -->
    <dSubExo>0</dSubExo>                      <!-- Subtotal exonerado -->
    <dSub5>0</dSub5>                          <!-- Subtotal IVA 5% -->
    <dSub10>1000000</dSub10>                  <!-- Subtotal IVA 10% -->
    <dTotOpe>1000000</dTotOpe>                <!-- Total operación -->
    <dTotDesc>0</dTotDesc>                    <!-- Total descuentos -->
    <dTotDescGlotem>0</dTotDescGlotem>        <!-- Desc. global ítem -->
    <dTotAntItem>0</dTotAntItem>              <!-- Anticipos ítem -->
    <dTotAnt>0</dTotAnt>                      <!-- Total anticipos -->
    <dPorcDescTotal>0</dPorcDescTotal>        <!-- % descuento total -->
    <dDescTotal>0</dDescTotal>                <!-- Descuento total -->
    <dAnticipo>0</dAnticipo>                  <!-- Anticipo -->
    <dRedon>0</dRedon>                        <!-- Redondeo -->
    <dComi>0</dComi>                          <!-- Comisión -->
    <dTotGralOpe>1000000</dTotGralOpe>        <!-- Total general -->
    <dIVA5>0</dIVA5>                          <!-- IVA 5% -->
    <dIVA10>90909</dIVA10>                    <!-- IVA 10% -->
    <dLiqTotIVA5>0</dLiqTotIVA5>              <!-- Liquidación IVA 5% -->
    <dLiqTotIVA10>90909</dLiqTotIVA10>        <!-- Liquidación IVA 10% -->
    <dTotIVA>90909</dTotIVA>                  <!-- Total IVA -->
    <dBaseGrav5>0</dBaseGrav5>                <!-- Base gravada 5% -->
    <dBaseGrav10>909091</dBaseGrav10>         <!-- Base gravada 10% -->
    <dTBasGraIVA>909091</dTBasGraIVA>         <!-- Total base gravada -->
</gTotSub>
```

---

### E600. Condición de Operación (gCamCond)

**Ubicación en código:** `sifen/xml/generator.py` → `_generate_condicion()`

**Estructura:**
```xml
<gCamCond>
    <iCondOpe>1</iCondOpe>                    <!-- 1=Contado, 2=Crédito -->
    <dDesCondOpe>Contado</dDesCondOpe>
    
    <!-- Si es CONTADO (iCondOpe = 1) -->
    <gPaConEIni>
        <iTiPago>1</iTiPago>                  <!-- Tipo de pago -->
        <dDesTiPag>Efectivo</dDesTiPag>
        <dMonTiPag>1000000</dMonTiPag>        <!-- Monto -->
        <cMoneTiPag>PYG</cMoneTiPag>          <!-- Moneda -->
        <dTiCamTiPag>1.00</dTiCamTiPag>       <!-- Tipo cambio -->
    </gPaConEIni>
    
    <!-- Si es CRÉDITO (iCondOpe = 2) -->
    <gPagCred>
        <iCondCred>1</iCondCred>              <!-- Condición crédito -->
        <dDesCondCred>Plazo</dDesCondCred>
        <dPlazoCre>30 días</dPlazoCre>        <!-- Plazo -->
        <dCuotas>3</dCuotas>                  <!-- Cantidad cuotas -->
        <dMonEnt>0</dMonEnt>                  <!-- Monto entrega inicial -->
        
        <!-- Cuotas (repetible) -->
        <gCuotas>
            <cMoneCuo>PYG</cMoneCuo>
            <dMonCuota>333333</dMonCuota>
            <dVencCuo>2024-06-04</dVencCuo>
        </gCuotas>
    </gPagCred>
</gCamCond>
```

---

## 🔧 Dónde Modificar Según el Cambio

### Si SIFEN agrega un nuevo campo:

| Ubicación del Campo | Archivo a Modificar |
|---------------------|---------------------|
| En `<gTimb>` | `sifen/models/timbrado.py` + `sifen/xml/generator.py::_generate_identificacion()` |
| En `<gEmis>` | `sifen/models/emisor.py` + `sifen/xml/generator.py::_generate_emisor()` |
| En `<gDatRec>` | `sifen/models/receptor.py` + `sifen/xml/generator.py::_generate_receptor()` |
| En `<gCamItem>` | `sifen/models/items.py` + `sifen/xml/generator.py::_generate_item()` |
| En `<gCamIVA>` | `sifen/models/items.py::IVAItem` + `sifen/xml/generator.py::_generate_item()` |
| En `<gTotSub>` | `sifen/models/totales.py` + `sifen/xml/generator.py::_generate_totales()` |
| En `<gCamCond>` | `sifen/models/condicion.py` + `sifen/xml/generator.py::_generate_condicion()` |

### Si SIFEN cambia la estructura:

1. **Cambio de orden de elementos:**
   - Modificar solo `sifen/xml/generator.py`
   - Reordenar las llamadas a `_add_element()` o `SubElement()`

2. **Nuevo grupo completo:**
   - Crear modelo en `sifen/models/`
   - Crear función `_generate_nuevo_grupo()` en `sifen/xml/generator.py`
   - Llamar desde `generate()`

3. **Cambio de namespace:**
   - Modificar `sifen/constants.py::NAMESPACE_SIFEN`

---

## 📝 Ejemplos de Cambios

### Ejemplo 1: SIFEN agrega campo "dObservacion" en gTimb

```python
# 1. Agregar al modelo
# sifen/models/timbrado.py
@dataclass
class Timbrado:
    # ... campos existentes
    dObservacion: Optional[str] = None  # ← NUEVO

# 2. Agregar al generador
# sifen/xml/generator.py
def _generate_identificacion(self, parent: etree.Element):
    """..."""
    # ... código existente
    
    # NUEVO: Agregar observación si existe
    if gTimb.dObservacion:
        self._add_element(timb_elem, "dObservacion", gTimb.dObservacion)
```

### Ejemplo 2: SIFEN cambia fórmula de IVA (Nota Técnica 14)

```python
# sifen/utils/calculators.py

# Mantener función vieja
def calcular_base_exenta_nt13(...):
    """Fórmula NT-13."""
    # Código existente
    pass

# Agregar nueva función
def calcular_base_exenta_nt14(...):  # ← NUEVO
    """
    Fórmula NT-14 (nueva).
    
    Nueva fórmula: [...]
    """
    # Nueva fórmula aquí
    pass

# Usar según configuración
# sifen/xml/generator.py
def _generate_item(self, ...):
    if config.habilitar_nota_tecnica_14:
        base_exenta = calcular_base_exenta_nt14(...)
    elif config.habilitar_nota_tecnica_13:
        base_exenta = calcular_base_exenta_nt13(...)
```

### Ejemplo 3: SIFEN lanza versión 160

```python
# sifen/constants.py
VERSION_SIFEN_150 = "150"
VERSION_SIFEN_160 = "160"  # ← NUEVO

# sifen/config.py
class SifenConfig:
    def __init__(
        self,
        ...,
        version_formato: int = 150,  # ← Permitir especificar
    ):
        self.version_formato = version_formato

# sifen/xml/generator.py
def generate(self):
    # Versión
    self._add_element(de_elem, "dVerFor", self.config.version_formato)
    
    # Campos específicos v160
    if self.config.version_formato >= 160:
        self._generate_campos_v160(de_elem)  # ← NUEVO
```

---

## 🎯 Mejores Prácticas

### 1. Mantener comentarios actualizados
```python
def _generate_item(self, ...):
    """
    Genera elemento gCamItem (E700-E799).
    
    Estructura:
    <gCamItem>
        <dNroItem>1</dNroItem>
        ...
    </gCamItem>
    
    Cambios:
    - v150: Versión inicial
    - v160: Agregado campo dNuevoCampo  # ← Documentar cambios
    """
```

### 2. Usar constantes para valores fijos
```python
# sifen/constants.py
TIPO_DOCUMENTO_FACTURA = 1
TIPO_DOCUMENTO_NOTA_CREDITO = 5
AFECTACION_IVA_10 = 1
AFECTACION_IVA_PARCIAL = 4
```

### 3. Validar antes de generar
```python
def _generate_item(self, ...):
    # Validar datos
    if not item.codigo:
        raise ValueError("Código de ítem es obligatorio")
    
    # Generar XML
    ...
```

### 4. Testing
```python
# tests/test_xml_generator.py
def test_generate_item_con_iva_10():
    """Verifica generación correcta de ítem con IVA 10%."""
    item = Item(...)
    xml = generator._generate_item(item)
    
    assert xml.find("dCodInt").text == "PROD001"
    assert xml.find(".//iAfecIVA").text == "1"
```

---

## 📚 Referencias

- [Documentación Técnica SIFEN](https://ekuatia.set.gov.py/portal/ekuatia)
- [Manual Técnico v150](https://ekuatia.set.gov.py/portal/ekuatia/detail?content-id=/repository/collaboration/sites/ekuatia/documents/documentacion/documentacion-tecnica/manual-tecnico-de-kuatia-version-150.pdf)
- [Nota Técnica 13](https://ekuatia.set.gov.py/portal/ekuatia/detail?content-id=/repository/collaboration/sites/ekuatia/documents/documentacion/documentacion-tecnica/NT_E_KUATIA_013_MT_V150.pdf)

---

**Última actualización:** Mayo 2024  
**Versión SIFEN:** 150
