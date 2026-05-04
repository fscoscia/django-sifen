"""
Ejemplo de validación de firmas digitales y generación de URLs QR.

Demuestra cómo validar XMLs firmados recibidos de SIFEN o terceros,
y cómo generar URLs de consulta QR para documentos electrónicos.
"""

from sifen import SifenClient, SifenConfig, TipoAmbiente


def ejemplo_validar_firma_xml():
    """Ejemplo de validación de firma de un XML."""
    
    print("=" * 70)
    print("Ejemplo: Validación de Firma Digital en XML")
    print("=" * 70)
    
    # XML de ejemplo (firmado)
    xml_firmado = """<?xml version="1.0" encoding="UTF-8"?>
<rDE xmlns="http://ekuatia.set.gov.py/sifen/xsd" Id="DE0000001">
    <dVerFor>150</dVerFor>
    <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
        <!-- Firma digital aquí -->
    </Signature>
</rDE>"""
    
    # Opción 1: Con instancia de cliente
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/path/to/cert.pfx",
        certificado_contrasena="password",
        csc="ABCD1234...",
        csc_id="0001"
    )
    
    client = SifenClient(config)
    
    print("\n1. Validar XML con cliente instanciado:")
    print("   (Comentado - requiere XML firmado válido)")
    print("""
    resultado = client.validar_firma_xml(xml_firmado)
    
    if resultado.is_valid:
        print(f"✓ Firma válida")
        print(f"  Emisor: {resultado.subject}")
        print(f"  Válido desde: {resultado.valid_from}")
        print(f"  Válido hasta: {resultado.valid_to}")
    else:
        print(f"✗ Firma inválida")
        print(f"  Error: {resultado.error}")
    """)
    
    # Opción 2: Método estático (sin configuración)
    print("\n2. Validar XML con método estático:")
    print("   (No requiere instanciar cliente)")
    print("""
    from sifen import SifenClient
    
    resultado = SifenClient.validar_firma_xml_estatico(xml_firmado)
    print(f"Firma válida: {resultado.is_valid}")
    """)


def ejemplo_validar_firma_archivo():
    """Ejemplo de validación de firma de un archivo."""
    
    print("\n\n" + "=" * 70)
    print("Ejemplo: Validación de Firma en Archivo XML")
    print("=" * 70)
    
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/path/to/cert.pfx",
        certificado_contrasena="password",
        csc="ABCD1234...",
        csc_id="0001"
    )
    
    client = SifenClient(config)
    
    print("\nValidar archivo XML firmado:")
    print("(Comentado - requiere archivo válido)")
    print("""
    # Validar archivo descargado de SIFEN
    resultado = client.validar_firma_archivo("/path/to/documento_firmado.xml")
    
    if resultado.is_valid:
        print(f"✓ El archivo tiene una firma válida")
        print(f"  Certificado: {resultado.subject}")
    else:
        print(f"✗ Firma inválida o corrupta")
        print(f"  Razón: {resultado.error}")
    """)


def ejemplo_generar_url_qr():
    """Ejemplo de generación de URL QR."""
    
    print("\n\n" + "=" * 70)
    print("Ejemplo: Generación de URL de Consulta QR")
    print("=" * 70)
    
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/path/to/cert.pfx",
        certificado_contrasena="password",
        csc="ABCD1234...",
        csc_id="0001"
    )
    
    client = SifenClient(config)
    
    # CDC de ejemplo
    cdc = "01001001000000112024050412300080012345601"
    
    # Generar URL
    url_qr = client.generar_url_qr(cdc)
    
    print(f"\nCDC: {cdc}")
    print(f"URL QR: {url_qr}")
    
    print("\n✓ Esta URL puede ser convertida a código QR")
    print("  Los clientes pueden escanear el QR para consultar el documento")


def ejemplo_generar_qr_imagen():
    """Ejemplo de generación de imagen QR."""
    
    print("\n\n" + "=" * 70)
    print("Ejemplo: Generar Imagen QR con qrcode")
    print("=" * 70)
    
    print("""
Para generar una imagen QR, instala la librería qrcode:

    pip install qrcode[pil]

Luego usa:

```python
from sifen import SifenClient
import qrcode

# Configurar cliente
client = SifenClient(config)

# Generar URL
cdc = "01001001000000112024050412300080012345601"
url = client.generar_url_qr(cdc)

# Crear código QR
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(url)
qr.make(fit=True)

# Generar imagen
img = qr.make_image(fill_color="black", back_color="white")
img.save("documento_qr.png")

print("✓ QR generado: documento_qr.png")
```

El cliente puede escanear este QR con su celular para:
- Ver el documento electrónico
- Verificar su autenticidad
- Descargar el XML
- Ver el estado en SIFEN
    """)


def ejemplo_caso_uso_completo():
    """Caso de uso completo: Enviar, validar y generar QR."""
    
    print("\n\n" + "=" * 70)
    print("Caso de Uso Completo")
    print("=" * 70)
    
    print("""
Flujo completo de un documento electrónico:

```python
from sifen import SifenClient, SifenConfig, TipoAmbiente

# 1. Configurar cliente
config = SifenConfig(
    ambiente=TipoAmbiente.PROD,
    certificado_archivo="/path/to/cert.pfx",
    certificado_contrasena="password",
    csc="ABCD1234...",
    csc_id="0001"
)

client = SifenClient(config)

# 2. Crear y enviar documento
documento = crear_documento_electronico()
respuesta = client.enviar_documento(documento)

if respuesta.aprobado:
    cdc = respuesta.cdc
    print(f"✓ Documento aprobado: {cdc}")
    
    # 3. Generar URL QR para el cliente
    url_qr = client.generar_url_qr(cdc)
    print(f"URL QR: {url_qr}")
    
    # 4. Generar imagen QR
    import qrcode
    qr = qrcode.make(url_qr)
    qr.save(f"qr_{cdc}.png")
    
    # 5. Validar el XML firmado (opcional)
    xml_firmado = respuesta.xml_firmado
    validacion = client.validar_firma_xml(xml_firmado)
    
    if validacion.is_valid:
        print(f"✓ Firma válida hasta: {validacion.valid_to}")
    
    # 6. Entregar al cliente
    # - Enviar PDF con QR impreso
    # - Enviar URL por email/WhatsApp
    # - Cliente escanea QR para verificar
```

Beneficios:
- ✓ Cliente puede verificar autenticidad
- ✓ Consulta directa en SIFEN
- ✓ No requiere instalar apps
- ✓ Cumplimiento normativo
    """)


if __name__ == "__main__":
    ejemplo_validar_firma_xml()
    ejemplo_validar_firma_archivo()
    ejemplo_generar_url_qr()
    ejemplo_generar_qr_imagen()
    ejemplo_caso_uso_completo()
    
    print("\n" + "=" * 70)
    print("Resumen de Funcionalidades")
    print("=" * 70)
    print("✓ Validar firmas XML (con cliente o estático)")
    print("✓ Validar firmas de archivos")
    print("✓ Generar URLs de consulta QR")
    print("✓ Integración con librerías QR")
    print("✓ 100% compatible con librería Java")
    print("=" * 70)
