# django-sifen

Librería Python para Facturación Electrónica de Paraguay (SIFEN)

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Django Version](https://img.shields.io/badge/django-3.2+-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Documentación

### Guías Técnicas

- **[Manejo de Certificados](docs/CERTIFICADOS.md)** - Todas las formas de configurar certificados digitales
  - Archivo en disco, bytes, Base64
  - Desde base de datos o secrets manager
  - Variables de entorno y cloud
  - Mejores prácticas de seguridad
  
- **[Estructura XML](docs/ESTRUCTURA_XML.md)** - Documentación completa de la estructura XML generada
  - Grupos principales y su ubicación en el código
  - Dónde modificar según cambios de SIFEN
  - Ejemplos de cambios comunes
  - Mejores prácticas de mantenimiento

### Ejemplos de Uso

Para más detalles sobre el uso de la librería, consulta los ejemplos en el directorio `examples/`:

- `ejemplo_basico.py` - Uso básico de la librería
- `ejemplo_certificados.py` - Todas las formas de configurar certificados
- `ejemplo_nota_tecnica_13.py` - Cálculo de IVA con NT-13
- `ejemplo_validacion_firmas.py` - Validación de firmas digitales y QR
- `ejemplo_compresion_lote.py` - Compresión ZIP en lotes

## Descripción

`django-sifen` es una librería Python completa para interactuar con el Sistema Integrado de Facturación Electrónica Nacional (SIFEN) de Paraguay. Está basada en el **Manual Técnico Versión 150** y proporciona una API robusta para:

- ✅ Emisión de Documentos Electrónicos (facturas, notas de crédito, etc.)
- ✅ Consulta de RUC
- ✅ Consulta de estado de documentos
- ✅ Firma digital XML con certificados PFX
- ✅ Validaciones automáticas
- ✅ Cálculos de IVA y totales
- ✅ API REST completa con Django

## Características Principales

### Core
-  **Firma Digital XML**: Soporte completo para certificados PFX con XMLDSig
-  **Modelos de Datos**: Dataclasses Python para todos los campos SIFEN
-  **Generación XML**: Conversión automática a XML SIFEN
-  **Validaciones**: RUC, CDC, emails, teléfonos
-  **Calculadoras**: IVA, totales, precios automáticos
-  **Nota Técnica 13**: Cálculo correcto de base exenta para gravado parcial
-  **Servicios Web**: Todos los 6 servicios SIFEN (Recepción DE, Consulta RUC, Consulta DE, Recepción Lote, Consulta Lote, Recepción Eventos)

### Django Integration
-  **API REST**: Endpoints completos con Django REST Framework
-  **Modelos Django**: Almacenamiento de documentos y configuración
-  **Admin**: Panel de administración visual
-  **Logs**: Auditoría completa de comunicaciones
-  **Autenticación**: Token-based authentication
-  **Documentación**: Swagger/OpenAPI automática

### Utilidades
-  **Formatters**: RUC, CDC, moneda, teléfonos
-  **Validators**: Validación de datos antes de enviar
-  **Calculators**: Cálculos automáticos de IVA y totales
-  **Cliente Unificado**: API simple con `SifenClient`

## Instalación

### Desde GitHub

```bash
pip install git+https://github.com/girolabs/django-sifen.git
```

### Con soporte Django (recomendado)

```bash
pip install git+https://github.com/girolabs/django-sifen.git[django]
```

### Para desarrollo

```bash
git clone https://github.com/girolabs/django-sifen.git
cd django-sifen
pip install -e .[dev,django]
```

## Inicio Rápido

### 1. Configuración

```python
from sifen import SifenClient, SifenConfig
from sifen.config import TipoAmbiente

# Crear configuración
config = SifenConfig(
    ambiente=TipoAmbiente.DEV,
    certificado_archivo="/path/to/certificado.pfx",
    certificado_contrasena="mi_password",
    csc="ABCD0000000000000000000000000000",
    csc_id="0001",
)

# Crear cliente
client = SifenClient(config)
```

### 2. Crear y Enviar Documento

```python
from sifen.models import DocumentoElectronico, Item
from sifen.utils import calcular_valor_item, calcular_totales
from decimal import Decimal

# Crear ítem con cálculos automáticos
item = Item(
    dCodInt="PROD001",
    dDesProSer="Producto de Prueba",
    cUniMed=77,
    dCantProSer=Decimal('10'),
    gValorItem=calcular_valor_item(
        precio_unitario=Decimal('100000'),
        cantidad=Decimal('10'),
        tasa_iva=10,
    ),
)

# Calcular totales automáticamente
totales = calcular_totales([item])

# Crear documento
documento = DocumentoElectronico(...)

# Enviar a SIFEN (valida, genera CDC, XML, firma y envía)
respuesta = client.enviar_documento(documento)

if respuesta.aprobado:
    print(f"✓ Aprobado: {respuesta.cdc}")
    print(f"Protocolo: {respuesta.numero_protocolo}")
else:
    print(f"✗ Rechazado: {respuesta.mensaje}")
```

### 3. Consultar RUC

```python
# Consultar RUC en SIFEN
respuesta = client.consultar_ruc("80012345", "6")

if respuesta.encontrado:
    print(f"Nombre: {respuesta.contribuyente.nombre}")
    print(f"Estado: {respuesta.contribuyente.estado}")
```

### 4. Validaciones

```python
from sifen.utils import validar_ruc, calcular_dv_ruc

# Validar RUC
if validar_ruc("80012345", "6"):
    print("✓ RUC válido")

# Calcular DV
dv = calcular_dv_ruc("80012345")  # Retorna: 6
```

### 5. Envío de Lotes

```python
# Crear múltiples documentos
documentos = [documento1, documento2, documento3]  # Máximo 50

# Enviar lote (valida, genera CDC, XML, firma, comprime y envía todo)
# Los XMLs se comprimen con GZIP y se codifican en Base64 automáticamente
respuesta = client.enviar_lote(documentos)

if respuesta.exitoso:
    print(f"✓ Lote enviado: {respuesta.numero_lote}")
    print(f"Aprobados: {respuesta.documentos_aprobados}")
    print(f"Rechazados: {respuesta.documentos_rechazados}")
    
    # Ver detalle de cada documento
    for detalle in respuesta.detalles:
        print(f"CDC: {detalle.cdc} - {'Aprobado' if detalle.aprobado else 'Rechazado'}")

# Consultar estado del lote
consulta = client.consultar_lote(respuesta.numero_lote)
print(f"Estado del lote: {consulta.estado}")
```

### 6. Eventos

```python
# Cancelar un documento
respuesta = client.cancelar_documento(
    cdc="01001001000000112024050412300080012345601",
    motivo="Error en datos del cliente"
)

if respuesta.aprobado:
    print(f"✓ Documento cancelado")
    print(f"Protocolo: {respuesta.numero_protocolo}")

# Enviar conformidad (receptor confirma recepción)
client.enviar_conformidad(cdc="...")

# Enviar disconformidad (receptor rechaza)
client.enviar_disconformidad(
    cdc="...",
    motivo="Mercadería no recibida"
)
```

**Tipos de eventos soportados:**
- ✅ Cancelación
- ✅ Conformidad
- ✅ Disconformidad
- ✅ Desconocimiento
- ✅ Inutilización
- ✅ Notificación de no recepción

### 7. Validación de Firmas y QR

```python
# Validar firma de XML recibido
resultado = client.validar_firma_xml(xml_recibido)

if resultado.is_valid:
    print(f"✓ Firma válida - Emisor: {resultado.subject}")
    print(f"Válido hasta: {resultado.valid_to}")
else:
    print(f"✗ Firma inválida: {resultado.error}")

# Validar archivo XML
resultado = client.validar_firma_archivo("/path/to/documento.xml")

# Generar URL de consulta QR
url_qr = client.generar_url_qr(cdc)
print(url_qr)  # https://ekuatia.set.gov.py/consultas/qr?...

# Generar código QR (requiere: pip install qrcode[pil])
import qrcode
qr = qrcode.make(url_qr)
qr.save("documento_qr.png")
```

## Integración con Django

### 1. Agregar a INSTALLED_APPS

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'django_filters',
    'corsheaders',
    'drf_spectacular',
    'sifen_django',
]
```

### 2. Configurar en settings.py

```python
SIFEN_CONFIG = {
    'ambiente': 'DEV',
    'certificado_archivo': BASE_DIR / 'certs' / 'certificado.pfx',
    'certificado_contrasena': env('SIFEN_CERT_PASSWORD'),
    'csc': env('SIFEN_CSC'),
    'csc_id': env('SIFEN_CSC_ID'),
    'habilitar_nota_tecnica_13': True,
}
```

### 3. Incluir URLs

```python
from django.urls import path, include

urlpatterns = [
    ...
    path('api/sifen/', include('sifen_django.urls')),
]
```

### 4. Usar la API REST

La librería expone los siguientes endpoints:

- `GET /api/sifen/documentos/` - Listar documentos electrónicos
- `POST /api/sifen/documentos/` - Crear y enviar DE
- `GET /api/sifen/documentos/{id}/` - Detalle de DE
- `GET /api/sifen/documentos/{id}/xml/` - Obtener XML formateado
- `GET /api/sifen/documentos/{id}/qr/` - Obtener imagen QR
- `POST /api/sifen/documentos/{id}/consultar/` - Consultar estado
- `GET /api/sifen/estadisticas/` - Estadísticas
- `GET /api/sifen/consulta-ruc/{ruc}/` - Consultar RUC

## Documentación

- [Instalación](docs/installation.md)
- [Configuración](docs/configuration.md)
- [Uso](docs/usage.md)
- [Integración Django](docs/django_integration.md)
- [API Reference](docs/api_reference.md)

## Requisitos

- Python 3.8+
- Django 3.2+ (opcional, para sifen_django)

## Licencia

MIT License - ver [LICENSE](LICENSE) para más detalles.

## Créditos

Basado en la librería Java [rshk-jsifenlib](https://github.com/roshkadev/rshk-jsifenlib) v0.2.4.

## Soporte

Para reportar bugs o solicitar features, por favor crear un issue en GitHub.
