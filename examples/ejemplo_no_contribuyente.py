"""
Ejemplo de creación de un Documento Electrónico para un NO CONTRIBUYENTE.

Este script demuestra cómo emitir una factura a un cliente no contribuyente
con diferentes tipos de documentos de identidad.
"""

from datetime import datetime, date
from decimal import Decimal

from sifen.models import (
    DocumentoElectronico,
    IdentificacionDE,
    DatosGeneralesDE,
    Emisor,
    Receptor,
    Item,
    ValorItem,
    IVAItem,
    Totales,
    SubtotalIVA,
    CondicionOperacion,
    Pago,
    ActividadEconomica,
)


def crear_factura_no_contribuyente_cedula():
    """
    Ejemplo 1: Factura a no contribuyente con CÉDULA PARAGUAYA.
    Tipo de operación: B2C (Business to Consumer)
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 1: Factura a No Contribuyente con Cédula Paraguaya")
    print("=" * 70)
    
    # Receptor no contribuyente con cédula
    receptor = Receptor(
        iNatRec=2,  # ⭐ 2 = No contribuyente
        dDesNatRec="No contribuyente",
        iTiOpe=2,   # ⭐ 2 = B2C (Business to Consumer)
        dDesTiOpe="B2C",
        cPaisRec="PRY",
        dDesPaisRe="Paraguay",
        
        # ⭐ Tipo de documento para no contribuyente
        iTipIDRec=1,  # 1 = Cédula paraguaya
        dDTipIDRec="Cédula paraguaya",
        dNumIDRec="1234567",  # Número de cédula
        
        # Datos del cliente
        dNomRec="Juan Pérez González",
        dDirRec="Av. Eusebio Ayala 1234",
        dNumCasRec=1234,
        cDepRec=1,
        dDesDepRec="Central",
        cDisRec=1,
        dDesDisRec="Asunción",
        cCiuRec=1,
        dDesCiuRec="Asunción",
        dTelRec="021-123456",
        dEmailRec="juan.perez@example.com",
    )
    
    # Validar receptor
    is_valid, error = receptor.validate()
    if is_valid:
        print("✓ Receptor válido")
        print(f"  - Naturaleza: No contribuyente")
        print(f"  - Tipo operación: B2C")
        print(f"  - Documento: Cédula paraguaya N° {receptor.dNumIDRec}")
    else:
        print(f"✗ Error: {error}")
        return None
    
    return receptor


def crear_factura_no_contribuyente_pasaporte():
    """
    Ejemplo 2: Factura a no contribuyente con PASAPORTE.
    Útil para turistas o extranjeros sin residencia.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 2: Factura a No Contribuyente con Pasaporte")
    print("=" * 70)
    
    receptor = Receptor(
        iNatRec=2,  # No contribuyente
        dDesNatRec="No contribuyente",
        iTiOpe=2,   # B2C
        dDesTiOpe="B2C",
        cPaisRec="BRA",  # País del pasaporte
        dDesPaisRe="Brasil",
        
        # ⭐ Pasaporte
        iTipIDRec=2,  # 2 = Pasaporte
        dDTipIDRec="Pasaporte",
        dNumIDRec="BR123456789",
        
        dNomRec="Maria Silva Santos",
        dTelRec="0981-234567",
        dEmailRec="maria.silva@example.com",
    )
    
    is_valid, error = receptor.validate()
    if is_valid:
        print("✓ Receptor válido")
        print(f"  - Tipo documento: Pasaporte")
        print(f"  - Número: {receptor.dNumIDRec}")
        print(f"  - País: {receptor.dDesPaisRe}")
    else:
        print(f"✗ Error: {error}")
    
    return receptor


def crear_factura_no_contribuyente_carnet_residencia():
    """
    Ejemplo 3: Factura a no contribuyente con CARNET DE RESIDENCIA.
    Para extranjeros residentes en Paraguay.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 3: Factura a No Contribuyente con Carnet de Residencia")
    print("=" * 70)
    
    receptor = Receptor(
        iNatRec=2,
        dDesNatRec="No contribuyente",
        iTiOpe=2,
        dDesTiOpe="B2C",
        cPaisRec="PRY",
        dDesPaisRe="Paraguay",
        
        # ⭐ Carnet de residencia
        iTipIDRec=4,  # 4 = Carnet de residencia
        dDTipIDRec="Carnet de residencia",
        dNumIDRec="RES987654",
        
        dNomRec="Carlos Rodríguez Martínez",
        dDirRec="Av. España 567",
        dNumCasRec=567,
        cDepRec=1,
        dDesDepRec="Central",
        cDisRec=1,
        dDesDisRec="Asunción",
        cCiuRec=1,
        dDesCiuRec="Asunción",
        dTelRec="021-987654",
    )
    
    is_valid, error = receptor.validate()
    if is_valid:
        print("✓ Receptor válido")
        print(f"  - Tipo documento: Carnet de residencia")
        print(f"  - Número: {receptor.dNumIDRec}")
    else:
        print(f"✗ Error: {error}")
    
    return receptor


def crear_factura_innominada():
    """
    Ejemplo 4: Factura INNOMINADA (sin identificación del cliente).
    Útil para ventas al público sin datos del cliente.
    Luego puede nominarse con el evento de nominación.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO 4: Factura Innominada (sin identificación)")
    print("=" * 70)
    
    receptor = Receptor(
        iNatRec=2,
        dDesNatRec="No contribuyente",
        iTiOpe=9,   # ⭐ 9 = Operación con innominado
        dDesTiOpe="Operación con innominado",
        cPaisRec="PRY",
        dDesPaisRe="Paraguay",
        
        # ⭐ Innominado
        iTipIDRec=5,  # 5 = Innominado
        dDTipIDRec="Innominado",
        dNumIDRec="0",  # Se completa con cero
        dNomRec="Sin Nombre",  # Nombre genérico
    )
    
    is_valid, error = receptor.validate()
    if is_valid:
        print("✓ Receptor válido")
        print(f"  - Tipo: Innominado")
        print(f"  - Nota: Esta factura puede nominarse posteriormente")
    else:
        print(f"✗ Error: {error}")
    
    return receptor


def mostrar_tipos_documento():
    """Muestra todos los tipos de documento disponibles para no contribuyentes."""
    print("\n" + "=" * 70)
    print("TIPOS DE DOCUMENTO PARA NO CONTRIBUYENTES")
    print("=" * 70)
    
    tipos = [
        (1, "Cédula paraguaya", "Para ciudadanos paraguayos"),
        (2, "Pasaporte", "Para extranjeros sin residencia"),
        (3, "Cédula extranjera", "Para extranjeros con cédula de su país"),
        (4, "Carnet de residencia", "Para extranjeros residentes en Paraguay"),
        (5, "Innominado", "Sin identificación (puede nominarse después)"),
        (6, "Tarjeta Diplomática", "Para personal diplomático"),
        (9, "No especificado", "Otros tipos de documento"),
    ]
    
    for codigo, nombre, descripcion in tipos:
        print(f"\n{codigo}. {nombre}")
        print(f"   {descripcion}")
    
    print("\n" + "=" * 70)


def mostrar_tipos_operacion():
    """Muestra los tipos de operación válidos para no contribuyentes."""
    print("\n" + "=" * 70)
    print("TIPOS DE OPERACIÓN PARA NO CONTRIBUYENTES")
    print("=" * 70)
    
    tipos = [
        (2, "B2C", "Business to Consumer", "✓ Más común para no contribuyentes"),
        (3, "B2G", "Business to Government", "✓ Operaciones con entidades públicas"),
        (4, "B2F", "Business to Foreign", "✓ Operaciones con extranjeros"),
        (9, "Innominado", "Operación innominada", "✓ Sin identificación del cliente"),
    ]
    
    print("\n❌ NO VÁLIDO: iTiOpe=1 (B2B) - Solo para contribuyentes con RUC\n")
    
    for codigo, sigla, nombre, nota in tipos:
        print(f"{codigo}. {sigla} - {nombre}")
        print(f"   {nota}\n")
    
    print("=" * 70)


def main():
    """Función principal."""
    print("\n" + "=" * 70)
    print("EJEMPLOS DE FACTURACIÓN A NO CONTRIBUYENTES")
    print("=" * 70)
    
    # Mostrar información general
    mostrar_tipos_documento()
    mostrar_tipos_operacion()
    
    # Crear ejemplos
    crear_factura_no_contribuyente_cedula()
    crear_factura_no_contribuyente_pasaporte()
    crear_factura_no_contribuyente_carnet_residencia()
    crear_factura_innominada()
    
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print("\nPara emitir a NO CONTRIBUYENTE:")
    print("  1. iNatRec = 2 (No contribuyente)")
    print("  2. iTiOpe = 2, 3, 4 o 9 (NO usar 1=B2B)")
    print("  3. iTipIDRec = tipo de documento (1-6, 9)")
    print("  4. dNumIDRec = número del documento")
    print("\nPara emitir a CONTRIBUYENTE:")
    print("  1. iNatRec = 1 (Contribuyente)")
    print("  2. iTiOpe = 1 (B2B)")
    print("  3. dRucRec y dDVRec = RUC del contribuyente")
    print("=" * 70)


if __name__ == "__main__":
    main()
