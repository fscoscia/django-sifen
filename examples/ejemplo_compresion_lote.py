"""
Ejemplo de compresión ZIP en envío de lotes.

Demuestra cómo la librería comprime automáticamente los XMLs
para reducir el tamaño de la petición HTTP.
"""

import gzip
import base64
from lxml import etree


def demostrar_compresion():
    """Demuestra la compresión de XMLs en lotes."""
    
    print("=" * 70)
    print("Ejemplo: Compresión ZIP en Lotes")
    print("=" * 70)
    
    # Simular XMLs de documentos
    xmls = []
    for i in range(1, 6):
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rDE xmlns="http://ekuatia.set.gov.py/sifen/xsd" Id="DE{i:07d}">
    <dVerFor>150</dVerFor>
    <gTimb>
        <iTiDE>1</iTiDE>
        <dNumDoc>{i:07d}</dNumDoc>
    </gTimb>
    <gDatGralOpe>
        <dFeEmiDE>2024-05-04</dFeEmiDE>
    </gDatGralOpe>
</rDE>"""
        xmls.append(xml)
    
    print(f"\n1. Documentos a enviar: {len(xmls)}")
    
    # Calcular tamaño sin comprimir
    tamano_sin_comprimir = sum(len(xml.encode('utf-8')) for xml in xmls)
    print(f"\n2. Tamaño sin comprimir: {tamano_sin_comprimir:,} bytes")
    
    # Crear contenedor rLoteDE
    lote_root = etree.Element("rLoteDE")
    for xml_string in xmls:
        doc_element = etree.fromstring(xml_string.encode('utf-8'))
        lote_root.append(doc_element)
    
    # Convertir a string
    lote_xml_string = etree.tostring(
        lote_root,
        encoding='unicode',
        xml_declaration=False
    )
    
    print(f"   XML del lote: {len(lote_xml_string):,} bytes")
    
    # Comprimir con GZIP
    lote_xml_bytes = lote_xml_string.encode('utf-8')
    compressed = gzip.compress(lote_xml_bytes)
    
    print(f"\n3. Compresión GZIP:")
    print(f"   Tamaño comprimido: {len(compressed):,} bytes")
    print(f"   Reducción: {100 - (len(compressed) / len(lote_xml_bytes) * 100):.1f}%")
    
    # Codificar en Base64
    lote_base64 = base64.b64encode(compressed).decode('utf-8')
    
    print(f"\n4. Codificación Base64:")
    print(f"   Tamaño final: {len(lote_base64):,} bytes")
    print(f"   Primeros 100 caracteres:")
    print(f"   {lote_base64[:100]}...")
    
    # Verificar que se puede descomprimir
    print(f"\n5. Verificación:")
    decoded = base64.b64decode(lote_base64)
    decompressed = gzip.decompress(decoded).decode('utf-8')
    
    if decompressed == lote_xml_string:
        print("   ✓ Compresión/descompresión exitosa")
    else:
        print("   ✗ Error en compresión/descompresión")
    
    # Resumen
    print("\n" + "=" * 70)
    print("Resumen de Compresión")
    print("=" * 70)
    print(f"Original:    {tamano_sin_comprimir:>10,} bytes")
    print(f"Comprimido:  {len(compressed):>10,} bytes")
    print(f"Base64:      {len(lote_base64):>10,} bytes")
    print(f"Ahorro:      {100 - (len(compressed) / tamano_sin_comprimir * 100):>10.1f}%")
    print("\nBeneficios:")
    print("- Menor uso de ancho de banda")
    print("- Peticiones HTTP más rápidas")
    print("- Menor carga en servidores SIFEN")
    print("- Compatible con librería Java oficial")
    print("=" * 70)


def ejemplo_uso_en_libreria():
    """Muestra cómo la librería usa la compresión automáticamente."""
    
    print("\n\n" + "=" * 70)
    print("Uso en la Librería")
    print("=" * 70)
    
    print("""
La compresión es AUTOMÁTICA cuando usas client.enviar_lote():

```python
from sifen import SifenClient

client = SifenClient(config)

# Crear documentos
documentos = [doc1, doc2, doc3, ...]  # Hasta 50

# Enviar lote
# La librería automáticamente:
# 1. Genera XML de cada documento
# 2. Firma cada XML
# 3. Agrupa todos en un contenedor rLoteDE
# 4. Comprime con GZIP
# 5. Codifica en Base64
# 6. Envía a SIFEN
respuesta = client.enviar_lote(documentos)

print(f"Lote enviado: {respuesta.numero_lote}")
```

NO necesitas hacer nada especial - ¡la compresión es transparente!
    """)
    
    print("=" * 70)


if __name__ == "__main__":
    demostrar_compresion()
    ejemplo_uso_en_libreria()
