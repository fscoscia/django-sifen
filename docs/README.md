# Documentación django-sifen

Bienvenido a la documentación técnica de **django-sifen**, la librería Python para Facturación Electrónica de Paraguay.

## 📚 Guías Disponibles

### 🧪 [Testing y Verificación](TESTING.md)
Guía completa sobre cómo probar que todo funciona correctamente.

**Contenido:**
- Tests rápidos por componente
- Tests de integración completos
- Configuración del ambiente de desarrollo SIFEN
- Tests automatizados con pytest
- Troubleshooting de problemas comunes
- Script de verificación automática

**Útil para:**
- Verificar instalación correcta
- Probar antes de producción
- Debugging de problemas
- Configurar CI/CD
- Validar cambios

### 🔐 [Manejo de Certificados](CERTIFICADOS.md)
Guía completa sobre todas las formas de configurar y usar certificados digitales.

**Contenido:**
- 6 opciones para proveer certificados (archivo, bytes, Base64, DB, env vars, secrets manager)
- Ejemplos prácticos para cada opción
- Integración con AWS, Azure, GCP
- Mejores prácticas de seguridad
- Comparación de opciones por escenario

**Útil para:**
- Configurar certificados en diferentes ambientes
- Migrar de desarrollo a producción
- Implementar rotación de certificados
- Integrar con servicios cloud
- Manejar multi-empresa

### 🏗️ [Estructura XML](ESTRUCTURA_XML.md)
Documentación completa sobre la estructura XML de documentos electrónicos SIFEN.

**Contenido:**
- Estructura general del XML
- Grupos principales (gTimb, gEmis, gDatRec, gCamItem, etc.)
- Dónde modificar según cambios de SIFEN
- Ejemplos de cambios comunes
- Mejores prácticas de mantenimiento

**Útil para:**
- Entender cómo se genera el XML
- Saber dónde modificar cuando SIFEN actualice el formato
- Agregar nuevos campos o grupos
- Mantener la librería actualizada

---

## 🎯 Guías por Tema

### Para Desarrolladores

#### Primeros Pasos
1. Leer el [README principal](../README.md)
2. Revisar [ejemplos básicos](../examples/ejemplo_basico.py)
3. Entender la [estructura XML](ESTRUCTURA_XML.md)

#### Mantenimiento
1. [Estructura XML](ESTRUCTURA_XML.md) - Cómo modificar la generación XML
2. Revisar código en `sifen/xml/generator.py` con comentarios estructurados
3. Consultar ejemplos en `examples/`

#### Testing
```bash
# Ejecutar tests
pytest tests/

# Con coverage
pytest --cov=sifen tests/
```

---

## 📖 Documentación Oficial SIFEN

### Enlaces Importantes

- **Portal e-Kuatia:** https://ekuatia.set.gov.py/portal/ekuatia
- **Manual Técnico v150:** [PDF](https://ekuatia.set.gov.py/portal/ekuatia/detail?content-id=/repository/collaboration/sites/ekuatia/documents/documentacion/documentacion-tecnica/manual-tecnico-de-kuatia-version-150.pdf)
- **Nota Técnica 13:** [PDF](https://ekuatia.set.gov.py/portal/ekuatia/detail?content-id=/repository/collaboration/sites/ekuatia/documents/documentacion/documentacion-tecnica/NT_E_KUATIA_013_MT_V150.pdf)
- **Documentación Técnica:** https://ekuatia.set.gov.py/portal/ekuatia/documentos.html

---

## 🔧 Arquitectura de la Librería

```
django-sifen/
├── sifen/                      # Core (sin Django)
│   ├── client.py              # Cliente principal
│   ├── config.py              # Configuración
│   ├── constants.py           # Constantes y URLs
│   ├── exceptions.py          # Excepciones
│   │
│   ├── models/                # Modelos de datos
│   │   ├── documento.py       # DocumentoElectronico
│   │   ├── emisor.py          # Emisor
│   │   ├── receptor.py        # Receptor
│   │   ├── items.py           # Items y IVA
│   │   ├── totales.py         # Totales
│   │   └── eventos.py         # Eventos
│   │
│   ├── xml/                   # Generación XML
│   │   ├── generator.py       # Generador principal ← COMENTADO
│   │   └── generator_evento.py
│   │
│   ├── crypto/                # Firma digital
│   │   ├── signature.py       # Firma XML
│   │   ├── validator.py       # Validación firmas
│   │   └── keystore.py        # Certificados
│   │
│   ├── services/              # Servicios SIFEN
│   │   ├── base.py            # Base SOAP
│   │   ├── recepcion_de.py    # Envío DE
│   │   ├── consulta_de.py     # Consulta DE
│   │   ├── consulta_ruc.py    # Consulta RUC
│   │   ├── recepcion_lote.py  # Envío lote
│   │   ├── consulta_lote.py   # Consulta lote
│   │   └── recepcion_evento.py # Eventos
│   │
│   └── utils/                 # Utilidades
│       ├── validators.py      # Validadores
│       ├── calculators.py     # Calculadoras ← NT-13
│       └── formatters.py      # Formateadores
│
├── django_sifen_api/          # Django (opcional)
│   ├── models.py              # Modelos Django
│   ├── views.py               # API REST
│   ├── serializers.py         # Serializers
│   ├── admin.py               # Admin
│   └── urls.py                # URLs
│
├── examples/                  # Ejemplos
│   ├── ejemplo_basico.py
│   ├── ejemplo_nota_tecnica_13.py
│   ├── ejemplo_validacion_firmas.py
│   └── ejemplo_compresion_lote.py
│
└── docs/                      # Documentación
    ├── README.md              # Este archivo
    └── ESTRUCTURA_XML.md      # Estructura XML
```

---

## 🚀 Flujo de Trabajo

### 1. Crear Documento
```python
from sifen import SifenClient, SifenConfig
from sifen.models import DocumentoElectronico, Emisor, Receptor, Item

# Configurar
config = SifenConfig.from_env()
client = SifenClient(config)

# Crear documento
documento = DocumentoElectronico(...)
```

### 2. Generar XML
```python
# Internamente el cliente:
# 1. Valida el documento
# 2. Genera CDC
# 3. Genera XML (sifen/xml/generator.py)
# 4. Firma XML (sifen/crypto/signature.py)
# 5. Envía a SIFEN (sifen/services/recepcion_de.py)
```

### 3. Enviar a SIFEN
```python
respuesta = client.enviar_documento(documento)

if respuesta.aprobado:
    print(f"CDC: {respuesta.cdc}")
else:
    print(f"Error: {respuesta.mensaje}")
```

---

## 📝 Preguntas Frecuentes

### ¿Dónde modifico si SIFEN cambia el XML?

Consulta la guía [Estructura XML](ESTRUCTURA_XML.md), sección "Dónde Modificar".

### ¿Cómo agrego un nuevo campo?

1. Agregar al modelo en `sifen/models/`
2. Agregar al generador en `sifen/xml/generator.py`
3. Ver ejemplos en [Estructura XML](ESTRUCTURA_XML.md)

### ¿Cómo funciona la Nota Técnica 13?

Ver:
- Documentación: [ejemplo_nota_tecnica_13.py](../examples/ejemplo_nota_tecnica_13.py)
- Código: `sifen/utils/calculators.py::calcular_base_exenta_nt13()`

### ¿Puedo usar la librería sin Django?

Sí, el core (`sifen/`) funciona independientemente. Django es opcional.

---

## 🤝 Contribuir

### Reportar Issues
- Usar GitHub Issues
- Incluir versión de Python y Django
- Proporcionar ejemplo reproducible

### Pull Requests
1. Fork del repositorio
2. Crear branch feature
3. Agregar tests
4. Actualizar documentación
5. Crear PR

---

## 📄 Licencia

MIT License - Ver [LICENSE](../LICENSE) para más detalles.

---

**Última actualización:** Mayo 2024  
**Versión:** 1.0.0  
**Versión SIFEN soportada:** 150
