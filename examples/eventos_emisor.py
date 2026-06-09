"""
Ejemplos de uso de eventos del emisor.

Eventos disponibles para el emisor:
- Cancelación de DTE (Evento 1)
- Inutilización de numeración (Evento 2)
"""

from datetime import datetime
from sifen import SifenClient
from sifen.config import SifenConfig, TipoAmbiente


def ejemplo_cancelacion_dte():
    """
    Ejemplo de cancelación de un DTE.

    El emisor puede cancelar un DTE dentro de las 48 horas de su aprobación
    cuando:
    - Hubo errores en la emisión del DE
    - La mercadería no fue entregada al cliente
    - El servicio no ha sido realizado al cliente
    """
    print("\n=== Ejemplo: Cancelación de DTE ===\n")

    # Configurar cliente
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/path/to/certificado.p12",
        certificado_contrasena="password123",
        csc="ABCD0000000000000000000000000000",
        csc_id="0001",
    )

    client = SifenClient(config)

    # CDC del documento a cancelar
    cdc = "01001001000000112024050412300080012345601"

    # Motivo de la cancelación
    motivo = (
        "Error en el monto facturado. Se emitirá nuevo documento con el monto correcto."
    )

    try:
        # Enviar evento de cancelación
        respuesta = client.cancelar_documento(cdc, motivo)

        if respuesta.aprobado:
            print(f"✓ Cancelación aprobada")
            print(f"  Protocolo: {respuesta.numero_protocolo}")
            print(f"  Fecha: {respuesta.fecha_recepcion}")
        else:
            print(f"✗ Cancelación rechazada")
            print(f"  Código: {respuesta.codigo}")
            print(f"  Mensaje: {respuesta.mensaje}")

    except Exception as e:
        print(f"✗ Error al cancelar documento: {str(e)}")


def ejemplo_inutilizacion_numeracion():
    """
    Ejemplo de inutilización de numeración.

    El emisor debe inutilizar rangos de numeración cuando:
    - Saltos de numeración por errores técnicos
    - Errores de llenado del DE
    - No existe el generador del impuesto

    Se puede inutilizar un rango de hasta 1000 números.
    """
    print("\n=== Ejemplo: Inutilización de Numeración ===\n")

    # Configurar cliente
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/path/to/certificado.p12",
        certificado_contrasena="password123",
        csc="ABCD0000000000000000000000000000",
        csc_id="0001",
    )

    client = SifenClient(config)

    try:
        # Inutilizar rango de numeración
        respuesta = client.inutilizar_numeracion(
            motivo="Error en sistema de facturación. Números no utilizados.",
            timbrado=12345678,
            establecimiento="001",
            punto_expedicion="001",
            numero_inicial="0000100",
            numero_final="0000110",
            tipo_documento=1,  # Factura electrónica
        )

        if respuesta.aprobado:
            print(f"✓ Inutilización aprobada")
            print(f"  Rango: 001-001-0000100 a 001-001-0000110")
            print(f"  Protocolo: {respuesta.numero_protocolo}")
        else:
            print(f"✗ Inutilización rechazada")
            print(f"  Código: {respuesta.codigo}")
            print(f"  Mensaje: {respuesta.mensaje}")

    except Exception as e:
        print(f"✗ Error al inutilizar numeración: {str(e)}")


def ejemplo_lote_eventos():
    """
    Ejemplo de envío de lote de eventos.

    Se pueden enviar hasta 15 eventos de cualquier tipo en un solo lote.
    """
    print("\n=== Ejemplo: Lote de Eventos ===\n")

    # Configurar cliente
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/path/to/certificado.p12",
        certificado_contrasena="password123",
        csc="ABCD0000000000000000000000000000",
        csc_id="0001",
    )

    client = SifenClient(config)

    # Lista de XMLs de eventos firmados
    # (En un caso real, estos serían generados y firmados previamente)
    eventos_xml = [
        # XML de evento 1 (cancelación)
        "<rGesEve>...</rGesEve>",
        # XML de evento 2 (cancelación)
        "<rGesEve>...</rGesEve>",
        # ... hasta 15 eventos
    ]

    try:
        # Enviar lote de eventos
        respuesta = client.enviar_lote_eventos(eventos_xml)

        if respuesta.aprobado:
            print(f"✓ Lote de eventos aprobado")
            print(f"  Número de lote: {respuesta.numero_lote}")
            print(f"  Fecha: {respuesta.fecha_recepcion}")
            print(f"\nDetalles de eventos:")

            for evento in respuesta.eventos:
                estado = "✓" if evento.aprobado else "✗"
                print(
                    f"  {estado} Evento {evento.tipo_evento} - CDC: {evento.cdc[:20]}..."
                )
                print(f"     {evento.mensaje}")
        else:
            print(f"✗ Lote rechazado")
            print(f"  Código: {respuesta.codigo}")
            print(f"  Mensaje: {respuesta.mensaje}")

    except Exception as e:
        print(f"✗ Error al enviar lote de eventos: {str(e)}")


if __name__ == "__main__":
    print("=" * 60)
    print("EJEMPLOS DE EVENTOS DEL EMISOR")
    print("=" * 60)

    # Descomentar el ejemplo que deseas ejecutar:

    # ejemplo_cancelacion_dte()
    # ejemplo_inutilizacion_numeracion()
    # ejemplo_lote_eventos()

    print("\n" + "=" * 60)
    print("Nota: Estos son ejemplos de demostración.")
    print("Configura correctamente las credenciales antes de ejecutar.")
    print("=" * 60)
