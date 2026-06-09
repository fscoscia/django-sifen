# ¿Qué es el CDC y cómo obtenerlo?

## 📋 ¿Qué es el CDC?

El **CDC (Código de Control)** es un identificador único de 44 caracteres que SIFEN asigna a cada documento electrónico aprobado.

### Estructura del CDC (44 caracteres)

```
01 800695115 001 001 0000001 2024 12 06 1 3 3709 00001
│  │         │   │   │       │    │  │  │ │ │    │
│  │         │   │   │       │    │  │  │ │ │    └─ Número de documento (5 dígitos)
│  │         │   │   │       │    │  │  │ │ └────── Código de seguridad (4 dígitos)
│  │         │   │   │       │    │  │  │ └──────── Tipo de emisión (1 dígito)
│  │         │   │   │       │    │  │  └────────── Tipo de documento (1 dígito)
│  │         │   │   │       │    │  └───────────── Día (2 dígitos)
│  │         │   │   │       │    └──────────────── Mes (2 dígitos)
│  │         │   │   │       └───────────────────── Año (4 dígitos)
│  │         │   │   └───────────────────────────── Número correlativo (7 dígitos)
│  │         │   └───────────────────────────────── Punto de expedición (3 dígitos)
│  │         └───────────────────────────────────── Establecimiento (3 dígitos)
│  └─────────────────────────────────────────────── RUC del emisor (8-9 dígitos)
└────────────────────────────────────────────────── Dígito verificador (2 dígitos)
```

**Ejemplo de CDC válido:**
```
01800695115001001000000120241206133709000001
│                                              │
└──────────────── 44 caracteres ───────────────┘
```

---

## 🔍 ¿Cómo obtener un CDC?

### Opción 1: Desde la Respuesta de SIFEN

Cuando emites un documento, SIFEN te devuelve el CDC en la respuesta:

```python
from sifen import SifenClient

client = SifenClient(config)

# Emitir documento
respuesta = client.enviar_documento_electronico(de)

if respuesta.aprobado:
    cdc = respuesta.cdc  # ← Aquí está el CDC
    print(f"CDC: {cdc}")
    print(f"Longitud: {len(cdc)} caracteres")
```

### Opción 2: Desde tu Base de Datos

Si guardas los documentos emitidos:

```python
from sifen_django.models import DocumentoElectronicoModel

# Buscar documento
documento = DocumentoElectronicoModel.objects.get(id=123)
cdc = documento.cdc

print(f"CDC: {cdc}")
```

### Opción 3: Emitir un Documento de Prueba

Para probar eventos, primero emite un documento:

```bash
# Ejecutar flujo completo de factura
cd django-sifen
python examples/flujo_completo_factura.py
```

Al final del proceso verás:
```
✓ Documento aprobado
  CDC: 01800695115001001000000120241206133709000001
  Protocolo: ABC123456789
```

**Copia ese CDC** para usarlo en las pruebas de eventos.

---

## ⚠️ Errores Comunes

### Error: "El CDC debe tener 44 caracteres"

**Causa**: El CDC no tiene exactamente 44 caracteres.

**Solución**:
```python
cdc = "01800695115001001000000120241206133709000001"
print(f"Longitud: {len(cdc)}")  # Debe mostrar: 44

# ✗ INCORRECTO (41 caracteres)
cdc = "01001001000000112024050412300080012345601"

# ✓ CORRECTO (44 caracteres)
cdc = "01800695115001001000000120241206133709000001"
```

### Error: "Documento no existe"

**Causa**: El CDC no existe en SIFEN o es inválido.

**Solución**:
- Verifica que el documento fue aprobado
- Usa el CDC exacto que te devolvió SIFEN
- Asegúrate de estar en el mismo ambiente (DEV/PROD)

### Error: "Evento fuera de plazo"

**Causa**: El documento tiene más de 48 horas de aprobado.

**Solución**:
- Emite un nuevo documento
- Usa el CDC de ese documento recién emitido

---

## 🧪 Cómo Probar Eventos con un CDC Real

### Paso 1: Emitir un Documento

```bash
python examples/flujo_completo_factura.py
```

Salida:
```
✓ Documento aprobado
  CDC: 01800695115001001000000120241206133709000001  ← COPIAR ESTO
  Protocolo: ABC123
```

### Paso 2: Copiar el CDC

Copia el CDC completo (44 caracteres).

### Paso 3: Actualizar el Script de Prueba

Edita `examples/test_eventos.py`:

```python
# Línea 43 - Reemplaza con tu CDC real
cdc = "01800695115001001000000120241206133709000001"  # ← Pegar aquí
```

### Paso 4: Ejecutar Prueba de Cancelación

```bash
python examples/test_eventos.py
# Seleccionar opción 1: Cancelación
```

---

## 📝 Validación del CDC

Antes de usar un CDC, valídalo:

```python
def validar_cdc(cdc: str) -> bool:
    """Valida que el CDC tenga el formato correcto."""
    
    # Verificar longitud
    if len(cdc) != 44:
        print(f"✗ Longitud incorrecta: {len(cdc)} (debe ser 44)")
        return False
    
    # Verificar que sea numérico
    if not cdc.isdigit():
        print("✗ El CDC debe contener solo dígitos")
        return False
    
    print(f"✓ CDC válido: {cdc}")
    return True

# Usar
cdc = "01800695115001001000000120241206133709000001"
if validar_cdc(cdc):
    # Proceder con el evento
    respuesta = client.cancelar_documento(cdc, motivo)
```

---

## 🎯 Ejemplo Completo

```python
from sifen import SifenClient
from sifen.config import SifenConfig, TipoAmbiente

# 1. Configurar cliente
config = SifenConfig(
    ambiente=TipoAmbiente.DEV,
    certificado_archivo="/path/to/cert.p12",
    certificado_contrasena="password",
    csc="ABCD0000000000000000000000000000",
    csc_id="0001",
)

client = SifenClient(config)

# 2. Emitir documento (obtener CDC)
# ... código para emitir factura ...
# respuesta = client.enviar_documento_electronico(de)
# cdc = respuesta.cdc

# 3. Usar CDC para evento (dentro de 48 horas)
cdc = "01800695115001001000000120241206133709000001"

# Validar longitud
if len(cdc) == 44:
    # Cancelar documento
    respuesta = client.cancelar_documento(
        cdc=cdc,
        motivo="Error en datos - Se emitirá nuevo documento"
    )
    
    if respuesta.aprobado:
        print(f"✓ Documento cancelado")
        print(f"  Protocolo: {respuesta.numero_protocolo}")
    else:
        print(f"✗ Error: {respuesta.mensaje}")
else:
    print(f"✗ CDC inválido: tiene {len(cdc)} caracteres, debe tener 44")
```

---

## 📚 Referencias

- **Manual Técnico SIFEN v150**: Sección sobre CDC
- **Especificaciones**: Estructura del CDC
- **Ejemplos**: `examples/flujo_completo_*.py`

---

## 💡 Tips

1. **Guarda los CDCs**: Almacena los CDCs de documentos emitidos en tu base de datos
2. **Valida siempre**: Verifica la longitud antes de enviar eventos
3. **Usa documentos recientes**: Para cancelación, usa documentos con menos de 48 horas
4. **Ambiente correcto**: Asegúrate de usar CDCs del mismo ambiente (DEV/PROD)

---

## ❓ Preguntas Frecuentes

**P: ¿Puedo inventar un CDC para pruebas?**
R: No. El CDC debe ser generado por SIFEN al aprobar un documento.

**P: ¿El CDC cambia si reenvío el mismo documento?**
R: Sí. Cada envío genera un CDC único.

**P: ¿Puedo usar un CDC de producción en desarrollo?**
R: No. Los CDCs son específicos del ambiente (DEV o PROD).

**P: ¿Cómo sé si un CDC es válido?**
R: Debe tener 44 caracteres numéricos y existir en SIFEN.
