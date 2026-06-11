"""
Flujo completo: Emitir factura innominada y luego nominarla.

IMPORTANTE: Este ejemplo muestra el concepto, pero para emitir una factura
innominada real, debes usar el ejemplo crear_documento.py como base y modificar
el receptor para que sea innominado (iTiOpe=9, dTipoDoc=5).

Por ahora, este script solo demuestra cómo nominar una factura existente.
"""

from sifen import SifenClient
from sifen.config import SifenConfig, TipoAmbiente


def configurar_cliente():
    """Configura el cliente SIFEN."""
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/Users/fscoscia/Girolabs/facturacion-electronica/django-sifen/JOANA NICOLE SAWATZKY VDA DE REGIER.pfx",
        certificado_contrasena="Sk59vkhu?!",
        csc="ABCD0000000000000000000000000000",
        csc_id="0001",
    )
    return SifenClient(config)


def nominar_factura_interactivo():
    """
    Nomina una factura innominada de forma interactiva.
    
    REQUISITOS:
    1. Debes tener el CDC de una factura que TÚ hayas emitido
    2. La factura debe haber sido emitida a "innominado" (iTiOpe=9)
    3. La factura debe estar aprobada por SIFEN
    """
    print("\n" + "=" * 70)
    print("NOMINACIÓN DE FACTURA INNOMINADA")
    print("=" * 70)
    
    print("\n⚠️  REQUISITOS:")
    print("1. CDC de una factura que TÚ hayas emitido a 'innominado'")
    print("2. La factura debe estar aprobada por SIFEN")
    print("3. El RUC del emisor debe coincidir con tu certificado")
    
    print("\n" + "-" * 70)
    
    # Solicitar CDC
    cdc = input("\nIngresa el CDC de la factura innominada (44 dígitos): ").strip()
    
    if len(cdc) != 44 or not cdc.isdigit():
        print("\n❌ CDC inválido. Debe tener exactamente 44 dígitos numéricos.")
        return False
    
    print(f"\n✓ CDC válido: {cdc}")
    
    # Solicitar datos del receptor
    print("\n" + "-" * 70)
    print("DATOS DEL RECEPTOR A ASIGNAR:")
    print("-" * 70)
    
    ruc = input("RUC del receptor (sin DV, ej: 80012345): ").strip()
    dv = input("Dígito verificador (ej: 6): ").strip()
    nombre = input("Nombre o razón social (ej: Juan Pérez): ").strip()
    motivo = input("Motivo de la nominación (opcional): ").strip()
    
    if not motivo:
        motivo = "Cliente identificado posteriormente - Asignación de datos fiscales"
    
    # Validaciones básicas
    if not ruc.isdigit() or len(ruc) < 3 or len(ruc) > 8:
        print("\n❌ RUC inválido. Debe tener entre 3 y 8 dígitos.")
        return False
    
    if not dv.isdigit():
        print("\n❌ DV inválido. Debe ser un dígito.")
        return False
    
    if len(nombre) < 4:
        print("\n❌ Nombre inválido. Debe tener al menos 4 caracteres.")
        return False
    
    # Mostrar resumen
    print("\n" + "=" * 70)
    print("RESUMEN DE LA NOMINACIÓN")
    print("=" * 70)
    print(f"CDC:      {cdc}")
    print(f"RUC:      {ruc}-{dv}")
    print(f"Nombre:   {nombre}")
    print(f"Motivo:   {motivo}")
    print("=" * 70)
    
    confirmar = input("\n¿Confirmar nominación? (s/n): ").strip().lower()
    
    if confirmar != 's':
        print("\n❌ Nominación cancelada")
        return False
    
    # Enviar nominación
    print("\n⏳ Enviando evento de nominación a SIFEN...")
    
    try:
        client = configurar_cliente()
        
        respuesta = client.nominar_documento(
            cdc=cdc,
            motivo=motivo,
            ruc=ruc,
            dv=int(dv),
            nombre=nombre,
        )
        
        print("\n" + "=" * 70)
        if respuesta.aprobado:
            print("✅ NOMINACIÓN EXITOSA")
            print("=" * 70)
            print(f"Protocolo: {respuesta.numero_protocolo}")
            print(f"Fecha:     {respuesta.fecha_recepcion}")
            print(f"\n🎉 La factura ahora está a nombre de: {nombre}")
        else:
            print("❌ NOMINACIÓN RECHAZADA")
            print("=" * 70)
            print(f"Código:  {respuesta.codigo}")
            print(f"Mensaje: {respuesta.mensaje}")
            
            # Ayuda específica para errores comunes
            if respuesta.codigo == "4468":
                print("\n💡 SOLUCIÓN:")
                print("   Este error significa que el RUC del emisor no coincide.")
                print("   Solo puedes nominar facturas que TÚ hayas emitido.")
                print("   Verifica que el CDC corresponda a una factura emitida")
                print("   con el certificado que estás usando actualmente.")
            elif respuesta.codigo == "0602":
                print("\n💡 SOLUCIÓN:")
                print("   La factura no fue emitida a 'innominado'.")
                print("   Solo se pueden nominar facturas con iTiOpe=9.")
        
        print("=" * 70)
        return respuesta.aprobado
        
    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ ERROR AL NOMINAR")
        print("=" * 70)
        print(f"Error: {str(e)}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        return False


def mostrar_ayuda():
    """Muestra ayuda sobre cómo emitir una factura innominada."""
    print("\n" + "=" * 70)
    print("CÓMO EMITIR UNA FACTURA INNOMINADA")
    print("=" * 70)
    
    print("\nPara emitir una factura a un cliente innominado, el receptor debe tener:")
    print("\n1. iTiOpe = 9 (Operación con innominado)")
    print("2. dTipoDoc = 5 (Innominado)")
    print("3. dNomRec = 'INNOMINADO'")
    print("4. NO incluir dNumDoc, dRucRec, ni dDVRec")
    
    print("\nEjemplo de código:")
    print("-" * 70)
    print("""
receptor = Receptor(
    iNatRec=2,  # No contribuyente
    iTiOpe=9,   # ⭐ Operación con innominado
    dDesTiOpe="Operación con innominado",
    cPaisRec="PRY",
    dDesPaisRe="Paraguay",
    dNomRec="INNOMINADO",  # Nombre genérico
    dTipoDoc=5,  # ⭐ Tipo documento = Innominado
    dDesTipoDoc="Innominado",
    # NO incluir dNumDoc, dRucRec, dDVRec
)
    """)
    print("-" * 70)
    
    print("\nPara un ejemplo completo de cómo crear un documento,")
    print("consulta: examples/crear_documento.py")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("=" * 70)
    print("FLUJO DE NOMINACIÓN DE FACTURAS")
    print("=" * 70)
    
    while True:
        print("\n" + "=" * 70)
        print("MENÚ PRINCIPAL")
        print("=" * 70)
        print("\n1. Nominar factura innominada existente")
        print("2. Ver ayuda: Cómo emitir factura innominada")
        print("0. Salir")
        print("=" * 70)
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == "0":
            print("\n¡Hasta luego!")
            break
        elif opcion == "1":
            nominar_factura_interactivo()
        elif opcion == "2":
            mostrar_ayuda()
        else:
            print("\n❌ Opción inválida")
        
        input("\nPresiona ENTER para continuar...")
