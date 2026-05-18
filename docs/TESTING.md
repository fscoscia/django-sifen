# Guía de Testing - django-sifen

Esta guía explica cómo probar que todo funciona correctamente en la librería django-sifen.

## 📋 Tabla de Contenidos

- [Tests Rápidos](#tests-rápidos)
- [Tests por Componente](#tests-por-componente)
- [Tests de Integración](#tests-de-integración)
- [Ambiente de Desarrollo SIFEN](#ambiente-de-desarrollo-sifen)
- [Tests Automatizados](#tests-automatizados)
- [Troubleshooting](#troubleshooting)

---

## ⚡ Tests Rápidos

### 1. Verificar Instalación

```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Verificar instalación
python -c "import sifen; print('✓ SIFEN instalado correctamente')"
```

### 2. Test de Configuración

```python
# test_config.py
from sifen import SifenConfig, TipoAmbiente

# Crear configuración
config = SifenConfig(
    ambiente=TipoAmbiente.DEV,
    certificado_archivo="path/to/cert.pfx",
    certificado_contrasena="password",
    csc="test_csc",
    csc_id="0001"
)

print(f"✓ Configuración creada")
print(f"  Ambiente: {config.ambiente.value}")
print(f"  CSC ID: {config.csc_id}")
```

### 3. Test de Certificado

```python
# test_certificado.py
from sifen import SifenConfig, TipoAmbiente
from sifen.crypto import load_certificate

config = SifenConfig(
    ambiente=TipoAmbiente.DEV,
    certificado_archivo="certs/dev.pfx",
    certificado_contrasena="password",
    csc="test",
    csc_id="0001"
)

try:
    # Intentar cargar certificado
    cert_bytes = config.get_certificado_bytes()
    print(f"✓ Certificado cargado: {len(cert_bytes)} bytes")
    
    # Validar certificado
    cert_info = load_certificate(cert_bytes, config.certificado_contrasena)
    print(f"✓ Certificado válido")
    print(f"  Subject: {cert_info.get('subject', 'N/A')}")
    
except Exception as e:
    print(f"✗ Error: {e}")
```

---

## 🧪 Tests por Componente

### A. Test de Modelos

```python
# test_modelos.py
from sifen.models import (
    DocumentoElectronico,
    Timbrado,
    Emisor,
    Receptor,
    Item,
    Totales
)
from datetime import datetime, date

print("Testing Modelos...")

# 1. Timbrado
timbrado = Timbrado(
    iTiDE=1,
    dNumTim="12345678",
    dEst="001",
    dPunExp="001",
    dNumDoc="0000001",
    dFeIniT=datetime.now()
)
print("✓ Timbrado creado")

# 2. Emisor
emisor = Emisor(
    dRucEm="80012345-6",
    dDVEmi="6",
    dNomEmi="Empresa Test SA",
    dDirEmi="Av. Test 123",
    dTelEmi="021-123456",
    dEmailE="test@empresa.com.py"
)
print("✓ Emisor creado")

# 3. Receptor
receptor = Receptor(
    iNatRec=1,
    iTiOpe=1,
    dNomRec="Cliente Test",
    dRucRec="80098765-4"
)
print("✓ Receptor creado")

# 4. Item
item = Item(
    dNroItem=1,
    dCodInt="PROD001",
    dDesProSer="Producto Test",
    dCantProSer=10.0,
    dPUniProSer=100000.0
)
print("✓ Item creado")

print("\n✓ Todos los modelos funcionan correctamente")
```

### B. Test de Calculadoras

```python
# test_calculadoras.py
from decimal import Decimal
from sifen.utils.calculators import (
    calcular_iva_item,
    calcular_totales,
    calcular_base_exenta_nt13
)
from sifen.models import Item

print("Testing Calculadoras...")

# 1. Test IVA 10%
item = Item(
    dNroItem=1,
    dCodInt="PROD001",
    dDesProSer="Producto",
    dCantProSer=Decimal("10"),
    dPUniProSer=Decimal("100000")
)

iva_result = calcular_iva_item(
    item,
    afectacion_iva=1,  # Gravado 10%
    tasa_iva=Decimal("10"),
    proporcion_iva=Decimal("100")
)

print(f"✓ IVA 10% calculado:")
print(f"  Base Gravada: {iva_result.dBasGravIVA}")
print(f"  Liquidación IVA: {iva_result.dLiqIVAItem}")

# 2. Test Nota Técnica 13
base_exenta = calcular_base_exenta_nt13(
    total_operacion=Decimal("1000000"),
    proporcion_iva=Decimal("50"),
    tasa_iva=Decimal("10")
)
print(f"✓ NT-13 calculado: {base_exenta}")

print("\n✓ Calculadoras funcionan correctamente")
```

### C. Test de Generación XML

```python
# test_xml.py
from sifen.xml.generator import XMLGenerator
from sifen.models import DocumentoElectronico
from lxml import etree

print("Testing Generación XML...")

# Crear documento mínimo
documento = DocumentoElectronico(
    Id="01800123456001001000000012024050400000001",
    dVerFor=150,
    # ... agregar campos necesarios
)

try:
    # Generar XML
    generator = XMLGenerator(documento)
    xml_element = generator.generate()
    
    # Convertir a string
    xml_string = etree.tostring(
        xml_element,
        encoding='unicode',
        pretty_print=True
    )
    
    print("✓ XML generado correctamente")
    print(f"  Longitud: {len(xml_string)} caracteres")
    print(f"  Primeras líneas:")
    print(xml_string[:200])
    
except Exception as e:
    print(f"✗ Error generando XML: {e}")
```

### D. Test de Firma Digital

```python
# test_firma.py
from sifen.crypto import sign_xml
from sifen import SifenConfig, TipoAmbiente

print("Testing Firma Digital...")

config = SifenConfig(
    ambiente=TipoAmbiente.DEV,
    certificado_archivo="certs/dev.pfx",
    certificado_contrasena="password",
    csc="test",
    csc_id="0001"
)

xml_sin_firmar = """<?xml version="1.0" encoding="UTF-8"?>
<rDE xmlns="http://ekuatia.set.gov.py/sifen/xsd">
    <DE Id="test123">
        <dVerFor>150</dVerFor>
    </DE>
</rDE>"""

try:
    # Firmar XML
    xml_firmado = sign_xml(
        xml_sin_firmar,
        config.get_certificado_bytes(),
        config.certificado_contrasena
    )
    
    print("✓ XML firmado correctamente")
    print(f"  Contiene <Signature>: {'<Signature' in xml_firmado}")
    
except Exception as e:
    print(f"✗ Error firmando XML: {e}")
```

### E. Test de Validación de Firmas

```python
# test_validacion_firma.py
from sifen.crypto import validate_xml_signature

print("Testing Validación de Firmas...")

# XML firmado (ejemplo)
xml_firmado = """<?xml version="1.0"?>
<rDE xmlns="...">
    ...
    <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
        ...
    </Signature>
</rDE>"""

try:
    result = validate_xml_signature(xml_firmado)
    
    if result.is_valid:
        print("✓ Firma válida")
        print(f"  Certificado: {result.certificate_info.get('subject', 'N/A')}")
    else:
        print(f"✗ Firma inválida: {result.error}")
        
except Exception as e:
    print(f"✗ Error validando firma: {e}")
```

---

## 🔗 Tests de Integración

### Test Completo: Crear y Enviar Documento

```python
# test_integracion_completo.py
"""
Test de integración completo:
1. Crear documento
2. Generar XML
3. Firmar XML
4. Enviar a SIFEN (DEV)
5. Consultar estado
"""

from sifen import SifenClient, SifenConfig, TipoAmbiente
from sifen.models import (
    DocumentoElectronico,
    Timbrado,
    DatosGenerales,
    Emisor,
    Receptor,
    Item
)
from datetime import datetime, date
from decimal import Decimal

def test_flujo_completo():
    print("=" * 70)
    print("TEST DE INTEGRACIÓN COMPLETO")
    print("=" * 70)
    
    # 1. CONFIGURACIÓN
    print("\n1. Configurando cliente...")
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,  # ← Ambiente de desarrollo
        certificado_archivo="certs/dev.pfx",
        certificado_contrasena="dev_password",
        csc="DEV_CSC_12345",
        csc_id="0001"
    )
    
    client = SifenClient(config)
    print("   ✓ Cliente configurado")
    
    # 2. CREAR DOCUMENTO
    print("\n2. Creando documento...")
    
    # Timbrado
    timbrado = Timbrado(
        iTiDE=1,  # Factura
        dNumTim="12345678",
        dEst="001",
        dPunExp="001",
        dNumDoc="0000001",
        dFeIniT=datetime.now()
    )
    
    # Emisor
    emisor = Emisor(
        dRucEm="80012345-6",
        dDVEmi="6",
        iTipCont=1,
        dNomEmi="Empresa Test SA",
        dDirEmi="Av. Test 123",
        cDepEmi=1,
        cDisEmi=1,
        cCiuEmi=1,
        dTelEmi="021-123456",
        dEmailE="test@empresa.com.py",
        gActEco=[{
            "cActEco": "47111",
            "dDesActEco": "Venta al por menor"
        }]
    )
    
    # Receptor
    receptor = Receptor(
        iNatRec=1,
        iTiOpe=1,
        dNomRec="Cliente Test",
        dRucRec="80098765-4",
        dDVRec="4",
        dDirRec="Calle Test 456",
        dTelRec="021-654321"
    )
    
    # Item
    item = Item(
        dNroItem=1,
        dCodInt="PROD001",
        dDesProSer="Producto de Prueba",
        cUniMed=77,
        dDesUniMed="Unidades",
        dCantProSer=Decimal("10"),
        cPaisOrig="PRY",
        dDesPaisOrig="Paraguay",
        dPUniProSer=Decimal("100000"),
        iAfecIVA=1,  # Gravado 10%
        dPropIVA=Decimal("100"),
        dTasaIVA=Decimal("10")
    )
    
    # Documento
    documento = DocumentoElectronico(
        gTimb=timbrado,
        gDatGralOpe={
            "dFeEmiDE": date.today(),
            "iTipEmi": 1,
            "gEmis": emisor,
            "gDatRec": receptor
        },
        gCamItem=[item],
        gCamCond={
            "iCondOpe": 1,  # Contado
            "gPaConEIni": [{
                "iTiPago": 1,  # Efectivo
                "dMonTiPag": Decimal("1000000"),
                "cMoneTiPag": "PYG"
            }]
        }
    )
    
    print("   ✓ Documento creado")
    
    # 3. ENVIAR A SIFEN
    print("\n3. Enviando a SIFEN (DEV)...")
    
    try:
        respuesta = client.enviar_documento(documento)
        
        if respuesta.aprobado:
            print("   ✓ Documento APROBADO")
            print(f"     CDC: {respuesta.cdc}")
            print(f"     Protocolo: {respuesta.protocolo}")
            
            # 4. CONSULTAR ESTADO
            print("\n4. Consultando estado...")
            consulta = client.consultar_documento(respuesta.cdc)
            
            print(f"   ✓ Estado: {consulta.estado}")
            print(f"     Mensaje: {consulta.mensaje}")
            
            return True
            
        else:
            print(f"   ✗ Documento RECHAZADO")
            print(f"     Código: {respuesta.codigo}")
            print(f"     Mensaje: {respuesta.mensaje}")
            return False
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    exito = test_flujo_completo()
    
    print("\n" + "=" * 70)
    if exito:
        print("✓ TEST COMPLETO EXITOSO")
    else:
        print("✗ TEST COMPLETO FALLÓ")
    print("=" * 70)
```

---

## 🌐 Ambiente de Desarrollo SIFEN

### Credenciales de Prueba

SIFEN proporciona un ambiente de desarrollo con certificados de prueba:

```python
# Configuración para ambiente DEV
config = SifenConfig(
    ambiente=TipoAmbiente.DEV,  # ← Importante: DEV
    
    # Certificado de prueba (solicitar a SIFEN)
    certificado_archivo="certs/sifen_dev.pfx",
    certificado_contrasena="password_dev",
    
    # CSC de desarrollo (proporcionado por SIFEN)
    csc="DEV_CSC_PROPORCIONADO_POR_SIFEN",
    csc_id="0001"
)
```

### Obtener Certificado de Prueba

1. **Registrarse en Portal e-Kuatia:**
   - URL: https://ekuatia.set.gov.py/portal/ekuatia
   - Crear cuenta de desarrollador

2. **Solicitar Certificado de Prueba:**
   - Ir a sección "Desarrolladores"
   - Descargar certificado de prueba
   - Guardar password proporcionado

3. **Obtener CSC de Desarrollo:**
   - En el portal, ir a "Configuración"
   - Copiar CSC y CSC ID de desarrollo

### URLs de Ambiente DEV

```python
# Ya configuradas en la librería
URL_BASE_DEV = "https://sifen-test.set.gov.py/de/ws/..."
URL_CONSULTA_QR_DEV = "https://ekuatia.set.gov.py/consultas-test/qr"
```

---

## 🤖 Tests Automatizados

### Estructura de Tests

```
tests/
├── __init__.py
├── test_config.py           # Tests de configuración
├── test_models.py           # Tests de modelos
├── test_calculators.py      # Tests de calculadoras
├── test_xml_generator.py    # Tests de generación XML
├── test_crypto.py           # Tests de firma/validación
├── test_services.py         # Tests de servicios SIFEN
└── test_integration.py      # Tests de integración
```

### Ejecutar Tests con pytest

```bash
# Instalar pytest
pip install pytest pytest-cov

# Ejecutar todos los tests
pytest tests/

# Con coverage
pytest --cov=sifen tests/

# Test específico
pytest tests/test_calculators.py

# Con output verbose
pytest -v tests/

# Solo tests que fallan
pytest --lf tests/
```

### Ejemplo de Test con pytest

```python
# tests/test_calculators.py
import pytest
from decimal import Decimal
from sifen.utils.calculators import calcular_base_exenta_nt13

class TestCalculadoras:
    
    def test_base_exenta_nt13_basico(self):
        """Test básico de cálculo NT-13."""
        resultado = calcular_base_exenta_nt13(
            total_operacion=Decimal("1000000"),
            proporcion_iva=Decimal("50"),
            tasa_iva=Decimal("10")
        )
        
        assert resultado > 0
        assert isinstance(resultado, Decimal)
    
    def test_base_exenta_nt13_proporcion_100(self):
        """Test con proporción 100%."""
        resultado = calcular_base_exenta_nt13(
            total_operacion=Decimal("1000000"),
            proporcion_iva=Decimal("100"),
            tasa_iva=Decimal("10")
        )
        
        assert resultado == Decimal("0")
    
    def test_base_exenta_nt13_proporcion_0(self):
        """Test con proporción 0%."""
        resultado = calcular_base_exenta_nt13(
            total_operacion=Decimal("1000000"),
            proporcion_iva=Decimal("0"),
            tasa_iva=Decimal("10")
        )
        
        assert resultado == Decimal("1000000")
    
    @pytest.mark.parametrize("total,prop,tasa,esperado", [
        (Decimal("1000000"), Decimal("50"), Decimal("10"), Decimal("476190.48")),
        (Decimal("500000"), Decimal("25"), Decimal("5"), Decimal("365853.66")),
    ])
    def test_base_exenta_nt13_casos(self, total, prop, tasa, esperado):
        """Test con múltiples casos."""
        resultado = calcular_base_exenta_nt13(total, prop, tasa)
        assert abs(resultado - esperado) < Decimal("0.01")
```

### Ejecutar Tests

```bash
# Todos los tests
pytest tests/ -v

# Output:
# tests/test_calculators.py::TestCalculadoras::test_base_exenta_nt13_basico PASSED
# tests/test_calculators.py::TestCalculadoras::test_base_exenta_nt13_proporcion_100 PASSED
# tests/test_calculators.py::TestCalculadoras::test_base_exenta_nt13_proporcion_0 PASSED
# tests/test_calculators.py::TestCalculadoras::test_base_exenta_nt13_casos[...] PASSED
```

---

## 🔍 Troubleshooting

### Problema 1: Error al Cargar Certificado

```
Error: Unable to load certificate
```

**Solución:**
```python
# Verificar que el archivo existe
import os
cert_path = "certs/dev.pfx"
print(f"Archivo existe: {os.path.exists(cert_path)}")

# Verificar permisos
print(f"Puede leer: {os.access(cert_path, os.R_OK)}")

# Verificar password
from sifen.crypto import load_certificate

try:
    with open(cert_path, "rb") as f:
        cert_bytes = f.read()
    
    cert = load_certificate(cert_bytes, "password")
    print("✓ Certificado válido")
except Exception as e:
    print(f"✗ Error: {e}")
```

### Problema 2: Error de Conexión a SIFEN

```
Error: Connection timeout
```

**Solución:**
```python
# 1. Verificar conectividad
import requests

try:
    response = requests.get(
        "https://sifen-test.set.gov.py/de/ws/sync/recibe.wsdl",
        timeout=10
    )
    print(f"✓ Conectividad OK: {response.status_code}")
except Exception as e:
    print(f"✗ Error de conexión: {e}")

# 2. Verificar configuración de proxy (si aplica)
config = SifenConfig(
    ambiente=TipoAmbiente.DEV,
    # ... otros parámetros
    http_connect_timeout=30,  # ← Aumentar timeout
    http_read_timeout=60
)
```

### Problema 3: XML Inválido

```
Error: Invalid XML structure
```

**Solución:**
```python
# Validar XML generado
from lxml import etree

xml_string = """<?xml version="1.0"?>
<rDE>...</rDE>"""

try:
    # Parsear XML
    root = etree.fromstring(xml_string.encode('utf-8'))
    print("✓ XML válido")
    
    # Verificar namespace
    print(f"Namespace: {root.nsmap}")
    
    # Verificar estructura
    print(f"Tag raíz: {root.tag}")
    print(f"Hijos: {len(root)}")
    
except etree.XMLSyntaxError as e:
    print(f"✗ XML inválido: {e}")
```

### Problema 4: Firma Digital Inválida

```
Error: Invalid signature
```

**Solución:**
```python
# Verificar firma paso a paso
from sifen.crypto import sign_xml, validate_xml_signature

# 1. Firmar
xml_firmado = sign_xml(xml_sin_firmar, cert_bytes, password)

# 2. Verificar que contiene firma
if '<Signature' not in xml_firmado:
    print("✗ No se agregó firma")
else:
    print("✓ Firma agregada")

# 3. Validar firma
result = validate_xml_signature(xml_firmado)
if not result.is_valid:
    print(f"✗ Firma inválida: {result.error}")
else:
    print("✓ Firma válida")
```

---

## 📊 Checklist de Verificación

### Antes de Producción

- [ ] **Configuración**
  - [ ] Certificado de producción configurado
  - [ ] CSC de producción configurado
  - [ ] Ambiente configurado como PROD
  - [ ] Timeouts apropiados

- [ ] **Tests**
  - [ ] Tests unitarios pasan
  - [ ] Tests de integración pasan
  - [ ] Probado en ambiente DEV
  - [ ] Validación de firmas funciona

- [ ] **Seguridad**
  - [ ] Certificados no commiteados
  - [ ] Contraseñas en variables de entorno
  - [ ] Logs no exponen datos sensibles
  - [ ] Certificado válido y no vencido

- [ ] **Funcionalidad**
  - [ ] Envío de documentos funciona
  - [ ] Consulta de documentos funciona
  - [ ] Consulta de RUC funciona
  - [ ] Eventos funcionan (si aplica)

---

## 🚀 Script de Verificación Rápida

```python
# verificar_todo.py
"""Script para verificar que todo funciona."""

import sys
from pathlib import Path

def verificar_instalacion():
    """Verifica que la librería está instalada."""
    try:
        import sifen
        print("✓ Librería instalada")
        return True
    except ImportError:
        print("✗ Librería no instalada")
        return False

def verificar_dependencias():
    """Verifica dependencias."""
    dependencias = [
        'lxml',
        'cryptography',
        'requests',
        'python-dotenv'
    ]
    
    todas_ok = True
    for dep in dependencias:
        try:
            __import__(dep.replace('-', '_'))
            print(f"✓ {dep}")
        except ImportError:
            print(f"✗ {dep} no instalado")
            todas_ok = False
    
    return todas_ok

def verificar_certificado(cert_path, password):
    """Verifica certificado."""
    from sifen.crypto import load_certificate
    
    if not Path(cert_path).exists():
        print(f"✗ Certificado no encontrado: {cert_path}")
        return False
    
    try:
        with open(cert_path, "rb") as f:
            cert_bytes = f.read()
        
        cert_info = load_certificate(cert_bytes, password)
        print(f"✓ Certificado válido")
        print(f"  Subject: {cert_info.get('subject', 'N/A')}")
        return True
    except Exception as e:
        print(f"✗ Error con certificado: {e}")
        return False

def verificar_conectividad():
    """Verifica conectividad con SIFEN."""
    import requests
    
    try:
        response = requests.get(
            "https://sifen-test.set.gov.py/de/ws/sync/recibe.wsdl",
            timeout=10
        )
        print(f"✓ Conectividad SIFEN OK ({response.status_code})")
        return True
    except Exception as e:
        print(f"✗ Error de conectividad: {e}")
        return False

def main():
    print("=" * 70)
    print("VERIFICACIÓN DE INSTALACIÓN DJANGO-SIFEN")
    print("=" * 70)
    
    resultados = []
    
    print("\n1. Instalación:")
    resultados.append(verificar_instalacion())
    
    print("\n2. Dependencias:")
    resultados.append(verificar_dependencias())
    
    print("\n3. Conectividad:")
    resultados.append(verificar_conectividad())
    
    # Opcional: verificar certificado
    cert_path = input("\n4. Ruta al certificado (Enter para saltar): ").strip()
    if cert_path:
        password = input("   Password: ").strip()
        resultados.append(verificar_certificado(cert_path, password))
    
    print("\n" + "=" * 70)
    if all(resultados):
        print("✓ TODAS LAS VERIFICACIONES PASARON")
        print("=" * 70)
        return 0
    else:
        print("✗ ALGUNAS VERIFICACIONES FALLARON")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

**Ejecutar:**
```bash
python verificar_todo.py
```

---

## 📚 Referencias

- [Pytest Documentation](https://docs.pytest.org/)
- [Portal e-Kuatia](https://ekuatia.set.gov.py/portal/ekuatia)
- [Manual Técnico SIFEN](https://ekuatia.set.gov.py/portal/ekuatia/documentos.html)

---

**Última actualización:** Mayo 2024  
**Versión:** 1.0.0
