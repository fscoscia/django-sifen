# Generación de KuDE (Representación Gráfica en PDF)

## 📋 ¿Qué es el KuDE?

El **KuDE** (Código Único de Documento Electrónico) es la **representación gráfica en formato PDF** de un documento electrónico. Es el documento que se imprime o envía digitalmente al cliente.

### Características del KuDE

- ✅ Formato PDF estándar (A4)
- ✅ Incluye código QR para consulta en SIFEN
- ✅ Contiene CDC (44 caracteres) para validación
- ✅ Diseño según Manual Técnico SIFEN v150, Capítulo 13
- ✅ Válido por mínimo 6 meses (durabilidad del papel)
- ✅ Puede incluir logo del emisor

### Propósitos del KuDE

1. **Documento tributario físico** para receptores no electrónicos o consumidores finales
2. **Ampara el traslado** de mercaderías entre locales
3. **Respalda créditos fiscales** del receptor no facturador electrónico

---

## 🚀 Instalación

El generador de KuDE requiere dependencias adicionales:

```bash
# Instalar ReportLab (generación de PDF)
pip install reportlab

# Instalar QRCode (generación de código QR)
pip install qrcode[pil]

# O instalar todo junto
pip install reportlab qrcode[pil]
```

---

## 💻 Uso Básico

### Generar KuDE después de enviar un documento

```python
from sifen import SifenClient
from sifen.config import SifenConfig, TipoAmbiente

# Configurar cliente
config = SifenConfig(
    ambiente=TipoAmbiente.DEV,
    certificado_archivo="/path/to/cert.p12",
    certificado_contrasena="password",
    csc="ABCD0000000000000000000000000000",
    csc_id="0001",
)

client = SifenClient(config)

# Enviar documento
respuesta = client.enviar_documento(documento)

if respuesta.aprobado:
    # Generar KuDE
    pdf_bytes = client.generar_kude(
        documento=documento,
        output_path="/path/to/factura.pdf",
        logo_path="/path/to/logo.png"  # Opcional
    )
    
    print(f"✓ KuDE generado: {len(pdf_bytes)} bytes")
```

### Generar KuDE sin guardar archivo

```python
# Solo obtener bytes del PDF
pdf_bytes = client.generar_kude(documento)

# Enviar por email, guardar en S3, etc.
enviar_por_email(pdf_bytes, cliente_email)
```

### Generar KuDE con logo personalizado

```python
# Con logo del emisor
pdf_bytes = client.generar_kude(
    documento=documento,
    output_path="/path/to/factura.pdf",
    logo_path="/path/to/logo_empresa.png"
)
```

---

## 📐 Estructura del KuDE

El KuDE generado incluye las siguientes secciones según el Manual Técnico v150:

### 1. Encabezado
- Logo del emisor (opcional)
- Tipo de documento (Factura, Nota de Crédito, etc.)
- Título "KuDE de [Tipo Documento] Electrónica"

### 2. Datos del Emisor y Timbrado
- **Emisor**: Nombre, RUC, dirección, ciudad, teléfono, email
- **Timbrado**: Número, fecha inicio vigencia, número de documento

### 3. Datos Generales y Receptor
- Fecha y hora de emisión
- Condición de venta (Contado/Crédito)
- Moneda y tipo de cambio
- RUC/Documento del receptor
- Nombre, dirección, teléfono, email del receptor
- Tipo de operación

### 4. Tabla de Ítems
Columnas:
- Código del ítem
- Descripción
- Unidad de medida
- Cantidad
- Precio unitario
- Descuento
- Valor de venta
- Exentas
- Gravado 5%
- Gravado 10%

### 5. Subtotales y Totales
- Subtotal
- Total a pagar
- Total en guaraníes
- Liquidación de IVA (5% y 10%)
- Total IVA

### 6. Información de Consulta SIFEN
- Código QR para consulta móvil
- URL de consulta: `https://ekuatia.set.gov.py/consultas/`
- CDC formateado (grupos de 4 dígitos)
- Texto legal sobre validez del documento

---

## 🎨 Personalización

### Logo del Emisor

El logo debe ser una imagen en formato PNG, JPG o similar:

```python
pdf_bytes = client.generar_kude(
    documento=documento,
    logo_path="/path/to/logo.png"
)
```

**Recomendaciones para el logo:**
- Formato: PNG con fondo transparente
- Tamaño recomendado: 300x200 px
- Peso máximo: 500 KB
- Se ajustará automáticamente a 3x2 cm en el PDF

### Ambiente (DEV/PROD)

El ambiente se toma automáticamente de la configuración del cliente:

```python
# Desarrollo
config = SifenConfig(ambiente=TipoAmbiente.DEV, ...)
# URL QR: https://ekuatia.set.gov.py/consultas-test/

# Producción
config = SifenConfig(ambiente=TipoAmbiente.PROD, ...)
# URL QR: https://ekuatia.set.gov.py/consultas/
```

---

## 📝 Ejemplo Completo

Ver el archivo `examples/ejemplo_generar_kude.py` para un ejemplo completo:

```bash
cd django-sifen
python examples/ejemplo_generar_kude.py
```

El ejemplo incluye:
- Creación de documento con múltiples ítems
- Ítems con diferentes tasas de IVA (5%, 10%, exento)
- Generación de CDC
- Generación de KuDE con logo
- Guardado del PDF

---

## ⚠️ Requisitos y Validaciones

### Requisitos previos

1. **CDC generado**: El documento debe tener CDC antes de generar el KuDE
   ```python
   if not documento.CDC:
       documento.generate_cdc()
   ```

2. **Dependencias instaladas**: ReportLab y QRCode deben estar instalados
   ```python
   try:
       pdf_bytes = client.generar_kude(documento)
   except ImportError as e:
       print("Instalar: pip install reportlab qrcode[pil]")
   ```

### Validaciones automáticas

El generador valida:
- ✅ Documento tiene CDC
- ✅ Todos los campos requeridos están presentes
- ✅ Logo existe (si se especifica ruta)
- ✅ Formato de montos y fechas

---

## 🔧 API Reference

### `SifenClient.generar_kude()`

```python
def generar_kude(
    self,
    documento: DocumentoElectronico,
    output_path: Optional[str] = None,
    logo_path: Optional[str] = None
) -> bytes
```

**Parámetros:**
- `documento`: Documento electrónico con CDC generado
- `output_path`: Ruta donde guardar el PDF (opcional)
- `logo_path`: Ruta del logo del emisor (opcional)

**Retorna:**
- `bytes`: Contenido del PDF generado

**Excepciones:**
- `ImportError`: Si ReportLab no está instalado
- `ValueError`: Si el documento no tiene CDC

### Función helper

```python
from sifen.kude_generator import generar_kude

pdf_bytes = generar_kude(
    documento=documento,
    output_path="/path/to/file.pdf",
    logo_path="/path/to/logo.png",
    ambiente=TipoAmbiente.DEV
)
```

---

## 📊 Tipos de Documentos Soportados

El generador soporta todos los tipos de documentos electrónicos:

| Tipo | Código | Nombre |
|------|--------|--------|
| Factura | 1 | Factura Electrónica |
| Autofactura | 4 | Autofactura Electrónica |
| Nota Crédito | 5 | Nota de Crédito Electrónica |
| Nota Débito | 6 | Nota de Débito Electrónica |
| Nota Remisión | 7 | Nota de Remisión Electrónica |

Cada tipo tiene su formato específico según el Manual Técnico v150.

---

## 💡 Casos de Uso

### 1. Enviar KuDE por Email

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Generar KuDE
pdf_bytes = client.generar_kude(documento)

# Crear email
msg = MIMEMultipart()
msg['Subject'] = f'Factura Electrónica - CDC: {documento.CDC}'
msg['From'] = 'facturacion@empresa.com'
msg['To'] = documento.gDatRec.dEmailRec

# Adjuntar PDF
pdf_attachment = MIMEApplication(pdf_bytes, _subtype='pdf')
pdf_attachment.add_header(
    'Content-Disposition',
    'attachment',
    filename=f'factura_{documento.CDC}.pdf'
)
msg.attach(pdf_attachment)

# Enviar
smtp = smtplib.SMTP('smtp.gmail.com', 587)
smtp.send_message(msg)
```

### 2. Guardar en AWS S3

```python
import boto3

# Generar KuDE
pdf_bytes = client.generar_kude(documento)

# Subir a S3
s3 = boto3.client('s3')
s3.put_object(
    Bucket='facturas-electronicas',
    Key=f'kude/{documento.CDC}.pdf',
    Body=pdf_bytes,
    ContentType='application/pdf'
)
```

### 3. Generar múltiples KuDEs en lote

```python
documentos = [doc1, doc2, doc3]

for documento in documentos:
    try:
        pdf_bytes = client.generar_kude(
            documento=documento,
            output_path=f'/output/kude_{documento.CDC}.pdf'
        )
        print(f"✓ KuDE generado: {documento.CDC}")
    except Exception as e:
        print(f"✗ Error en {documento.CDC}: {e}")
```

---

## 🐛 Troubleshooting

### Error: "ReportLab no está instalado"

```bash
pip install reportlab
```

### Error: "El documento debe tener CDC generado"

```python
# Generar CDC antes del KuDE
documento.generate_cdc()
pdf_bytes = client.generar_kude(documento)
```

### Error: "No se puede abrir el logo"

```python
# Verificar que el archivo existe
import os
if os.path.exists(logo_path):
    pdf_bytes = client.generar_kude(documento, logo_path=logo_path)
else:
    # Generar sin logo
    pdf_bytes = client.generar_kude(documento)
```

### PDF generado pero no se ve el QR

```bash
# Instalar dependencias de QR
pip install qrcode[pil]
```

---

## 📚 Referencias

- **Manual Técnico SIFEN v150**: Capítulo 13 - Gráfica (KUDE)
- **ReportLab**: https://www.reportlab.com/docs/reportlab-userguide.pdf
- **QRCode**: https://pypi.org/project/qrcode/
- **Consulta SIFEN**: https://ekuatia.set.gov.py/consultas/

---

## ✅ Checklist de Implementación

- [x] Generador de PDF con ReportLab
- [x] Encabezado con logo opcional
- [x] Datos del emisor y timbrado
- [x] Datos generales y receptor
- [x] Tabla de ítems con IVA
- [x] Subtotales y totales
- [x] Liquidación de IVA
- [x] Código QR de consulta
- [x] CDC formateado
- [x] Texto legal
- [x] Integración con SifenClient
- [x] Ejemplo de uso
- [x] Documentación completa

---

## 🎯 Próximos Pasos

1. **Probar la generación**: Ejecutar `ejemplo_generar_kude.py`
2. **Personalizar diseño**: Ajustar colores, fuentes, espaciados
3. **Integrar en tu aplicación**: Usar `client.generar_kude()` después de enviar documentos
4. **Automatizar envío**: Enviar KuDE por email automáticamente
5. **Almacenar PDFs**: Guardar en sistema de archivos o cloud storage
