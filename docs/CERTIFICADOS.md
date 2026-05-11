# Manejo de Certificados Digitales en django-sifen

Esta guía explica todas las formas de configurar y usar certificados digitales (PFX/PKCS12) en la librería.

## 📋 Tabla de Contenidos

- [Opciones Disponibles](#opciones-disponibles)
- [Opción 1: Archivo en Disco](#opción-1-archivo-en-disco)
- [Opción 2: Bytes en Memoria](#opción-2-bytes-en-memoria)
- [Opción 3: Base64](#opción-3-base64-string)
- [Opción 4: Desde Base de Datos](#opción-4-desde-base-de-datos)
- [Opción 5: Variables de Entorno](#opción-5-variables-de-entorno)
- [Opción 6: Secrets Manager](#opción-6-secrets-manager-aws-azure-gcp)
- [Mejores Prácticas](#mejores-prácticas)
- [Seguridad](#seguridad)

---

## 🎯 Opciones Disponibles

La librería soporta **3 formas principales** de proveer el certificado:

| Opción | Parámetro | Uso Recomendado |
|--------|-----------|-----------------|
| **Archivo** | `certificado_archivo` | Desarrollo local, scripts |
| **Bytes** | `certificado_bytes` | Base de datos, memoria |
| **Base64** | `certificado_base64` | Variables de entorno, APIs |

---

## 📁 Opción 1: Archivo en Disco

### Uso Básico

```python
from sifen import SifenConfig, TipoAmbiente

config = SifenConfig(
    ambiente=TipoAmbiente.PROD,
    certificado_archivo="/path/to/certificado.pfx",  # ← Ruta al archivo
    certificado_contrasena="mi_password_seguro",
    csc="ABCD1234567890...",
    csc_id="0001"
)
```

### Con Path Relativo

```python
from pathlib import Path

# Relativo al proyecto
cert_path = Path(__file__).parent / "certs" / "empresa.pfx"

config = SifenConfig(
    ambiente=TipoAmbiente.PROD,
    certificado_archivo=str(cert_path),
    certificado_contrasena="password",
    csc="...",
    csc_id="0001"
)
```

### Con Variables de Entorno

```python
import os

config = SifenConfig(
    ambiente=TipoAmbiente.PROD,
    certificado_archivo=os.getenv("SIFEN_CERT_PATH"),
    certificado_contrasena=os.getenv("SIFEN_CERT_PASSWORD"),
    csc=os.getenv("SIFEN_CSC"),
    csc_id=os.getenv("SIFEN_CSC_ID")
)
```

**Ventajas:**
- ✅ Simple y directo
- ✅ Fácil de usar en desarrollo
- ✅ No requiere conversiones

**Desventajas:**
- ❌ Archivo debe estar en disco
- ❌ Problemas en contenedores efímeros
- ❌ Difícil de rotar certificados
- ❌ Riesgo de seguridad si se commitea

---

## 💾 Opción 2: Bytes en Memoria

### Desde Archivo (Lectura Manual)

```python
# Leer archivo a bytes
with open("/path/to/certificado.pfx", "rb") as f:
    cert_bytes = f.read()

config = SifenConfig(
    ambiente=TipoAmbiente.PROD,
    certificado_bytes=cert_bytes,  # ← Bytes directos
    certificado_contrasena="password",
    csc="...",
    csc_id="0001"
)
```

### Desde Base de Datos

```python
# Django ORM
from django_sifen_api.models import ConfiguracionSIFEN

config_db = ConfiguracionSIFEN.objects.get(activo=True)

config = SifenConfig(
    ambiente=TipoAmbiente.PROD,
    certificado_bytes=config_db.certificado_pfx,  # ← BinaryField
    certificado_contrasena=config_db.certificado_contrasena,
    csc=config_db.csc,
    csc_id=config_db.csc_id
)
```

### Desde API Externa

```python
import requests

# Obtener certificado de API
response = requests.get(
    "https://api.empresa.com/certificados/actual",
    headers={"Authorization": f"Bearer {token}"}
)

cert_bytes = response.content

config = SifenConfig(
    ambiente=TipoAmbiente.PROD,
    certificado_bytes=cert_bytes,
    certificado_contrasena="password",
    csc="...",
    csc_id="0001"
)
```

**Ventajas:**
- ✅ No requiere archivo en disco
- ✅ Funciona en contenedores
- ✅ Fácil de obtener de DB/API
- ✅ Rotación dinámica

**Desventajas:**
- ⚠️ Debe manejar bytes en memoria

---

## 🔐 Opción 3: Base64 String

### Desde Variable de Entorno

```python
import os

# Variable de entorno con certificado en Base64
# SIFEN_CERT_B64=MIIKpAIBAzCCCl4GCSqGSIb3DQEHAaCCCk8...

config = SifenConfig(
    ambiente=TipoAmbiente.PROD,
    certificado_base64=os.getenv("SIFEN_CERT_B64"),  # ← Base64
    certificado_contrasena=os.getenv("SIFEN_CERT_PASSWORD"),
    csc=os.getenv("SIFEN_CSC"),
    csc_id=os.getenv("SIFEN_CSC_ID")
)
```

### Convertir Archivo a Base64

```bash
# En terminal (Linux/Mac)
base64 certificado.pfx > certificado.b64

# O en una línea
base64 certificado.pfx | tr -d '\n' > certificado.b64
```

```python
# En Python
import base64

# Leer y convertir
with open("certificado.pfx", "rb") as f:
    cert_bytes = f.read()
    cert_b64 = base64.b64encode(cert_bytes).decode('utf-8')

print(cert_b64)  # Copiar a variable de entorno
```

### Desde Base de Datos (TextField)

```python
# Si guardas el certificado como Base64 en DB
from myapp.models import Empresa

empresa = Empresa.objects.get(activo=True)

config = SifenConfig(
    ambiente=TipoAmbiente.PROD,
    certificado_base64=empresa.certificado_base64,  # ← TextField
    certificado_contrasena=empresa.cert_password,
    csc=empresa.csc,
    csc_id=empresa.csc_id
)
```

**Ventajas:**
- ✅ Fácil de almacenar en variables de entorno
- ✅ Compatible con servicios cloud (Heroku, AWS, etc.)
- ✅ Fácil de copiar/pegar
- ✅ No requiere archivos

**Desventajas:**
- ⚠️ String más largo (~33% más que bytes)
- ⚠️ Requiere conversión

---

## 🗄️ Opción 4: Desde Base de Datos

### Django con BinaryField

```python
# models.py
from django.db import models

class ConfiguracionSIFEN(models.Model):
    empresa = models.CharField(max_length=200)
    certificado_pfx = models.BinaryField()  # ← Bytes
    certificado_contrasena = models.CharField(max_length=100)
    csc = models.CharField(max_length=100)
    csc_id = models.CharField(max_length=10)
    activo = models.BooleanField(default=True)

# views.py o service
config_db = ConfiguracionSIFEN.objects.get(activo=True)

config = SifenConfig(
    ambiente=TipoAmbiente.PROD,
    certificado_bytes=config_db.certificado_pfx,
    certificado_contrasena=config_db.certificado_contrasena,
    csc=config_db.csc,
    csc_id=config_db.csc_id
)
```

### Django con TextField (Base64)

```python
# models.py
class ConfiguracionSIFEN(models.Model):
    certificado_base64 = models.TextField()  # ← Base64

# views.py
config = SifenConfig(
    ambiente=TipoAmbiente.PROD,
    certificado_base64=config_db.certificado_base64,
    certificado_contrasena=config_db.certificado_contrasena,
    csc=config_db.csc,
    csc_id=config_db.csc_id
)
```

### PostgreSQL con bytea

```python
import psycopg2

# Consultar DB
conn = psycopg2.connect("dbname=mydb user=myuser")
cur = conn.cursor()
cur.execute("SELECT certificado_pfx, password FROM configuracion WHERE activo = true")
cert_bytes, password = cur.fetchone()

config = SifenConfig(
    ambiente=TipoAmbiente.PROD,
    certificado_bytes=cert_bytes,
    certificado_contrasena=password,
    csc="...",
    csc_id="0001"
)
```

**Ventajas:**
- ✅ Centralizado en base de datos
- ✅ Fácil de actualizar
- ✅ Multi-empresa
- ✅ Auditable

**Desventajas:**
- ⚠️ Requiere base de datos
- ⚠️ Cuidado con backups (datos sensibles)

---

## 🌍 Opción 5: Variables de Entorno

### .env File (Desarrollo)

```bash
# .env
SIFEN_AMBIENTE=PROD
SIFEN_CERT_PATH=/path/to/cert.pfx
SIFEN_CERT_PASSWORD=mi_password
SIFEN_CSC=ABCD1234567890...
SIFEN_CSC_ID=0001

# O con Base64
SIFEN_CERT_B64=MIIKpAIBAzCCCl4GCSqGSIb3DQEHAaCCCk8...
```

```python
# Usar python-dotenv
from dotenv import load_dotenv
import os

load_dotenv()

config = SifenConfig.from_env()  # ← Método helper
```

### Heroku Config Vars

```bash
# Configurar en Heroku
heroku config:set SIFEN_CERT_B64="MIIKpAIBAzCCCl4..."
heroku config:set SIFEN_CERT_PASSWORD="password"
heroku config:set SIFEN_CSC="ABCD1234..."
heroku config:set SIFEN_CSC_ID="0001"
```

```python
# En la app
config = SifenConfig(
    ambiente=TipoAmbiente.PROD,
    certificado_base64=os.getenv("SIFEN_CERT_B64"),
    certificado_contrasena=os.getenv("SIFEN_CERT_PASSWORD"),
    csc=os.getenv("SIFEN_CSC"),
    csc_id=os.getenv("SIFEN_CSC_ID")
)
```

**Ventajas:**
- ✅ No commitear secretos
- ✅ Fácil de cambiar por ambiente
- ✅ Compatible con 12-factor app

**Desventajas:**
- ⚠️ Límite de tamaño en algunos servicios
- ⚠️ Visible en logs si no se tiene cuidado

---

## ☁️ Opción 6: Secrets Manager (AWS, Azure, GCP)

### AWS Secrets Manager

```python
import boto3
import json
import base64

# Cliente de Secrets Manager
client = boto3.client('secretsmanager', region_name='us-east-1')

# Obtener secreto
response = client.get_secret_value(SecretId='sifen/prod/certificado')
secret = json.loads(response['SecretString'])

config = SifenConfig(
    ambiente=TipoAmbiente.PROD,
    certificado_base64=secret['certificado_base64'],
    certificado_contrasena=secret['password'],
    csc=secret['csc'],
    csc_id=secret['csc_id']
)
```

### Azure Key Vault

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import base64

# Cliente de Key Vault
credential = DefaultAzureCredential()
client = SecretClient(
    vault_url="https://mi-keyvault.vault.azure.net/",
    credential=credential
)

# Obtener secretos
cert_b64 = client.get_secret("sifen-certificado").value
password = client.get_secret("sifen-password").value

config = SifenConfig(
    ambiente=TipoAmbiente.PROD,
    certificado_base64=cert_b64,
    certificado_contrasena=password,
    csc=client.get_secret("sifen-csc").value,
    csc_id=client.get_secret("sifen-csc-id").value
)
```

### Google Cloud Secret Manager

```python
from google.cloud import secretmanager
import base64

# Cliente de Secret Manager
client = secretmanager.SecretManagerServiceClient()

# Obtener secreto
name = "projects/my-project/secrets/sifen-certificado/versions/latest"
response = client.access_secret_version(request={"name": name})
cert_b64 = response.payload.data.decode('UTF-8')

config = SifenConfig(
    ambiente=TipoAmbiente.PROD,
    certificado_base64=cert_b64,
    certificado_contrasena="...",
    csc="...",
    csc_id="0001"
)
```

**Ventajas:**
- ✅ Máxima seguridad
- ✅ Rotación automática
- ✅ Auditoría completa
- ✅ Encriptación en reposo

**Desventajas:**
- ⚠️ Requiere configuración cloud
- ⚠️ Costo adicional
- ⚠️ Más complejo

---

## 🎯 Mejores Prácticas

### 1. **Nunca Commitear Certificados**

```bash
# .gitignore
*.pfx
*.p12
*.pem
*.key
certs/
certificados/
.env
```

### 2. **Usar Diferentes Certificados por Ambiente**

```python
import os

ambiente = os.getenv("ENVIRONMENT", "dev")

if ambiente == "prod":
    config = SifenConfig(
        ambiente=TipoAmbiente.PROD,
        certificado_base64=os.getenv("SIFEN_CERT_PROD_B64"),
        certificado_contrasena=os.getenv("SIFEN_CERT_PROD_PASSWORD"),
        csc=os.getenv("SIFEN_CSC_PROD"),
        csc_id=os.getenv("SIFEN_CSC_ID_PROD")
    )
else:
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="certs/dev.pfx",
        certificado_contrasena="dev_password",
        csc="DEV_CSC",
        csc_id="0001"
    )
```

### 3. **Validar Certificado al Inicio**

```python
from sifen.crypto import validate_certificate

try:
    config = SifenConfig(...)
    
    # Validar certificado
    cert_info = validate_certificate(
        config.get_certificado_bytes(),
        config.certificado_contrasena
    )
    
    print(f"✓ Certificado válido hasta: {cert_info['valid_to']}")
    
except Exception as e:
    print(f"✗ Error con certificado: {e}")
    # Notificar, logear, etc.
```

### 4. **Caché de Configuración**

```python
# Evitar leer DB/Secrets en cada request
from functools import lru_cache

@lru_cache(maxsize=1)
def get_sifen_config():
    """Obtiene configuración (con caché)."""
    config_db = ConfiguracionSIFEN.objects.get(activo=True)
    
    return SifenConfig(
        ambiente=TipoAmbiente.PROD,
        certificado_bytes=config_db.certificado_pfx,
        certificado_contrasena=config_db.certificado_contrasena,
        csc=config_db.csc,
        csc_id=config_db.csc_id
    )

# Usar
config = get_sifen_config()
```

---

## 🔒 Seguridad

### ✅ Hacer

- ✅ Usar secrets manager en producción
- ✅ Encriptar contraseñas en base de datos
- ✅ Rotar certificados regularmente
- ✅ Limitar acceso a certificados
- ✅ Auditar uso de certificados
- ✅ Usar HTTPS para transmisión
- ✅ Validar certificado antes de usar

### ❌ No Hacer

- ❌ Commitear certificados en Git
- ❌ Hardcodear contraseñas
- ❌ Compartir certificados por email
- ❌ Usar mismo certificado dev/prod
- ❌ Logear certificados completos
- ❌ Almacenar sin encriptar
- ❌ Usar certificados vencidos

---

## 📊 Comparación de Opciones

| Opción | Desarrollo | Producción | Docker | Serverless | Multi-empresa |
|--------|------------|------------|--------|------------|---------------|
| **Archivo** | ✅ Excelente | ⚠️ Aceptable | ❌ Difícil | ❌ No | ❌ No |
| **Bytes (DB)** | ⚠️ Aceptable | ✅ Excelente | ✅ Excelente | ✅ Excelente | ✅ Excelente |
| **Base64 (Env)** | ✅ Excelente | ✅ Excelente | ✅ Excelente | ✅ Excelente | ⚠️ Limitado |
| **Secrets Manager** | ❌ Complejo | ✅ Excelente | ✅ Excelente | ✅ Excelente | ✅ Excelente |

---

## 🚀 Recomendaciones por Escenario

### Desarrollo Local
```python
# Opción 1: Archivo
config = SifenConfig(
    certificado_archivo="certs/dev.pfx",
    certificado_contrasena="dev_password",
    ...
)
```

### Producción (Servidor Tradicional)
```python
# Opción 2: Base de datos
config = SifenConfig(
    certificado_bytes=config_db.certificado_pfx,
    certificado_contrasena=decrypt(config_db.encrypted_password),
    ...
)
```

### Producción (Docker/Kubernetes)
```python
# Opción 3: Variables de entorno (Base64)
config = SifenConfig(
    certificado_base64=os.getenv("SIFEN_CERT_B64"),
    certificado_contrasena=os.getenv("SIFEN_CERT_PASSWORD"),
    ...
)
```

### Producción (Cloud/Serverless)
```python
# Opción 4: Secrets Manager
config = SifenConfig(
    certificado_base64=get_secret("sifen/cert"),
    certificado_contrasena=get_secret("sifen/password"),
    ...
)
```

---

## 📚 Referencias

- [Documentación SIFEN](https://ekuatia.set.gov.py/portal/ekuatia)
- [PKCS#12 Format](https://en.wikipedia.org/wiki/PKCS_12)
- [12-Factor App - Config](https://12factor.net/config)
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)
- [Azure Key Vault](https://azure.microsoft.com/en-us/services/key-vault/)
- [Google Secret Manager](https://cloud.google.com/secret-manager)

---

**Última actualización:** Mayo 2024  
**Versión:** 1.0.0
