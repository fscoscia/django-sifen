"""
Ejemplo de uso del módulo de firma digital.

Este script demuestra cómo firmar un documento XML simple.
"""

from lxml import etree
from sifen.config import SifenConfig, TipoAmbiente
from sifen.crypto import sign_xml_element, validate_xml_signature


def create_sample_xml():
    """Crea un XML de ejemplo para firmar."""
    root = etree.Element("DocumentoElectronico")
    root.set("Id", "DE001")
    
    emisor = etree.SubElement(root, "Emisor")
    etree.SubElement(emisor, "RUC").text = "80012345-6"
    etree.SubElement(emisor, "Nombre").text = "Empresa de Prueba S.A."
    
    receptor = etree.SubElement(root, "Receptor")
    etree.SubElement(receptor, "RUC").text = "80067890-1"
    etree.SubElement(receptor, "Nombre").text = "Cliente de Prueba"
    
    total = etree.SubElement(root, "Total")
    total.text = "1000000"
    
    return root


def main():
    """Función principal de ejemplo."""
    print("=" * 60)
    print("Ejemplo de Firma Digital XML - SIFEN")
    print("=" * 60)
    
    # 1. Crear configuración
    # NOTA: Necesitas un certificado PFX válido para que esto funcione
    print("\n1. Configurando SIFEN...")
    
    try:
        config = SifenConfig(
            ambiente=TipoAmbiente.DEV,
            certificado_archivo="/path/to/certificado.pfx",  # Cambiar por tu certificado
            certificado_contrasena="tu_password",  # Cambiar por tu contraseña
            csc="ABCD0000000000000000000000000000",
            csc_id="0001",
        )
        print("   ✓ Configuración creada")
    except Exception as e:
        print(f"   ✗ Error en configuración: {e}")
        print("\n   NOTA: Este ejemplo requiere un certificado PFX válido.")
        print("   Modifica las rutas y contraseñas en el código.")
        return
    
    # 2. Crear XML de ejemplo
    print("\n2. Creando documento XML de ejemplo...")
    xml_doc = create_sample_xml()
    print("   ✓ XML creado")
    print("\nXML original:")
    print(etree.tostring(xml_doc, encoding='unicode', pretty_print=True))
    
    # 3. Firmar el documento
    print("\n3. Firmando documento...")
    try:
        signed_xml = sign_xml_element(
            xml_doc,
            config,
            reference_id="DE001"  # ID del elemento a firmar
        )
        print("   ✓ Documento firmado exitosamente")
        
        print("\nXML firmado:")
        print(etree.tostring(signed_xml, encoding='unicode', pretty_print=True))
        
    except Exception as e:
        print(f"   ✗ Error al firmar: {e}")
        return
    
    # 4. Validar la firma
    print("\n4. Validando firma...")
    try:
        xml_string = etree.tostring(signed_xml, encoding='unicode')
        result = validate_xml_signature(xml_string)
        
        if result.is_valid:
            print("   ✓ Firma válida")
            print(f"   Certificado: {result.certificate_subject}")
        else:
            print(f"   ✗ Firma inválida: {result.reason}")
            
    except Exception as e:
        print(f"   ✗ Error al validar: {e}")
    
    print("\n" + "=" * 60)
    print("Ejemplo completado")
    print("=" * 60)


if __name__ == "__main__":
    main()
