"""
Ejemplos de uso de eventos del receptor.

Eventos disponibles para el receptor:
- Notificación de Recepción (Evento 10)
- Conformidad Total/Parcial (Evento 11)
- Disconformidad (Evento 12)
- Desconocimiento (Evento 13)
"""

from datetime import datetime
from sifen import SifenClient
from sifen.config import SifenConfig, TipoAmbiente


def ejemplo_conformidad_documento():
    """
    Ejemplo de conformidad de un documento recibido.

    El receptor confirma que recibió el documento correctamente.
    Debe enviarse dentro de los 45 días desde la fecha de emisión.
    """
    print("\n=== Ejemplo: Conformidad de Documento ===\n")

    # Configurar cliente
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/path/to/certificado.p12",
        certificado_contrasena="password123",
        csc="ABCD0000000000000000000000000000",
        csc_id="0001",
    )

    client = SifenClient(config)

    # CDC del documento recibido
    cdc = "01001001000000112024050412300080012345601"

    try:
        # Enviar conformidad
        respuesta = client.enviar_conformidad(cdc)

        if respuesta.aprobado:
            print(f"✓ Conformidad registrada")
            print(f"  CDC: {cdc}")
            print(f"  Protocolo: {respuesta.numero_protocolo}")
            print(f"  Fecha: {respuesta.fecha_recepcion}")
        else:
            print(f"✗ Conformidad rechazada")
            print(f"  Código: {respuesta.codigo}")
            print(f"  Mensaje: {respuesta.mensaje}")

    except Exception as e:
        print(f"✗ Error al enviar conformidad: {str(e)}")


def ejemplo_disconformidad_documento():
    """
    Ejemplo de disconformidad de un documento recibido.

    El receptor rechaza el documento por algún motivo (mercadería incorrecta,
    diferencias en cantidades, etc.).
    Debe enviarse dentro de los 45 días desde la fecha de emisión.
    """
    print("\n=== Ejemplo: Disconformidad de Documento ===\n")

    # Configurar cliente
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/path/to/certificado.p12",
        certificado_contrasena="password123",
        csc="ABCD0000000000000000000000000000",
        csc_id="0001",
    )

    client = SifenClient(config)

    # CDC del documento recibido
    cdc = "01001001000000112024050412300080012345601"

    # Motivo de la disconformidad
    motivo = "La mercadería recibida no coincide con la facturada. Se recibieron 10 unidades en lugar de 20."

    try:
        # Enviar disconformidad
        respuesta = client.enviar_disconformidad(cdc, motivo)

        if respuesta.aprobado:
            print(f"✓ Disconformidad registrada")
            print(f"  CDC: {cdc}")
            print(f"  Motivo: {motivo}")
            print(f"  Protocolo: {respuesta.numero_protocolo}")
        else:
            print(f"✗ Disconformidad rechazada")
            print(f"  Código: {respuesta.codigo}")
            print(f"  Mensaje: {respuesta.mensaje}")

    except Exception as e:
        print(f"✗ Error al enviar disconformidad: {str(e)}")


def ejemplo_desconocimiento_documento():
    """
    Ejemplo de desconocimiento de un documento.

    El receptor indica que desconoce el documento (no lo recibió física o
    electrónicamente).
    Debe enviarse dentro de los 45 días desde la fecha de emisión.
    """
    print("\n=== Ejemplo: Desconocimiento de Documento ===\n")

    # Configurar cliente
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/path/to/certificado.p12",
        certificado_contrasena="password123",
        csc="ABCD0000000000000000000000000000",
        csc_id="0001",
    )

    client = SifenClient(config)

    # CDC del documento
    cdc = "01001001000000112024050412300080012345601"

    # Motivo del desconocimiento
    motivo = "No se recibió el documento electrónico ni la mercadería. No existe registro de esta transacción."

    try:
        # Enviar desconocimiento
        respuesta = client.enviar_desconocimiento(cdc, motivo)

        if respuesta.aprobado:
            print(f"✓ Desconocimiento registrado")
            print(f"  CDC: {cdc}")
            print(f"  Motivo: {motivo}")
            print(f"  Protocolo: {respuesta.numero_protocolo}")
        else:
            print(f"✗ Desconocimiento rechazado")
            print(f"  Código: {respuesta.codigo}")
            print(f"  Mensaje: {respuesta.mensaje}")

    except Exception as e:
        print(f"✗ Error al enviar desconocimiento: {str(e)}")


def ejemplo_flujo_completo_receptor():
    """
    Ejemplo de flujo completo del receptor.

    Muestra cómo un receptor puede gestionar documentos recibidos.
    """
    print("\n=== Ejemplo: Flujo Completo del Receptor ===\n")

    # Configurar cliente
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/path/to/certificado.p12",
        certificado_contrasena="password123",
        csc="ABCD0000000000000000000000000000",
        csc_id="0001",
    )

    client = SifenClient(config)

    # Simular recepción de varios documentos
    documentos_recibidos = [
        {
            "cdc": "01001001000000112024050412300080012345601",
            "estado": "conforme",
            "motivo": None,
        },
        {
            "cdc": "01001001000000112024050412300080012345602",
            "estado": "disconforme",
            "motivo": "Cantidad incorrecta",
        },
        {
            "cdc": "01001001000000112024050412300080012345603",
            "estado": "desconocido",
            "motivo": "No se recibió la mercadería",
        },
    ]

    print("Procesando documentos recibidos...\n")

    for doc in documentos_recibidos:
        cdc = doc["cdc"]
        estado = doc["estado"]
        motivo = doc["motivo"]

        print(f"Documento: {cdc[:20]}...")

        try:
            if estado == "conforme":
                respuesta = client.enviar_conformidad(cdc)
                print(f"  ✓ Conformidad enviada")

            elif estado == "disconforme":
                respuesta = client.enviar_disconformidad(cdc, motivo)
                print(f"  ✓ Disconformidad enviada: {motivo}")

            elif estado == "desconocido":
                respuesta = client.enviar_desconocimiento(cdc, motivo)
                print(f"  ✓ Desconocimiento enviado: {motivo}")

            if not respuesta.aprobado:
                print(f"  ✗ Evento rechazado: {respuesta.mensaje}")

        except Exception as e:
            print(f"  ✗ Error: {str(e)}")

        print()


if __name__ == "__main__":
    print("=" * 60)
    print("EJEMPLOS DE EVENTOS DEL RECEPTOR")
    print("=" * 60)

    # Descomentar el ejemplo que deseas ejecutar:

    # ejemplo_conformidad_documento()
    # ejemplo_disconformidad_documento()
    # ejemplo_desconocimiento_documento()
    # ejemplo_flujo_completo_receptor()

    print("\n" + "=" * 60)
    print("Nota: Estos son ejemplos de demostración.")
    print("Configura correctamente las credenciales antes de ejecutar.")
    print("=" * 60)
