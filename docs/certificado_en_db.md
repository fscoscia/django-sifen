# Almacenar Certificado en Base de Datos

## ¿Por qué almacenar el certificado en la DB?

En entornos de producción, especialmente con múltiples servidores o contenedores, almacenar el certificado en la base de datos tiene ventajas:

✅ **No depende del filesystem** del servidor  
✅ **Fácil de gestionar** desde el admin de Django  
✅ **Múltiples configuraciones** (diferentes sucursales, empresas)  
✅ **Backup automático** con el resto de la DB  
✅ **Escalable** en arquitecturas cloud/Kubernetes  

## Cómo funciona

La librería soporta **3 formas** de proveer el certificado:

### 1. Desde archivo (tradicional)
```python
from sifen import SifenConfig, TipoAmbiente

config = SifenConfig(
    ambiente=TipoAmbiente.PROD,
    certificado_archivo="/path/to/certificado.pfx",  # Ruta al archivo
    certificado_contrasena="password",
    csc="...",
    csc_id="0001",
)
```

### 2. Desde base64 (variable de entorno)
```python
import os

config = SifenConfig(
    ambiente=TipoAmbiente.PROD,
    certificado_base64=os.getenv('SIFEN_CERT_BASE64'),  # Base64 del certificado
    certificado_contrasena=os.getenv('SIFEN_CERT_PASSWORD'),
    csc=os.getenv('SIFEN_CSC'),
    csc_id=os.getenv('SIFEN_CSC_ID'),
)
```

### 3. Desde bytes (base de datos) ⭐ Recomendado
```python
from sifen_django.models import ConfiguracionSIFEN

# Obtener configuración desde la DB
config_db = ConfiguracionSIFEN.get_activa()

# Convertir a SifenConfig
config = config_db.to_sifen_config()

# Usar normalmente
from sifen import SifenClient
SifenClient.set_config(config)
```

## Uso con Django

### 1. Migrar los modelos

```bash
python manage.py makemigrations sifen_django
python manage.py migrate
```

### 2. Subir el certificado desde el admin

1. Ir al admin de Django: `/admin/`
2. Ir a "Configuraciones SIFEN"
3. Clic en "Agregar Configuración SIFEN"
4. Llenar el formulario:
   - **Nombre**: "Principal" (o el que prefieras)
   - **Ambiente**: Desarrollo o Producción
   - **Certificado PFX**: Subir el archivo `.pfx`
   - **Contraseña**: Contraseña del certificado
   - **CSC**: Tu código de seguridad
   - **CSC ID**: ID del CSC
   - **Activo**: ✓ (marcar como activo)

### 3. Usar en tu código

```python
# En tu vista, API, o donde necesites
from sifen import SifenClient
from sifen_django.models import ConfiguracionSIFEN

def mi_vista(request):
    # Obtener configuración activa desde la DB
    config_db = ConfiguracionSIFEN.get_activa()
    
    if not config_db:
        return JsonResponse({'error': 'No hay configuración SIFEN activa'}, status=500)
    
    # Convertir a SifenConfig
    config = config_db.to_sifen_config()
    
    # Establecer configuración
    SifenClient.set_config(config)
    
    # Ahora puedes usar SifenClient normalmente
    # ... tu lógica aquí
```

### 4. Configuración automática en settings.py

```python
# settings.py

# Al iniciar Django, cargar configuración desde DB
def setup_sifen():
    from sifen import SifenClient
    from sifen_django.models import ConfiguracionSIFEN
    
    try:
        config_db = ConfiguracionSIFEN.get_activa()
        if config_db:
            config = config_db.to_sifen_config()
            SifenClient.set_config(config)
    except Exception as e:
        print(f"No se pudo cargar configuración SIFEN: {e}")

# Llamar al iniciar
setup_sifen()
```

## Subir certificado programáticamente

```python
from sifen_django.models import ConfiguracionSIFEN

# Leer el archivo PFX
with open('/path/to/certificado.pfx', 'rb') as f:
    cert_bytes = f.read()

# Crear configuración en la DB
config = ConfiguracionSIFEN.objects.create(
    nombre='Principal',
    ambiente='PROD',
    certificado_pfx=cert_bytes,  # Bytes del certificado
    certificado_contrasena='mi_password',
    csc='ABCD0000000000000000000000000000',
    csc_id='0001',
    habilitar_nota_tecnica_13=True,
    activo=True,
)

print(f"Configuración creada: {config}")
```

## Múltiples configuraciones

Puedes tener múltiples configuraciones (ej: diferentes sucursales):

```python
# Configuración para sucursal 1
config_suc1 = ConfiguracionSIFEN.objects.get(nombre='Sucursal 1')
config1 = config_suc1.to_sifen_config()

# Configuración para sucursal 2
config_suc2 = ConfiguracionSIFEN.objects.get(nombre='Sucursal 2')
config2 = config_suc2.to_sifen_config()

# Usar según necesites
SifenClient.set_config(config1)  # Para sucursal 1
# ... hacer operaciones

SifenClient.set_config(config2)  # Para sucursal 2
# ... hacer operaciones
```

## Seguridad

⚠️ **IMPORTANTE**: La contraseña del certificado se almacena en texto plano en la DB.

Para mayor seguridad, puedes:

### Opción 1: Encriptar la contraseña

```python
from django.conf import settings
from cryptography.fernet import Fernet

class ConfiguracionSIFEN(models.Model):
    # ... otros campos
    
    certificado_contrasena_encriptada = models.BinaryField()
    
    def set_contrasena(self, password):
        """Encripta y guarda la contraseña."""
        f = Fernet(settings.SIFEN_ENCRYPTION_KEY)
        self.certificado_contrasena_encriptada = f.encrypt(password.encode())
    
    def get_contrasena(self):
        """Desencripta y retorna la contraseña."""
        f = Fernet(settings.SIFEN_ENCRYPTION_KEY)
        return f.decrypt(self.certificado_contrasena_encriptada).decode()
```

### Opción 2: Usar variables de entorno para la contraseña

```python
# Guardar solo el certificado en la DB
# La contraseña viene de variable de entorno

import os

class ConfiguracionSIFEN(models.Model):
    # ... sin campo de contraseña
    
    def to_sifen_config(self):
        return SifenConfig(
            ambiente=TipoAmbiente[self.ambiente],
            certificado_bytes=bytes(self.certificado_pfx),
            certificado_contrasena=os.getenv('SIFEN_CERT_PASSWORD'),  # Desde env
            csc=self.csc,
            csc_id=self.csc_id,
        )
```

## Comparación de enfoques

| Enfoque | Ventajas | Desventajas |
|---------|----------|-------------|
| **Archivo en servidor** | Simple, tradicional | Difícil en cloud/containers |
| **Base64 en env** | Portable, sin filesystem | Difícil de gestionar |
| **Base de datos** ⭐ | Fácil gestión, escalable | Requiere cuidado con seguridad |

## Recomendación

Para **producción moderna** (Docker, Kubernetes, cloud):
- ✅ Usar **base de datos** para el certificado
- ✅ Usar **variables de entorno** para la contraseña
- ✅ Encriptar la contraseña si es posible
- ✅ Hacer backup regular de la DB

Para **desarrollo local**:
- ✅ Usar **archivo** directamente
- ✅ Más simple y rápido
