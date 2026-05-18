#!/usr/bin/env python
"""
Script de verificación rápida para django-sifen.

Verifica que todo esté correctamente instalado y configurado.
"""

import sys
from pathlib import Path


def print_header(text):
    """Imprime encabezado."""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


def print_section(text):
    """Imprime sección."""
    print(f"\n{text}")
    print("-" * 70)


def verificar_instalacion():
    """Verifica que la librería está instalada."""
    print_section("1. Verificando Instalación")
    
    try:
        import sifen
        print("✓ Librería sifen instalada")
        
        # Verificar versión si está disponible
        if hasattr(sifen, '__version__'):
            print(f"  Versión: {sifen.__version__}")
        
        return True
    except ImportError as e:
        print(f"✗ Librería no instalada: {e}")
        print("\n  Instalar con:")
        print("    pip install -e .")
        return False


def verificar_dependencias():
    """Verifica que todas las dependencias estén instaladas."""
    print_section("2. Verificando Dependencias")
    
    dependencias = {
        'lxml': 'lxml',
        'cryptography': 'cryptography',
        'requests': 'requests',
        'python-dotenv': 'dotenv',
    }
    
    todas_ok = True
    for nombre, modulo in dependencias.items():
        try:
            __import__(modulo)
            print(f"✓ {nombre}")
        except ImportError:
            print(f"✗ {nombre} no instalado")
            todas_ok = False
    
    if not todas_ok:
        print("\n  Instalar dependencias con:")
        print("    pip install -r requirements.txt")
    
    return todas_ok


def verificar_estructura():
    """Verifica la estructura de directorios."""
    print_section("3. Verificando Estructura")
    
    directorios = [
        'sifen',
        'sifen/models',
        'sifen/xml',
        'sifen/crypto',
        'sifen/services',
        'sifen/utils',
        'examples',
        'docs',
    ]
    
    todas_ok = True
    for directorio in directorios:
        path = Path(directorio)
        if path.exists() and path.is_dir():
            print(f"✓ {directorio}/")
        else:
            print(f"✗ {directorio}/ no encontrado")
            todas_ok = False
    
    return todas_ok


def verificar_imports():
    """Verifica que los imports principales funcionen."""
    print_section("4. Verificando Imports Principales")
    
    imports = [
        ('sifen', 'SifenClient'),
        ('sifen', 'SifenConfig'),
        ('sifen', 'TipoAmbiente'),
        ('sifen.models', 'DocumentoElectronico'),
        ('sifen.models', 'Emisor'),
        ('sifen.models', 'Receptor'),
        ('sifen.models', 'Item'),
        ('sifen.crypto', 'sign_xml'),
        ('sifen.crypto', 'validate_xml_signature'),
        ('sifen.utils.calculators', 'calcular_iva_item'),
    ]
    
    todas_ok = True
    for modulo, nombre in imports:
        try:
            mod = __import__(modulo, fromlist=[nombre])
            getattr(mod, nombre)
            print(f"✓ from {modulo} import {nombre}")
        except (ImportError, AttributeError) as e:
            print(f"✗ from {modulo} import {nombre}: {e}")
            todas_ok = False
    
    return todas_ok


def verificar_certificado_opcional():
    """Verifica certificado si el usuario lo proporciona."""
    print_section("5. Verificar Certificado (Opcional)")
    
    cert_path = input("\nRuta al certificado PFX (Enter para saltar): ").strip()
    
    if not cert_path:
        print("⊘ Verificación de certificado omitida")
        return None
    
    if not Path(cert_path).exists():
        print(f"✗ Archivo no encontrado: {cert_path}")
        return False
    
    password = input("Password del certificado: ").strip()
    
    try:
        from sifen.crypto import load_certificate
        
        with open(cert_path, "rb") as f:
            cert_bytes = f.read()
        
        print(f"\n  Tamaño: {len(cert_bytes)} bytes")
        
        cert_info = load_certificate(cert_bytes, password)
        
        print("✓ Certificado válido")
        if 'subject' in cert_info:
            print(f"  Subject: {cert_info['subject']}")
        if 'issuer' in cert_info:
            print(f"  Issuer: {cert_info['issuer']}")
        if 'valid_from' in cert_info:
            print(f"  Válido desde: {cert_info['valid_from']}")
        if 'valid_to' in cert_info:
            print(f"  Válido hasta: {cert_info['valid_to']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error al cargar certificado: {e}")
        return False


def verificar_conectividad():
    """Verifica conectividad con SIFEN."""
    print_section("6. Verificando Conectividad SIFEN")
    
    try:
        import requests
        
        # Ambiente de desarrollo
        url = "https://sifen-test.set.gov.py/de/ws/sync/recibe.wsdl"
        
        print(f"  Conectando a: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✓ Conectividad OK (HTTP {response.status_code})")
            print(f"  Tamaño respuesta: {len(response.content)} bytes")
            return True
        else:
            print(f"⚠ Respuesta inesperada: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ Timeout de conexión")
        print("  Verificar firewall o conexión a internet")
        return False
    except requests.exceptions.ConnectionError:
        print("✗ Error de conexión")
        print("  Verificar conexión a internet")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_basico():
    """Ejecuta un test básico de funcionalidad."""
    print_section("7. Test Básico de Funcionalidad")
    
    try:
        from sifen import SifenConfig, TipoAmbiente
        from decimal import Decimal
        from sifen.utils.calculators import calcular_base_exenta_nt13
        
        # Test 1: Crear configuración
        config = SifenConfig(
            ambiente=TipoAmbiente.DEV,
            certificado_archivo="dummy.pfx",
            certificado_contrasena="dummy",
            csc="test",
            csc_id="0001"
        )
        print("✓ Configuración creada")
        
        # Test 2: Calculadora NT-13
        resultado = calcular_base_exenta_nt13(
            total_operacion=Decimal("1000000"),
            proporcion_iva=Decimal("50"),
            tasa_iva=Decimal("10")
        )
        print(f"✓ Calculadora NT-13: {resultado}")
        
        # Test 3: Imports de modelos
        from sifen.models import Emisor, Receptor, Item
        
        emisor = Emisor(
            dRucEm="80012345-6",
            dDVEmi="6",
            dNomEmi="Test",
            dDirEmi="Test",
            dTelEmi="021-123456",
            dEmailE="test@test.com"
        )
        print("✓ Modelo Emisor creado")
        
        return True
        
    except Exception as e:
        print(f"✗ Error en test básico: {e}")
        import traceback
        traceback.print_exc()
        return False


def mostrar_siguiente_pasos():
    """Muestra los siguientes pasos."""
    print_section("Siguientes Pasos")
    
    print("""
1. Revisar documentación:
   - docs/README.md           - Índice de documentación
   - docs/CERTIFICADOS.md     - Configuración de certificados
   - docs/ESTRUCTURA_XML.md   - Estructura XML
   - docs/TESTING.md          - Guía de testing

2. Revisar ejemplos:
   - examples/ejemplo_basico.py
   - examples/ejemplo_certificados.py
   - examples/ejemplo_nota_tecnica_13.py

3. Configurar certificado:
   - Obtener certificado de prueba de SIFEN
   - Configurar en .env o usar SifenConfig

4. Ejecutar tests:
   - pytest tests/ -v

5. Probar en ambiente DEV:
   - Usar TipoAmbiente.DEV
   - Enviar documento de prueba
    """)


def main():
    """Función principal."""
    print_header("VERIFICACIÓN DE INSTALACIÓN - django-sifen")
    
    resultados = []
    
    # Verificaciones obligatorias
    resultados.append(("Instalación", verificar_instalacion()))
    resultados.append(("Dependencias", verificar_dependencias()))
    resultados.append(("Estructura", verificar_estructura()))
    resultados.append(("Imports", verificar_imports()))
    
    # Verificación opcional de certificado
    cert_result = verificar_certificado_opcional()
    if cert_result is not None:
        resultados.append(("Certificado", cert_result))
    
    # Verificaciones adicionales
    resultados.append(("Conectividad", verificar_conectividad()))
    resultados.append(("Test Básico", test_basico()))
    
    # Resumen
    print_header("RESUMEN")
    
    total = len(resultados)
    exitosos = sum(1 for _, r in resultados if r)
    
    for nombre, resultado in resultados:
        simbolo = "✓" if resultado else "✗"
        print(f"{simbolo} {nombre}")
    
    print(f"\nResultado: {exitosos}/{total} verificaciones exitosas")
    
    if exitosos == total:
        print("\n🎉 ¡TODO FUNCIONA CORRECTAMENTE!")
        mostrar_siguiente_pasos()
        return 0
    else:
        print("\n⚠️  ALGUNAS VERIFICACIONES FALLARON")
        print("\nRevisar los errores arriba y consultar la documentación.")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⊘ Verificación cancelada por el usuario")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n✗ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
