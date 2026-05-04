# Django SIFEN API

Aplicación Django con API REST para gestionar documentos electrónicos de SIFEN.

## Instalación

### 1. Agregar a INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'django_sifen_api',
]
```

### 2. Configurar REST Framework

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}
```

### 3. Incluir URLs

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    # ...
    path('', include('django_sifen_api.urls')),
]
```

### 4. Migrar base de datos

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear superusuario

```bash
python manage.py createsuperuser
```

## Uso

### Configurar SIFEN

1. Ir al admin de Django: `http://localhost:8000/admin/`
2. Crear una configuración SIFEN:
   - Empresa
   - RUC
   - Ambiente (DEV/PROD)
   - Certificado PFX
   - Contraseña del certificado
   - CSC y CSC ID
3. Marcar como "Activo"

### API Endpoints

#### Documentos Electrónicos

**Crear y enviar documento:**
```bash
POST /api/documentos/
Content-Type: application/json

{
  "tipo_documento": 1,
  "numero_timbrado": 12345678,
  "establecimiento": "001",
  "punto_expedicion": "001",
  "numero_documento": "0000001",
  "codigo_seguridad": "123456789",
  "emisor": {
    "ruc": "80012345",
    "dv": 6,
    "nombre": "Empresa S.A.",
    "direccion": "Av. Principal 123",
    "departamento": 1,
    "distrito": 1,
    "ciudad": 1,
    "telefono": "021-123456",
    "email": "contacto@empresa.com.py",
    "actividades_economicas": [{
      "codigo": "47111",
      "descripcion": "Venta al por menor"
    }]
  },
  "receptor": {
    "naturaleza": 1,
    "tipo_operacion": 1,
    "nombre": "Cliente S.R.L."
  },
  "items": [{
    "codigo": "PROD001",
    "descripcion": "Producto de Prueba",
    "unidad_medida": 77,
    "cantidad": 10,
    "precio_unitario": 100000,
    "tasa_iva": 10
  }],
  "condicion_operacion": 1,
  "pagos": [{
    "tipo_pago": 1,
    "monto": 1100000
  }]
}
```

**Listar documentos:**
```bash
GET /api/documentos/
GET /api/documentos/?estado=aprobado
GET /api/documentos/?emisor_ruc=80012345-6
GET /api/documentos/?fecha_desde=2024-01-01&fecha_hasta=2024-12-31
```

**Consultar estado:**
```bash
POST /api/documentos/{cdc}/consultar/
```

**Obtener XML:**
```bash
GET /api/documentos/{cdc}/xml/
```

#### Consulta de RUC

```bash
GET /api/consultas/ruc/consultar/?ruc=80012345&dv=6
```

#### Validaciones

**Validar RUC:**
```bash
POST /api/validaciones/validar_ruc/
{
  "ruc": "80012345",
  "dv": "6"
}
```

**Calcular DV:**
```bash
POST /api/validaciones/calcular_dv/
{
  "ruc": "80012345"
}
```

**Validar CDC:**
```bash
POST /api/validaciones/validar_cdc/
{
  "cdc": "01001001000000112024050412300080012345601"
}
```

## Admin de Django

El admin incluye:

- **Configuraciones SIFEN**: Gestionar certificados y credenciales
- **Documentos Electrónicos**: Ver, filtrar y consultar documentos
- **Logs SIFEN**: Auditoría de comunicaciones

### Acciones disponibles:

- Consultar estado en SIFEN
- Ver logs de un documento
- Activar/desactivar configuraciones

## Modelos

### ConfiguracionSIFEN
Almacena certificados y credenciales por empresa.

### DocumentoElectronico
Registro de documentos enviados a SIFEN.

### LogSIFEN
Auditoría de todas las comunicaciones con SIFEN.

## Autenticación

La API usa autenticación por token. Para obtener un token:

```bash
POST /api-token-auth/
{
  "username": "usuario",
  "password": "contraseña"
}
```

Luego usar el token en las peticiones:

```bash
Authorization: Token <token>
```

## Ejemplo con Python

```python
import requests

# Obtener token
response = requests.post('http://localhost:8000/api-token-auth/', {
    'username': 'admin',
    'password': 'admin'
})
token = response.json()['token']

# Crear documento
headers = {'Authorization': f'Token {token}'}
documento = {
    'tipo_documento': 1,
    # ... datos del documento
}

response = requests.post(
    'http://localhost:8000/api/documentos/',
    json=documento,
    headers=headers
)

print(response.json())
```

## Ejemplo con JavaScript

```javascript
// Obtener token
const response = await fetch('http://localhost:8000/api-token-auth/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    username: 'admin',
    password: 'admin'
  })
});
const {token} = await response.json();

// Crear documento
const documento = {
  tipo_documento: 1,
  // ... datos del documento
};

const result = await fetch('http://localhost:8000/api/documentos/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Token ${token}`
  },
  body: JSON.stringify(documento)
});

console.log(await result.json());
```

## Permisos

Por defecto, todos los endpoints requieren autenticación. Puedes personalizar los permisos en `views.py`.

## Filtros

Los documentos pueden filtrarse por:
- Estado
- Tipo de documento
- RUC emisor
- RUC receptor
- Rango de fechas

## Paginación

Los resultados están paginados (50 por página por defecto).

```bash
GET /api/documentos/?page=2
```

## Soporte

Para más información, consulta la documentación de la librería `django-sifen`.
