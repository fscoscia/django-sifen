# Guía Completa para Probar Eventos SIFEN

Esta guía te muestra cómo probar el sistema de eventos paso a paso.

## 📋 Tabla de Contenidos

1. [Preparación](#preparación)
2. [Pruebas sin Conexión](#pruebas-sin-conexión)
3. [Pruebas con SIFEN Test](#pruebas-con-sifen-test)
4. [Flujo Completo de Pruebas](#flujo-completo-de-pruebas)
5. [Solución de Problemas](#solución-de-problemas)

---

## 1. Preparación

### Requisitos Previos

✅ **Certificado Digital**: Necesitas un certificado `.p12` válido para el ambiente de test
✅ **RUC de Prueba**: RUC registrado en el ambiente de test de SIFEN
✅ **Documentos Emitidos**: Para probar eventos, necesitas CDCs de documentos ya emitidos

### Configuración Inicial

```python
from sifen import SifenClient
from sifen.config import SifenConfig, TipoAmbiente

# Configurar para ambiente de TEST
config = SifenConfig(
    ambiente=TipoAmbiente.DEV,
    contribuyente_ruc="TU_RUC_AQUI",
    contribuyente_razon_social="Tu Empresa S.A.",
    cert_path="/ruta/a/tu/certificado.p12",
    cert_password="tu_password",
)

client = SifenClient(config)
```

---

## 2. Pruebas sin Conexión

Estas pruebas NO requieren conexión a SIFEN y son útiles para validar datos.

### 2.1. Validar Modelos de Eventos

```python
from sifen.models.eventos import EventoCancelacion, EventoInutilizacion

# Test 1: Validar cancelación
evento = EventoCancelacion(mOtEve="Motivo de prueba")
is_valid, error = evento.validate()

if is_valid:
    print("✓ Evento válido")
else:
    print(f"✗ Error: {error}")

# Test 2: Validar inutilización
evento_inu = EventoInutilizacion(
    mOtEve="Motivo",
    dNumTim=12345678,
    dEst="001",
    dPunExp="001",
    dNumIn="0000001",
    dNumFin="0000010",
    iTiDE=1,
)
is_valid, error = evento_inu.validate()
print(f"{'✓' if is_valid else '✗'} {error or 'Válido'}")
```

### 2.2. Generar XML sin Enviar

```python
from sifen.xml.generator_evento import XMLEventoGenerator
from sifen.models.eventos import GestionEvento, EventoCancelacion
from datetime import datetime

# Crear evento
evento_canc = EventoCancelacion(mOtEve="Prueba de generación XML")

gestion = GestionEvento(
    Id="EVE20240604123000",
    dFecFirma=datetime.now(),
    iTipEve=1,
    dDesTipEve="Cancelación",
    Id_CDC="0" * 44,  # CDC ficticio
    mOtEve="Prueba",
    gGroupGesEve=evento_canc,
)

# Generar XML
generator = XMLEventoGenerator()
xml_string = generator.generate(gestion)

print("XML generado:")
print(xml_string)

# Guardar para inspección
with open("evento_prueba.xml", "w") as f:
    f.write(xml_string)
```

### 2.3. Ejecutar Script de Validación

```bash
# Ejecutar el script de prueba que creamos
cd django-sifen
python examples/test_eventos.py

# Seleccionar opción 6: Validación de Modelos
```

---

## 3. Pruebas con SIFEN Test

### 3.1. Preparar un Documento para Probar

**Primero necesitas emitir un documento en el ambiente de test:**

```python
# Emitir una factura de prueba
from examples.flujo_completo_factura import main as crear_factura

# Esto te dará un CDC que puedes usar para eventos
cdc = crear_factura()
print(f"CDC para pruebas: {cdc}")
```

### 3.2. Probar Cancelación (Evento 1)

**Requisito**: El documento debe tener menos de 48 horas de aprobado.

```python
from sifen import SifenClient

client = SifenClient(config)

# Usar el CDC del documento que acabas de crear
cdc = "01001001000000112024060412300080012345601"

try:
    respuesta = client.cancelar_documento(
        cdc=cdc,
        motivo="Prueba de cancelación - Error en datos"
    )
    
    if respuesta.aprobado:
        print(f"✓ Documento cancelado")
        print(f"  Protocolo: {respuesta.numero_protocolo}")
        print(f"  Fecha: {respuesta.fecha_recepcion}")
    else:
        print(f"✗ Rechazado: {respuesta.mensaje}")
        
except Exception as e:
    print(f"✗ Error: {str(e)}")
```

### 3.3. Probar Inutilización (Evento 2)

**Requisito**: Los números no deben estar utilizados.

```python
try:
    respuesta = client.inutilizar_numeracion(
        motivo="Prueba de inutilización - Salto de numeración",
        timbrado=12345678,  # Tu timbrado de prueba
        establecimiento="001",
        punto_expedicion="001",
        numero_inicial="0000900",  # Números no utilizados
        numero_final="0000905",
        tipo_documento=1,  # Factura
    )
    
    if respuesta.aprobado:
        print(f"✓ Numeración inutilizada")
        print(f"  Protocolo: {respuesta.numero_protocolo}")
    else:
        print(f"✗ Rechazado: {respuesta.mensaje}")
        
except Exception as e:
    print(f"✗ Error: {str(e)}")
```

### 3.4. Probar Conformidad (Evento 11)

**Requisito**: Documento recibido dentro de los 45 días.

```python
# Como receptor
try:
    respuesta = client.enviar_conformidad(
        cdc="CDC_DE_DOCUMENTO_RECIBIDO"
    )
    
    if respuesta.aprobado:
        print(f"✓ Conformidad registrada")
    else:
        print(f"✗ Rechazado: {respuesta.mensaje}")
        
except Exception as e:
    print(f"✗ Error: {str(e)}")
```

### 3.5. Probar Disconformidad (Evento 12)

```python
try:
    respuesta = client.enviar_disconformidad(
        cdc="CDC_DE_DOCUMENTO_RECIBIDO",
        motivo="Mercadería no coincide con la factura"
    )
    
    if respuesta.aprobado:
        print(f"✓ Disconformidad registrada")
    else:
        print(f"✗ Rechazado: {respuesta.mensaje}")
        
except Exception as e:
    print(f"✗ Error: {str(e)}")
```

---

## 4. Flujo Completo de Pruebas

### Opción A: Script Interactivo

```bash
cd django-sifen
python examples/test_eventos.py
```

El script te mostrará un menú:
```
MENÚ DE PRUEBAS DE EVENTOS SIFEN
================================

Eventos del Emisor:
  1. Cancelación de Documento
  2. Inutilización de Numeración

Eventos del Receptor:
  3. Conformidad
  4. Disconformidad
  5. Desconocimiento

Pruebas sin Envío:
  6. Validación de Modelos (sin envío a SIFEN)

  0. Salir
```

### Opción B: Flujo Programático

```python
# test_flujo_completo.py

from sifen import SifenClient
from sifen.config import SifenConfig, TipoAmbiente

def flujo_completo_emisor():
    """Prueba completa como emisor."""
    
    config = SifenConfig(
        ambiente=TipoAmbiente.TEST,
        contribuyente_ruc="80000001",
        contribuyente_razon_social="Empresa Test",
        cert_path="/path/to/cert.p12",
        cert_password="password",
    )
    
    client = SifenClient(config)
    
    print("=== FLUJO COMPLETO EMISOR ===\n")
    
    # Paso 1: Emitir documento
    print("1. Emitiendo documento de prueba...")
    # ... código para emitir factura ...
    cdc = "CDC_GENERADO"
    print(f"   ✓ Documento emitido: {cdc}\n")
    
    # Paso 2: Cancelar documento
    print("2. Cancelando documento...")
    respuesta = client.cancelar_documento(
        cdc=cdc,
        motivo="Prueba de cancelación"
    )
    
    if respuesta.aprobado:
        print(f"   ✓ Cancelado. Protocolo: {respuesta.numero_protocolo}\n")
    else:
        print(f"   ✗ Error: {respuesta.mensaje}\n")
    
    # Paso 3: Inutilizar numeración
    print("3. Inutilizando numeración...")
    respuesta = client.inutilizar_numeracion(
        motivo="Prueba de inutilización",
        timbrado=12345678,
        establecimiento="001",
        punto_expedicion="001",
        numero_inicial="0000800",
        numero_final="0000810",
        tipo_documento=1,
    )
    
    if respuesta.aprobado:
        print(f"   ✓ Inutilizado. Protocolo: {respuesta.numero_protocolo}\n")
    else:
        print(f"   ✗ Error: {respuesta.mensaje}\n")
    
    print("=== FIN FLUJO EMISOR ===")


def flujo_completo_receptor():
    """Prueba completa como receptor."""
    
    config = SifenConfig(
        ambiente=TipoAmbiente.TEST,
        contribuyente_ruc="80000002",
        contribuyente_razon_social="Receptor Test",
        cert_path="/path/to/cert.p12",
        cert_password="password",
    )
    
    client = SifenClient(config)
    
    print("\n=== FLUJO COMPLETO RECEPTOR ===\n")
    
    # Simular documentos recibidos
    documentos = [
        {"cdc": "CDC1", "accion": "conformidad"},
        {"cdc": "CDC2", "accion": "disconformidad"},
        {"cdc": "CDC3", "accion": "desconocimiento"},
    ]
    
    for doc in documentos:
        cdc = doc["cdc"]
        accion = doc["accion"]
        
        print(f"Procesando {cdc}...")
        
        try:
            if accion == "conformidad":
                respuesta = client.enviar_conformidad(cdc)
            elif accion == "disconformidad":
                respuesta = client.enviar_disconformidad(
                    cdc, "Mercadería incorrecta"
                )
            elif accion == "desconocimiento":
                respuesta = client.enviar_desconocimiento(
                    cdc, "No se recibió"
                )
            
            if respuesta.aprobado:
                print(f"  ✓ {accion.capitalize()} registrada\n")
            else:
                print(f"  ✗ Error: {respuesta.mensaje}\n")
                
        except Exception as e:
            print(f"  ✗ Excepción: {str(e)}\n")
    
    print("=== FIN FLUJO RECEPTOR ===")


if __name__ == "__main__":
    # Ejecutar flujos
    flujo_completo_emisor()
    flujo_completo_receptor()
```

---

## 5. Solución de Problemas

### Error: "Evento fuera de plazo"

**Causa**: El evento se envió después del plazo permitido.

**Solución**:
- Cancelación: Debe enviarse dentro de 48 horas
- Eventos del receptor: Dentro de 45 días
- Inutilización: Dentro de 15 días

### Error: "Documento no existe"

**Causa**: El CDC no existe en SIFEN o es inválido.

**Solución**:
- Verifica que el CDC sea correcto (44 caracteres)
- Asegúrate de que el documento fue aprobado por SIFEN
- Usa documentos del mismo ambiente (test/producción)

### Error: "Evento duplicado"

**Causa**: Ya se envió un evento del mismo tipo para ese documento.

**Solución**:
- No puedes enviar el mismo evento dos veces
- Verifica el historial de eventos del documento

### Error: "Certificado inválido"

**Causa**: Problema con el certificado digital.

**Solución**:
```python
# Verificar certificado
from sifen.crypto import load_certificate

try:
    cert = load_certificate("/path/to/cert.p12", "password")
    print("✓ Certificado válido")
except Exception as e:
    print(f"✗ Error en certificado: {str(e)}")
```

### Error de Validación

**Causa**: Los datos del evento no cumplen las reglas.

**Solución**:
```python
# Validar antes de enviar
evento = EventoCancelacion(mOtEve="Motivo")
is_valid, error = evento.validate()

if not is_valid:
    print(f"Error de validación: {error}")
    # Corregir datos antes de enviar
```

---

## 6. Checklist de Pruebas

### Antes de Probar

- [ ] Certificado digital configurado
- [ ] RUC de prueba registrado en SIFEN Test
- [ ] Ambiente configurado como TEST
- [ ] Documentos de prueba emitidos

### Pruebas Básicas

- [ ] Validación de modelos (sin conexión)
- [ ] Generación de XML
- [ ] Cancelación de documento
- [ ] Inutilización de numeración
- [ ] Conformidad de documento
- [ ] Disconformidad de documento

### Pruebas Avanzadas

- [ ] Envío de lote de eventos
- [ ] Manejo de errores
- [ ] Verificación de respuestas
- [ ] Almacenamiento de protocolos

---

## 7. Comandos Rápidos

```bash
# Validar modelos sin conexión
python examples/test_eventos.py
# Seleccionar opción 6

# Probar cancelación
python -c "
from sifen import SifenClient
from sifen.config import SifenConfig, TipoAmbiente

config = SifenConfig(
    ambiente=TipoAmbiente.DEV,
    contribuyente_ruc='TU_RUC',
    contribuyente_razon_social='Test',
    cert_path='/path/to/cert.p12',
    cert_password='password'
)

client = SifenClient(config)
resp = client.cancelar_documento('CDC_AQUI', 'Motivo de prueba')
print(f'Aprobado: {resp.aprobado}')
print(f'Mensaje: {resp.mensaje}')
"

# Ver ejemplos
cat examples/eventos_emisor.py
cat examples/eventos_receptor.py
```

---

## 8. Recursos Adicionales

- **Documentación**: `docs/EVENTOS.md`
- **Ejemplos**: `examples/eventos_*.py`
- **Script de prueba**: `examples/test_eventos.py`
- **Manual SIFEN**: Manual Técnico v150

---

## 9. Próximos Pasos

1. ✅ Ejecutar validaciones sin conexión
2. ✅ Probar en ambiente TEST
3. ✅ Verificar respuestas de SIFEN
4. ✅ Implementar en tu aplicación
5. ✅ Migrar a producción

---

**¿Necesitas ayuda?**

- Revisa los logs de error
- Consulta la documentación de SIFEN
- Verifica los ejemplos incluidos
- Prueba primero sin conexión
