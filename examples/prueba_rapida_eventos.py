"""
Prueba rápida de eventos - Script simplificado.

Configura tus credenciales y ejecuta este script para probar eventos.
"""

from sifen import SifenClient
from sifen.config import SifenConfig, TipoAmbiente

# ============================================================================
# CONFIGURACIÓN - ACTUALIZA ESTOS VALORES
# ============================================================================

RUTA_CERTIFICADO = "/Users/fscoscia/Girolabs/facturacion-electronica/django-sifen/JOANA NICOLE SAWATZKY VDA DE REGIER.pfx"
PASSWORD_CERTIFICADO = "Sk59vkhu?!"
CSC = "ABCD0000000000000000000000000000"  # CSC de prueba para ambiente DEV
CSC_ID = "0001"

# CDC de un documento que hayas emitido (para probar cancelación)
CDC_PARA_CANCELAR = "01001001000000112024060412300080012345601"

# Datos para inutilización
TIMBRADO = 12345678
ESTABLECIMIENTO = "001"
PUNTO_EXPEDICION = "001"
NUMERO_INICIAL = "0000900"  # Números NO utilizados
NUMERO_FINAL = "0000905"

# ============================================================================


def main():
    """Función principal de prueba."""

    print("=" * 70)
    print("PRUEBA RÁPIDA DE EVENTOS SIFEN")
    print("=" * 70)

    # Configurar cliente
    print("\n1. Configurando cliente...")
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo=RUTA_CERTIFICADO,
        certificado_contrasena=PASSWORD_CERTIFICADO,
        csc=CSC,
        csc_id=CSC_ID,
    )

    client = SifenClient(config)
    print("   ✓ Cliente configurado")

    # Menú de opciones
    while True:
        print("\n" + "=" * 70)
        print("¿Qué deseas probar?")
        print("=" * 70)
        print("1. Cancelar documento")
        print("2. Inutilizar numeración")
        print("3. Enviar conformidad (como receptor)")
        print("4. Enviar disconformidad (como receptor)")
        print("5. Validar modelo sin enviar")
        print("0. Salir")
        print("=" * 70)

        opcion = input("\nSelecciona una opción: ").strip()

        if opcion == "0":
            print("\n¡Hasta luego!")
            break

        elif opcion == "1":
            probar_cancelacion(client)

        elif opcion == "2":
            probar_inutilizacion(client)

        elif opcion == "3":
            probar_conformidad(client)

        elif opcion == "4":
            probar_disconformidad(client)

        elif opcion == "5":
            probar_validacion()

        else:
            print("\n✗ Opción inválida")

        input("\nPresiona ENTER para continuar...")


def probar_cancelacion(client):
    """Prueba cancelación de documento."""
    print("\n" + "-" * 70)
    print("PRUEBA: Cancelación de Documento")
    print("-" * 70)

    # Permitir ingresar CDC personalizado
    print(f"\nCDC configurado: {CDC_PARA_CANCELAR}")
    print(f"Longitud: {len(CDC_PARA_CANCELAR)} caracteres")
    usar_otro = input("\n¿Usar otro CDC? (s/n): ").strip().lower()

    if usar_otro == "s":
        cdc = input("Ingresa el CDC (44 caracteres): ").strip()
    else:
        cdc = CDC_PARA_CANCELAR

    # Validar CDC
    if len(cdc) != 44:
        print(f"\n✗ ERROR: El CDC debe tener 44 caracteres, tiene {len(cdc)}")
        print("Ejemplo válido: 01800695115001001000000012024120613370900001")
        print("\nPrimero emite un documento:")
        print("  python examples/flujo_completo_factura.py")
        return

    if not cdc.isdigit():
        print("\n✗ ERROR: El CDC debe contener solo números")
        return

    motivo = input("\nIngresa el motivo de cancelación: ").strip()
    if not motivo:
        motivo = "Prueba de cancelación - Error en datos"

    print(f"\n✓ CDC válido: {cdc}")
    print(f"✓ Motivo: {motivo}")
    print(f"\nEnviando cancelación...")

    try:
        respuesta = client.cancelar_documento(cdc, motivo)

        print(f"\n{'='*70}")
        if respuesta.aprobado:
            print("✓ CANCELACIÓN APROBADA")
            print(f"{'='*70}")
            print(f"Protocolo: {respuesta.numero_protocolo}")
            print(f"Fecha: {respuesta.fecha_recepcion}")
        else:
            print("✗ CANCELACIÓN RECHAZADA")
            print(f"{'='*70}")
            print(f"Código: {respuesta.codigo}")
            print(f"Mensaje: {respuesta.mensaje}")
        print(f"{'='*70}")

    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")


def probar_inutilizacion(client):
    """Prueba inutilización de numeración."""
    print("\n" + "-" * 70)
    print("PRUEBA: Inutilización de Numeración")
    print("-" * 70)

    print(f"\nDatos configurados:")
    print(f"  Timbrado: {TIMBRADO}")
    print(f"  Establecimiento: {ESTABLECIMIENTO}")
    print(f"  Punto Expedición: {PUNTO_EXPEDICION}")
    print(f"  Rango: {NUMERO_INICIAL} - {NUMERO_FINAL}")

    usar_otros = input("\n¿Usar otros valores? (s/n): ").strip().lower()

    if usar_otros == "s":
        timbrado = int(input("Timbrado: "))
        est = input("Establecimiento (3 dígitos): ")
        pto = input("Punto Expedición (3 dígitos): ")
        num_ini = input("Número Inicial (7 dígitos): ")
        num_fin = input("Número Final (7 dígitos): ")
    else:
        timbrado = TIMBRADO
        est = ESTABLECIMIENTO
        pto = PUNTO_EXPEDICION
        num_ini = NUMERO_INICIAL
        num_fin = NUMERO_FINAL

    motivo = input("Motivo: ").strip()
    if not motivo:
        motivo = "Prueba de inutilización - Salto de numeración"

    print(f"\nEnviando inutilización...")

    try:
        respuesta = client.inutilizar_numeracion(
            motivo=motivo,
            timbrado=timbrado,
            establecimiento=est,
            punto_expedicion=pto,
            numero_inicial=num_ini,
            numero_final=num_fin,
            tipo_documento=1,
        )

        print(f"\n{'='*70}")
        if respuesta.aprobado:
            print("✓ INUTILIZACIÓN APROBADA")
            print(f"{'='*70}")
            print(f"Protocolo: {respuesta.numero_protocolo}")
            print(f"Rango inutilizado: {est}-{pto}-{num_ini} a {num_fin}")
        else:
            print("✗ INUTILIZACIÓN RECHAZADA")
            print(f"{'='*70}")
            print(f"Código: {respuesta.codigo}")
            print(f"Mensaje: {respuesta.mensaje}")
        print(f"{'='*70}")

    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")


def probar_conformidad(client):
    """Prueba conformidad de documento."""
    print("\n" + "-" * 70)
    print("PRUEBA: Conformidad de Documento (Receptor)")
    print("-" * 70)

    cdc = input("\nIngresa el CDC del documento recibido: ").strip()

    if not cdc:
        print("✗ CDC requerido")
        return

    print(f"\nEnviando conformidad...")

    try:
        respuesta = client.enviar_conformidad(cdc)

        print(f"\n{'='*70}")
        if respuesta.aprobado:
            print("✓ CONFORMIDAD REGISTRADA")
            print(f"{'='*70}")
            print(f"Protocolo: {respuesta.numero_protocolo}")
        else:
            print("✗ CONFORMIDAD RECHAZADA")
            print(f"{'='*70}")
            print(f"Código: {respuesta.codigo}")
            print(f"Mensaje: {respuesta.mensaje}")
        print(f"{'='*70}")

    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")


def probar_disconformidad(client):
    """Prueba disconformidad de documento."""
    print("\n" + "-" * 70)
    print("PRUEBA: Disconformidad de Documento (Receptor)")
    print("-" * 70)

    cdc = input("\nIngresa el CDC del documento recibido: ").strip()
    motivo = input("Ingresa el motivo de disconformidad: ").strip()

    if not cdc or not motivo:
        print("✗ CDC y motivo son requeridos")
        return

    print(f"\nEnviando disconformidad...")

    try:
        respuesta = client.enviar_disconformidad(cdc, motivo)

        print(f"\n{'='*70}")
        if respuesta.aprobado:
            print("✓ DISCONFORMIDAD REGISTRADA")
            print(f"{'='*70}")
            print(f"Protocolo: {respuesta.numero_protocolo}")
        else:
            print("✗ DISCONFORMIDAD RECHAZADA")
            print(f"{'='*70}")
            print(f"Código: {respuesta.codigo}")
            print(f"Mensaje: {respuesta.mensaje}")
        print(f"{'='*70}")

    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")


def probar_validacion():
    """Prueba validación de modelos sin enviar."""
    print("\n" + "-" * 70)
    print("PRUEBA: Validación de Modelos (sin envío)")
    print("-" * 70)

    from sifen.models.eventos import (
        EventoCancelacion,
        EventoInutilizacion,
        EventoDisconformidad,
    )

    print("\n1. Validando EventoCancelacion...")
    evento1 = EventoCancelacion(mOtEve="Motivo válido")
    is_valid, error = evento1.validate()
    print(f"   {'✓' if is_valid else '✗'} {error or 'Válido'}")

    print("\n2. Validando EventoCancelacion con motivo vacío...")
    evento2 = EventoCancelacion(mOtEve="")
    is_valid, error = evento2.validate()
    print(f"   {'✓' if not is_valid else '✗'} {error or 'Debería ser inválido'}")

    print("\n3. Validando EventoInutilizacion...")
    evento3 = EventoInutilizacion(
        mOtEve="Motivo",
        dNumTim=12345678,
        dEst="001",
        dPunExp="001",
        dNumIn="0000001",
        dNumFin="0000010",
        iTiDE=1,
    )
    is_valid, error = evento3.validate()
    print(f"   {'✓' if is_valid else '✗'} {error or 'Válido'}")

    print("\n4. Validando EventoDisconformidad...")
    evento4 = EventoDisconformidad(mOtEve="Motivo de disconformidad")
    is_valid, error = evento4.validate()
    print(f"   {'✓' if is_valid else '✗'} {error or 'Válido'}")

    print("\n✓ Pruebas de validación completadas")


if __name__ == "__main__":
    print("\n⚠️  IMPORTANTE:")
    print("   - Actualiza las credenciales al inicio del archivo")
    print("   - Usa CDCs reales de documentos emitidos/recibidos")
    print("   - Este script usa el ambiente de TEST\n")

    input("Presiona ENTER para continuar...")

    main()
