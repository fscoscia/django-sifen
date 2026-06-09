"""
Script de prueba para eventos SIFEN.

Este script te permite probar diferentes tipos de eventos en el ambiente de test.
"""

from datetime import datetime
from sifen import SifenClient
from sifen.config import SifenConfig, TipoAmbiente


def configurar_cliente():
    """
    Configura el cliente SIFEN para pruebas.

    IMPORTANTE: Actualiza estos valores con tus credenciales reales.
    """
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/Users/fscoscia/Girolabs/facturacion-electronica/django-sifen/JOANA NICOLE SAWATZKY VDA DE REGIER.pfx",
        certificado_contrasena="Sk59vkhu?!",
        csc="ABCD0000000000000000000000000000",
        csc_id="0001",
    )

    return SifenClient(config)


def test_cancelacion():
    """
    Prueba el evento de cancelación.

    Requisitos:
    - Tener un CDC de un documento aprobado en las últimas 48 horas
    """
    print("\n" + "=" * 60)
    print("TEST: Cancelación de Documento")
    print("=" * 60)

    client = configurar_cliente()

    # Solicitar CDC al usuario
    print("\n" + "-" * 60)
    cdc = input("Ingresa el CDC del documento a cancelar (44 caracteres): ").strip()

    # Validar CDC
    if len(cdc) != 44:
        print(
            f"\n✗ ERROR: El CDC debe tener exactamente 44 caracteres, tiene {len(cdc)}"
        )
        print("Ejemplo de CDC válido: 01800695115001001000000012024120613370900001")
        print("\nPrimero debes emitir un documento para obtener un CDC válido.")
        print("Ejecuta: python examples/flujo_completo_factura.py")
        return False

    if not cdc.isdigit():
        print("\n✗ ERROR: El CDC debe contener solo números")
        return False

    motivo = input("Ingresa el motivo de cancelación: ").strip()
    if not motivo:
        motivo = "Prueba de cancelación - Error en datos del documento"

    print(f"\n✓ CDC válido: {cdc}")
    print(f"✓ Motivo: {motivo}")
    print("\nEnviando cancelación...")

    try:
        respuesta = client.cancelar_documento(cdc, motivo)

        print(f"\n{'✓' if respuesta.aprobado else '✗'} Resultado:")
        print(f"  Código: {respuesta.codigo}")
        print(f"  Mensaje: {respuesta.mensaje}")

        if respuesta.aprobado:
            print(f"  Protocolo: {respuesta.numero_protocolo}")
            print(f"  Fecha: {respuesta.fecha_recepcion}")

        return respuesta.aprobado

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False


def test_inutilizacion():
    """
    Prueba el evento de inutilización de numeración.

    Requisitos:
    - Tener un timbrado válido
    - Los números no deben estar utilizados
    """
    print("\n" + "=" * 60)
    print("TEST: Inutilización de Numeración")
    print("=" * 60)

    client = configurar_cliente()

    # IMPORTANTE: Ajusta estos valores según tu timbrado
    timbrado = 12345678
    establecimiento = "001"
    punto_expedicion = "001"
    numero_inicial = "0000100"
    numero_final = "0000105"
    tipo_documento = 1  # Factura electrónica
    motivo = "Prueba de inutilización - Salto de numeración por error técnico"

    print(f"\nTimbrado: {timbrado}")
    print(
        f"Rango: {establecimiento}-{punto_expedicion}-{numero_inicial} a {numero_final}"
    )
    print(f"Motivo: {motivo}")

    try:
        respuesta = client.inutilizar_numeracion(
            motivo=motivo,
            timbrado=timbrado,
            establecimiento=establecimiento,
            punto_expedicion=punto_expedicion,
            numero_inicial=numero_inicial,
            numero_final=numero_final,
            tipo_documento=tipo_documento,
        )

        print(f"\n{'✓' if respuesta.aprobado else '✗'} Resultado:")
        print(f"  Código: {respuesta.codigo}")
        print(f"  Mensaje: {respuesta.mensaje}")

        if respuesta.aprobado:
            print(f"  Protocolo: {respuesta.numero_protocolo}")

        return respuesta.aprobado

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False


def test_conformidad():
    """
    Prueba el evento de conformidad (como receptor).

    Requisitos:
    - Tener un CDC de un documento recibido
    - El documento debe estar dentro de los 45 días de emisión
    """
    print("\n" + "=" * 60)
    print("TEST: Conformidad de Documento")
    print("=" * 60)

    client = configurar_cliente()

    # IMPORTANTE: Reemplaza con un CDC real de un documento recibido
    cdc = "01001001000000112024050412300080012345601"

    print(f"\nCDC: {cdc}")

    try:
        respuesta = client.enviar_conformidad(cdc)

        print(f"\n{'✓' if respuesta.aprobado else '✗'} Resultado:")
        print(f"  Código: {respuesta.codigo}")
        print(f"  Mensaje: {respuesta.mensaje}")

        if respuesta.aprobado:
            print(f"  Protocolo: {respuesta.numero_protocolo}")

        return respuesta.aprobado

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False


def test_disconformidad():
    """
    Prueba el evento de disconformidad (como receptor).
    """
    print("\n" + "=" * 60)
    print("TEST: Disconformidad de Documento")
    print("=" * 60)

    client = configurar_cliente()

    # IMPORTANTE: Reemplaza con un CDC real
    cdc = "01001001000000112024050412300080012345601"
    motivo = "Prueba de disconformidad - Mercadería no coincide con factura"

    print(f"\nCDC: {cdc}")
    print(f"Motivo: {motivo}")

    try:
        respuesta = client.enviar_disconformidad(cdc, motivo)

        print(f"\n{'✓' if respuesta.aprobado else '✗'} Resultado:")
        print(f"  Código: {respuesta.codigo}")
        print(f"  Mensaje: {respuesta.mensaje}")

        if respuesta.aprobado:
            print(f"  Protocolo: {respuesta.numero_protocolo}")

        return respuesta.aprobado

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False


def test_desconocimiento():
    """
    Prueba el evento de desconocimiento (como receptor).
    """
    print("\n" + "=" * 60)
    print("TEST: Desconocimiento de Documento")
    print("=" * 60)

    client = configurar_cliente()

    # IMPORTANTE: Reemplaza con un CDC real
    cdc = "01001001000000112024050412300080012345601"
    motivo = "Prueba de desconocimiento - No se recibió el documento"

    print(f"\nCDC: {cdc}")
    print(f"Motivo: {motivo}")

    try:
        respuesta = client.enviar_desconocimiento(cdc, motivo)

        print(f"\n{'✓' if respuesta.aprobado else '✗'} Resultado:")
        print(f"  Código: {respuesta.codigo}")
        print(f"  Mensaje: {respuesta.mensaje}")

        if respuesta.aprobado:
            print(f"  Protocolo: {respuesta.numero_protocolo}")

        return respuesta.aprobado

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False


def test_validacion_modelos():
    """
    Prueba la validación de modelos sin enviar a SIFEN.
    Útil para verificar que los datos son correctos antes de enviar.
    """
    print("\n" + "=" * 60)
    print("TEST: Validación de Modelos (sin envío)")
    print("=" * 60)

    from sifen.models.eventos import (
        EventoCancelacion,
        EventoInutilizacion,
        EventoDisconformidad,
        GestionEvento,
    )

    # Test 1: Cancelación válida
    print("\n1. Validando EventoCancelacion...")
    evento_canc = EventoCancelacion(mOtEve="Motivo de prueba para cancelación")
    is_valid, error = evento_canc.validate()
    print(f"   {'✓' if is_valid else '✗'} {error if error else 'Válido'}")

    # Test 2: Cancelación inválida (motivo muy largo)
    print("\n2. Validando EventoCancelacion con motivo largo...")
    evento_canc_inv = EventoCancelacion(mOtEve="x" * 501)  # Más de 500 caracteres
    is_valid, error = evento_canc_inv.validate()
    print(
        f"   {'✓' if not is_valid else '✗'} {error if error else 'Debería ser inválido'}"
    )

    # Test 3: Inutilización válida
    print("\n3. Validando EventoInutilizacion...")
    evento_inu = EventoInutilizacion(
        mOtEve="Motivo de inutilización",
        dNumTim=12345678,
        dEst="001",
        dPunExp="001",
        dNumIn="0000001",
        dNumFin="0000010",
        iTiDE=1,
    )
    is_valid, error = evento_inu.validate()
    print(f"   {'✓' if is_valid else '✗'} {error if error else 'Válido'}")

    # Test 4: Inutilización inválida (establecimiento incorrecto)
    print("\n4. Validando EventoInutilizacion con establecimiento inválido...")
    evento_inu_inv = EventoInutilizacion(
        mOtEve="Motivo",
        dNumTim=12345678,
        dEst="1",  # Debe tener 3 dígitos
        dPunExp="001",
        dNumIn="0000001",
        dNumFin="0000010",
        iTiDE=1,
    )
    is_valid, error = evento_inu_inv.validate()
    print(
        f"   {'✓' if not is_valid else '✗'} {error if error else 'Debería ser inválido'}"
    )

    # Test 5: GestionEvento
    print("\n5. Validando GestionEvento...")
    gestion = GestionEvento(
        Id="EVE20240604123000",
        dFecFirma=datetime.now(),
        iTipEve=1,
        dDesTipEve="Cancelación",
        Id_CDC="0" * 44,  # CDC de 44 caracteres
        mOtEve="Motivo",
        gGroupGesEve=evento_canc,
    )
    is_valid, error = gestion.validate()
    print(f"   {'✓' if is_valid else '✗'} {error if error else 'Válido'}")


def menu_interactivo():
    """
    Menú interactivo para seleccionar qué prueba ejecutar.
    """
    while True:
        print("\n" + "=" * 60)
        print("MENÚ DE PRUEBAS DE EVENTOS SIFEN")
        print("=" * 60)
        print("\nEventos del Emisor:")
        print("  1. Cancelación de Documento")
        print("  2. Inutilización de Numeración")
        print("\nEventos del Receptor:")
        print("  3. Conformidad")
        print("  4. Disconformidad")
        print("  5. Desconocimiento")
        print("\nPruebas sin Envío:")
        print("  6. Validación de Modelos (sin envío a SIFEN)")
        print("\n  0. Salir")
        print("=" * 60)

        opcion = input("\nSelecciona una opción: ").strip()

        if opcion == "0":
            print("\n¡Hasta luego!")
            break
        elif opcion == "1":
            test_cancelacion()
        elif opcion == "2":
            test_inutilizacion()
        elif opcion == "3":
            test_conformidad()
        elif opcion == "4":
            test_disconformidad()
        elif opcion == "5":
            test_desconocimiento()
        elif opcion == "6":
            test_validacion_modelos()
        else:
            print("\n✗ Opción inválida")

        input("\nPresiona ENTER para continuar...")


if __name__ == "__main__":
    print("=" * 60)
    print("SCRIPT DE PRUEBA DE EVENTOS SIFEN")
    print("=" * 60)
    print("\n⚠️  IMPORTANTE:")
    print("1. Este script usa el ambiente de TEST de SIFEN")
    print("2. Debes actualizar las credenciales en configurar_cliente()")
    print("3. Debes usar CDCs reales de documentos que hayas emitido/recibido")
    print("4. Verifica los plazos de cada evento antes de probar")
    print("\n" + "=" * 60)

    input("\nPresiona ENTER para continuar...")

    # Ejecutar menú interactivo
    menu_interactivo()
