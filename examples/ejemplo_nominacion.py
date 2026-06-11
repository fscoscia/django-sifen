"""
Ejemplo de uso del evento de Nominación.

Este ejemplo muestra cómo asignar el RUC o identidad correcta a una factura
que originalmente se emitió a un "innominado" (sin identificación del receptor).

Flujo:
1. Emitir una factura a "innominado"
2. Obtener el CDC de la factura aprobada
3. Enviar evento de nominación para asignar los datos del receptor
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


def ejemplo_nominacion_basico():
    """
    Ejemplo básico de nominación de documento.

    Requisitos:
    - Tener un CDC de un documento emitido a "innominado"
    - El documento debe estar aprobado
    """
    print("\n" + "=" * 70)
    print("EJEMPLO: Nominación de Documento Innominado")
    print("=" * 70)

    client = configurar_cliente()

    # CDC del documento innominado que queremos nominar
    cdc_innominado = "01800695115001001000000012024120613370900001"

    # Datos del receptor a asignar
    ruc_receptor = "80012345"
    dv_receptor = 6
    nombre_receptor = "Juan Pérez"
    motivo = "Asignación de datos del receptor a factura innominada"

    print(f"\n📄 CDC del documento: {cdc_innominado}")
    print(f"👤 Receptor: {nombre_receptor}")
    print(f"🆔 RUC: {ruc_receptor}-{dv_receptor}")
    print(f"📝 Motivo: {motivo}")
    print("\n⏳ Enviando evento de nominación...")

    try:
        respuesta = client.nominar_documento(
            cdc=cdc_innominado,
            motivo=motivo,
            ruc=ruc_receptor,
            dv=dv_receptor,
            nombre=nombre_receptor,
        )

        print(f"\n{'✅' if respuesta.aprobado else '❌'} Resultado:")
        print(f"  Código: {respuesta.codigo}")
        print(f"  Mensaje: {respuesta.mensaje}")

        if respuesta.aprobado:
            print(f"  📋 Protocolo: {respuesta.numero_protocolo}")
            print(f"  📅 Fecha: {respuesta.fecha_recepcion}")
            print("\n✅ Documento nominado exitosamente!")
        else:
            print("\n❌ La nominación fue rechazada")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def ejemplo_nominacion_completo():
    """
    Ejemplo completo con todos los parámetros opcionales.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO: Nominación Completa con Todos los Parámetros")
    print("=" * 70)

    client = configurar_cliente()

    cdc_innominado = "01800695115001001000000012024120613370900001"

    print(f"\n📄 CDC del documento: {cdc_innominado}")
    print("\n⏳ Enviando evento de nominación con parámetros completos...")

    try:
        respuesta = client.nominar_documento(
            cdc=cdc_innominado,
            motivo="Cliente identificado posteriormente - Venta de contado",
            ruc="80012345",
            dv=6,
            nombre="EMPRESA EJEMPLO S.A.",
            naturaleza_receptor=1,  # 1=Contribuyente, 2=No contribuyente
            tipo_operacion=1,  # 1=B2B, 2=B2C, etc.
            codigo_pais="PRY",  # Código ISO del país
            descripcion_pais="Paraguay",
            tipo_contribuyente=1,  # 1=Persona física, 2=Persona jurídica
        )

        print(f"\n{'✅' if respuesta.aprobado else '❌'} Resultado:")
        print(f"  Código: {respuesta.codigo}")
        print(f"  Mensaje: {respuesta.mensaje}")

        if respuesta.aprobado:
            print(f"  📋 Protocolo: {respuesta.numero_protocolo}")
            print(f"  📅 Fecha: {respuesta.fecha_recepcion}")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def ejemplo_validacion_previa():
    """
    Ejemplo de validación del modelo antes de enviar.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO: Validación de Evento de Nominación")
    print("=" * 70)

    from sifen.models.eventos import EventoNominacion

    # Crear evento de nominación
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

    # Validar antes de enviar
    is_valid, error = evento.validate()

    if is_valid:
        print("\n✅ Evento válido - Listo para enviar")
    else:
        print(f"\n❌ Evento inválido: {error}")


def ejemplo_manejo_errores():
    """
    Ejemplo de manejo de errores comunes.
    """
    print("\n" + "=" * 70)
    print("EJEMPLO: Manejo de Errores en Nominación")
    print("=" * 70)

    client = configurar_cliente()

    # Casos de error comunes
    casos_error = [
        {
            "nombre": "CDC inválido (muy corto)",
            "cdc": "123",
            "ruc": "80012345",
            "dv": 6,
            "nombre": "Juan Pérez",
        },
        {
            "nombre": "RUC inválido (muy largo)",
            "cdc": "0" * 44,
            "ruc": "800123456789",
            "dv": 6,
            "nombre": "Juan Pérez",
        },
        {
            "nombre": "Nombre muy corto",
            "cdc": "0" * 44,
            "ruc": "80012345",
            "dv": 6,
            "nombre": "JP",
        },
    ]

    for caso in casos_error:
        print(f"\n🔍 Probando: {caso['nombre']}")

        try:
            respuesta = client.nominar_documento(
                cdc=caso["cdc"],
                motivo="Prueba de error",
                ruc=caso["ruc"],
                dv=caso["dv"],
                nombre=caso["nombre"],
            )

            print(f"  ⚠️  No se detectó error (inesperado)")

        except Exception as e:
            print(f"  ✅ Error detectado correctamente: {str(e)}")


if __name__ == "__main__":
    print("=" * 70)
    print("EJEMPLOS DE NOMINACIÓN DE DOCUMENTOS")
    print("=" * 70)
    print("\n⚠️  IMPORTANTE:")
    print("1. Actualiza las credenciales en configurar_cliente()")
    print("2. Usa un CDC real de un documento innominado que hayas emitido")
    print("3. El documento debe estar aprobado por SIFEN")
    print("4. Solo se puede nominar documentos emitidos a 'innominado'")
    print("\n" + "=" * 70)

    input("\nPresiona ENTER para continuar...")

    # Ejecutar ejemplos
    ejemplo_nominacion_basico()
    input("\nPresiona ENTER para el siguiente ejemplo...")

    ejemplo_nominacion_completo()
    input("\nPresiona ENTER para el siguiente ejemplo...")

    ejemplo_validacion_previa()
    input("\nPresiona ENTER para el siguiente ejemplo...")

    ejemplo_manejo_errores()

    print("\n" + "=" * 70)
    print("✅ Ejemplos completados")
    print("=" * 70)
