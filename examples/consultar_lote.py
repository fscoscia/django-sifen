#!/usr/bin/env python3
"""
Ejemplo de consulta de estado de lote.
"""

from sifen.client import SifenClient
from sifen.config import SifenConfig, TipoAmbiente


def main():
    print("\n" + "=" * 70)
    print("Consulta de Estado de Lote")
    print("=" * 70)

    # 1. Configurar cliente
    print("\n1. Configurando cliente SIFEN...")
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/Users/fscoscia/Girolabs/facturacion-electronica/django-sifen/JOANA NICOLE SAWATZKY VDA DE REGIER.pfx",
        certificado_contrasena="Sk59vkhu?!",
        csc="ABCD0000000000000000000000000000",
        csc_id="0001",
    )
    client = SifenClient(config)
    print("   ✓ Cliente configurado")

    # 2. Solicitar número de lote
    print("\n2. Ingrese el número de lote a consultar:")
    print("   (Ejemplo: 82927707102146486)")
    numero_lote = input("   Número de lote: ").strip()

    if not numero_lote:
        print("   ✗ Debe ingresar un número de lote")
        return

    # 3. Consultar estado del lote
    print(f"\n3. Consultando estado del lote {numero_lote}...")

    try:
        respuesta = client.consultar_lote(numero_lote)

        print("\n   ✓ Consulta exitosa!")
        print(f"\n   Código: {respuesta.codigo}")
        print(f"   Mensaje: {respuesta.mensaje}")

        if respuesta.numero_lote:
            print(f"   Número de lote: {respuesta.numero_lote}")

        if respuesta.estado:
            print(f"   Estado: {respuesta.estado}")

        if respuesta.cantidad_documentos > 0:
            print(f"\n   Total documentos: {respuesta.cantidad_documentos}")

            print("\n   Detalle de documentos:")
            for i, doc in enumerate(respuesta.documentos or [], 1):
                print(f"   {i}. Estado: {doc.estado}")
                if doc.cdc:
                    print(f"      CDC: {doc.cdc}")
                if doc.numero_protocolo:
                    print(f"      Protocolo: {doc.numero_protocolo}")
                if doc.codigo:
                    print(f"      Código: {doc.codigo}")
                if doc.mensaje:
                    print(f"      Mensaje: {doc.mensaje}")
                if doc.fecha_aprobacion:
                    print(f"      Fecha: {doc.fecha_aprobacion}")
        else:
            print("\n   El lote aún está en proceso o no tiene documentos.")

    except Exception as e:
        print(f"\n   ✗ Error al consultar lote: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
