# Evento de Nominación

## Descripción

El evento de **Nominación** permite asignar el RUC o identidad correcta a una factura que originalmente se emitió a un "innominado" (sin identificación del receptor).

Este evento es útil cuando:
- Se emite una factura de contado sin datos del cliente
- Posteriormente el cliente solicita la factura con sus datos fiscales
- Se necesita asignar el RUC/identidad para que el cliente pueda usar la factura

## Tipo de Evento

- **Código**: 3
- **Nombre**: Nominación
- **Categoría**: Evento del Emisor

## Requisitos

1. El documento debe haber sido emitido originalmente a un "innominado"
2. El documento debe estar aprobado por SIFEN
3. El evento debe enviarse dentro del plazo permitido (verificar con SIFEN)

## Uso Básico

```python
from sifen import SifenClient
from sifen.config import SifenConfig, TipoAmbiente

# Configurar cliente
config = SifenConfig(
    ambiente=TipoAmbiente.DEV,
    certificado_archivo="/ruta/certificado.pfx",
    certificado_contrasena="contraseña",
    csc="ABCD0000000000000000000000000000",
    csc_id="0001",
)

client = SifenClient(config)

# Nominar documento
respuesta = client.nominar_documento(
    cdc="01800695115001001000000012024120613370900001",
    motivo="Cliente identificado posteriormente",
    ruc="80012345",
    dv=6,
    nombre="Juan Pérez"
)

if respuesta.aprobado:
    print(f"✅ Documento nominado - Protocolo: {respuesta.numero_protocolo}")
else:
    print(f"❌ Rechazado: {respuesta.mensaje}")
```

## Parámetros

### Obligatorios

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `cdc` | str | CDC del documento a nominar (44 caracteres) |
| `motivo` | str | Motivo de la nominación (máx 500 caracteres) |
| `ruc` | str | RUC del receptor sin DV (3-8 dígitos) |
| `dv` | int | Dígito verificador del RUC |
| `nombre` | str | Nombre o razón social del receptor (4-60 caracteres) |

### Opcionales

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `naturaleza_receptor` | int | 1 | 1=Contribuyente, 2=No contribuyente |
| `tipo_operacion` | int | 1 | Tipo de operación (1-10) |
| `codigo_pais` | str | "PRY" | Código ISO del país (3 caracteres) |
| `descripcion_pais` | str | "Paraguay" | Descripción del país (4-50 caracteres) |
| `tipo_contribuyente` | int | 1 | 1=Persona física, 2=Persona jurídica |

## Ejemplo Completo

```python
respuesta = client.nominar_documento(
    cdc="01800695115001001000000012024120613370900001",
    motivo="Cliente identificado posteriormente - Venta de contado",
    ruc="80012345",
    dv=6,
    nombre="EMPRESA EJEMPLO S.A.",
    naturaleza_receptor=1,  # Contribuyente
    tipo_operacion=1,  # B2B
    codigo_pais="PRY",
    descripcion_pais="Paraguay",
    tipo_contribuyente=2,  # Persona jurídica
)
```

## Validación Previa

Puedes validar el evento antes de enviarlo:

```python
from sifen.models.eventos import EventoNominacion

evento = EventoNominacion(
    Id="01800695115001001000000012024120613370900001",
    mOtEve="Asignación de receptor",
    iNatRec=1,
    iTiOpe=1,
    cPaisRec="PRY",
    dDesPaisRe="Paraguay",
    iTiContRec=1,
    dRucRec="80012345",
    dDVRec=6,
    dNomRec="Juan Pérez",
)

is_valid, error = evento.validate()
if not is_valid:
    print(f"Error de validación: {error}")
```

## Estructura XML Generada

```xml
<rGesEve xmlns="http://ekuatia.set.gov.py/sifen/xsd">
  <rEve Id="1234567890">
    <dFecFirma>2024-12-06T13:37:09</dFecFirma>
    <dVerFor>150</dVerFor>
    <gGroupTiEvt>
      <rGEveNom>
        <Id>01800695115001001000000012024120613370900001</Id>
        <mOtEve>Cliente identificado posteriormente</mOtEve>
        <iNatRec>1</iNatRec>
        <iTiOpe>1</iTiOpe>
        <cPaisRec>PRY</cPaisRec>
        <dDesPaisRe>Paraguay</dDesPaisRe>
        <iTiContRec>1</iTiContRec>
        <dRucRec>80012345</dRucRec>
        <dDVRec>6</dDVRec>
        <dNomRec>Juan Pérez</dNomRec>
      </rGEveNom>
    </gGroupTiEvt>
  </rEve>
  <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
    <!-- Firma digital -->
  </Signature>
</rGesEve>
```

## Manejo de Errores

```python
from sifen.exceptions import ValidationException, SifenException

try:
    respuesta = client.nominar_documento(
        cdc=cdc_innominado,
        motivo="Asignación de receptor",
        ruc="80012345",
        dv=6,
        nombre="Juan Pérez"
    )
    
    if respuesta.aprobado:
        print("✅ Nominación exitosa")
    else:
        print(f"❌ Rechazado: {respuesta.mensaje}")
        
except ValidationException as e:
    print(f"❌ Error de validación: {e}")
except SifenException as e:
    print(f"❌ Error de SIFEN: {e}")
except Exception as e:
    print(f"❌ Error inesperado: {e}")
```

## Errores Comunes

### 1. CDC Inválido
```
Error: El CDC debe tener 44 caracteres
```
**Solución**: Verifica que el CDC tenga exactamente 44 dígitos.

### 2. RUC Inválido
```
Error: El RUC debe tener entre 3 y 8 dígitos
```
**Solución**: Verifica que el RUC sea válido y no incluya el DV.

### 3. Nombre Muy Corto
```
Error: El nombre del receptor debe tener entre 4 y 60 caracteres
```
**Solución**: El nombre debe tener al menos 4 caracteres.

### 4. Documento No Innominado
```
Error: El documento no fue emitido a innominado
```
**Solución**: Solo se pueden nominar documentos que originalmente fueron emitidos sin datos del receptor.

## Códigos de Respuesta

| Código | Descripción |
|--------|-------------|
| 0600 | Evento aprobado |
| 0601 | Evento rechazado - Documento no encontrado |
| 0602 | Evento rechazado - Documento no es innominado |
| 0603 | Evento rechazado - Fuera de plazo |
| 0604 | Evento rechazado - Datos inválidos |

## Notas Importantes

1. **Plazo**: Verifica con SIFEN el plazo permitido para nominar documentos
2. **Una sola vez**: Un documento solo puede ser nominado una vez
3. **Documento aprobado**: El documento original debe estar aprobado
4. **Validación de RUC**: SIFEN validará que el RUC exista y sea válido
5. **Innominado**: Solo aplica a documentos emitidos originalmente sin datos del receptor

## Ver También

- [Cancelación de Documentos](CANCELACION.md)
- [Inutilización de Numeración](INUTILIZACION.md)
- [Eventos del Receptor](EVENTOS_RECEPTOR.md)
- [Guía de Eventos](EVENTOS.md)

## Ejemplos Adicionales

Para más ejemplos, consulta:
- `examples/ejemplo_nominacion.py` - Ejemplos completos de uso
- `examples/test_eventos.py` - Script de pruebas interactivo
