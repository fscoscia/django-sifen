"""
Ejemplo de uso del SifenClient.

Demuestra cómo usar la interfaz simplificada del cliente principal.
"""

from datetime import datetime, date
from decimal import Decimal

from sifen.client import SifenClient
from sifen.config import SifenConfig, TipoAmbiente
from sifen.models import (
    DocumentoElectronico,
    IdentificacionDE,
    DatosGeneralesDE,
    Emisor,
    ActividadEconomica,
    Receptor,
    Item,
    Totales,
    CondicionOperacion,
    Pago,
)
from sifen.utils import (
    calcular_valor_item,
    calcular_totales,
    validar_ruc,
    formatear_ruc,
)
from sifen.models.items import IVAItem
from sifen.models.totales import CondicionOperacion, Pago, SubtotalIVA


def main():
    """Ejemplo completo de uso del SifenClient."""

    print("=" * 70)
    print("Ejemplo: Uso del SifenClient")
    print("=" * 70)

    # 1. Configurar el cliente
    print("\n1. Configurando cliente SIFEN...")
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/Users/fscoscia/Girolabs/facturacion-electronica/django-sifen/JOANA NICOLE SAWATZKY VDA DE REGIER.pfx",
        certificado_contrasena="Sk59vkhu?!",
        csc="ABCD0000000000000000000000000000",
        csc_id="0001",
    )

    # Opción A: Configuración global
    SifenClient.set_config(config)
    client = SifenClient()

    # Opción B: Configuración por instancia
    # client = SifenClient(config)

    print("   ✓ Cliente configurado")

    # 2. Validar RUC (método estático)
    print("\n2. Validando RUC...")
    ruc = "5173025"
    dv = SifenClient.calcular_dv_ruc(ruc)
    print(f"   RUC: {ruc}")
    print(f"   DV calculado: {dv}")
    print(f"   RUC formateado: {SifenClient.formatear_ruc(ruc, str(dv))}")

    if SifenClient.validar_ruc(ruc, str(dv)):
        print("   ✓ RUC válido")
    else:
        print("   ✗ RUC inválido")

    # 3. Consultar RUC en SIFEN
    print("\n3. Consultando RUC en SIFEN...")
    try:
        respuesta_ruc = client.consultar_ruc("80090941", "0")
        if respuesta_ruc.encontrado:
            print(f"   ✓ RUC encontrado: {respuesta_ruc.contribuyente.nombre}")
        else:
            print(f"   ✗ RUC no encontrado")
    except Exception as e:
        print(f"   ⚠ Error al consultar: {e}")

    # 4. Crear documento con utilidades
    print("\n4. Creando documento electrónico...")

    # Crear ítems usando calculadoras
    item1 = Item(
        dCodInt="PROD002",
        dDesProSer="DOCUMENTO ELECTRÓNICO SIN VALOR COMERCIAL NI FISCAL - GENERADO EN AMBIENTE DE PRUEBA",
        cUniMed=77,
        dCantProSer=Decimal("10"),
        gValorItem=calcular_valor_item(
            precio_unitario=Decimal("100000"),
            cantidad=Decimal("10"),
            tasa_iva=10,
        ),
    )

    items = [item1]

    # Calcular totales automáticamente
    totales = calcular_totales(items)

    # Crear documento
    documento = DocumentoElectronico(
        dVerFor=150,
        gTimb=IdentificacionDE(
            iTiDE=1,
            dDesTiDE="Factura electrónica",
            dNumTim=80159272,
            dEst="001",
            dPunExp="001",
            dNumDoc="0000003",
            dFeIniT=datetime.strptime("2026-04-16", "%Y-%m-%d").date(),
        ),
        gDatGralOpe=DatosGeneralesDE(
            dFeEmiDE=datetime.now(),
            iTipEmi=1,
            dDesTipEmi="Normal",
            dCodSeg="482731694",
            dInfoEmi="1",
            dInfoFisc="Información de interés del Fisco respecto al DE",
            iTipTra=1,
            dDesTipTra="Venta de mercadería",
            iTImp=1,
            dDesTImp="IVA",
            cMoneOpe="PYG",
            dDesMoneOpe="guarani",
        ),
        gEmis=Emisor(
            dRucEm="80159272-0",
            dDVEmi=0,
            iTipCont=2,
            cTipReg=8,
            dNomEmi="DE generado en ambiente de prueba - sin valor comercial ni fiscal",
            dDirEmi="Av. Principal 123",
            cDepEmi=16,
            dDesDepEmi="BOQUERON",
            cDisEmi=259,
            dDesDisEmi="FILADELFIA",
            cCiuEmi=6413,
            dDesCiuEmi="COL.FERNHEIN",
            dTelEmi="0981424007",
            dEmailE="joanasawatzky@gmail.com",
            gActEco=[
                ActividadEconomica(
                    cActEco="69209",
                    dDesActEco="ACTIVIDADES DE CONTABILIDAD, TENEDURÍA DE LIBROS, AUDITORIA Y ASESORIA FISCAL N.C.P.",
                )
            ],
        ),
        gDatRec=Receptor(
            iNatRec=1,
            iTiOpe=1,
            iTiContRec=2,
            dRucRec="80090941",
            dDVRec="0",
            dNomRec="GIROLABS SOCIEDAD ANONIMA",
        ),
        gCamItem=items,
        gTotSub=totales,
        gPaConEIni=CondicionOperacion(
            iCondOpe=1,
            dDesCondOpe="Contado",
            gPaConEIni=[
                Pago(
                    iTiPago=1,
                    dDesTiPag="Efectivo",
                    dMonTiPag=totales.dTotGralOpe,
                )
            ],
        ),
    )

    print("   ✓ Documento creado")

    # 5. Validar documento
    print("\n5. Validando documento...")
    is_valid, error = client.validar_documento(documento)
    if is_valid:
        print("   ✓ Documento válido")
    else:
        print(f"   ✗ Documento inválido: {error}")
        return

    # 6. Generar XML y firmarlo
    print("\n6. Generando XML...")
    try:
        xml = client.generar_xml(documento)
        print(f"   ✓ XML generado ({len(xml)} caracteres)")
        print(f"   CDC: {documento.CDC}")

        # Guardar XML sin firmar
        xml_filename = f"documento_{documento.CDC}.xml"
        with open(xml_filename, "w", encoding="utf-8") as f:
            f.write(xml)
        print(f"   ✓ XML guardado en: {xml_filename}")

        # Firmar el XML
        print("\n   Firmando XML...")
        # Usar el CDC como reference_id para la firma
        xml_firmado = client.firmar_xml(xml, documento.CDC)
        print(f"   ✓ XML firmado ({len(xml_firmado)} caracteres)")

        # Guardar XML firmado
        xml_firmado_filename = f"documento_{documento.CDC}_firmado.xml"
        with open(xml_firmado_filename, "w", encoding="utf-8") as f:
            f.write(xml_firmado)
        print(f"   ✓ XML firmado guardado en: {xml_firmado_filename}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return

    # 7. Enviar documento (TODO: descomentar cuando tengas certificado válido)
    # print("\n7. Enviando documento a SIFEN...")
    # print("   ⚠ Comentado - requiere certificado válido")
    # print("   Para enviar, descomenta el siguiente código:")

    try:
        respuesta = client.enviar_documento(documento)

        if respuesta.aprobado:
            print(f"   ✓ Documento aprobado!")
            print(f"   CDC: {respuesta.cdc}")
            print(f"   Protocolo: {respuesta.numero_protocolo}")

            # 8. Consultar estado
            consulta = client.consultar_documento(respuesta.cdc)
            print(f"   Estado: {consulta.estado}")
        else:
            print(f"   ✗ Documento rechazado")
            print(f"   Código: {respuesta.codigo}")
            print(f"   Mensaje: {respuesta.mensaje}")
            if respuesta.xml_respuesta:
                print(
                    f"\n   Respuesta SIFEN completa:\n{respuesta.xml_respuesta[:3000]}"
                )
            if respuesta.xml_request:
                req_path = f"soap_request_{documento.CDC}.xml"
                with open(req_path, "w", encoding="utf-8") as f:
                    f.write(respuesta.xml_request)
                print(f"\n   SOAP request guardado en: {req_path}")
    except Exception as e:
        import traceback

        print(f"   ✗ Error: {e}")
        traceback.print_exc()

    # Resumen
    print("\n" + "=" * 70)
    print("Resumen")
    print("=" * 70)
    print(f"Cliente: Configurado y listo")
    print(f"Documento: Válido")
    print(f"CDC: {documento.CDC}")
    print(f"Total: Gs. {totales.dTotGralOpe:,.0f}")
    print("\nEl SifenClient simplifica todo el proceso:")
    print("- Validación automática")
    print("- Generación de CDC")
    print("- Generación de XML")
    print("- Firma digital")
    print("- Envío a SIFEN")
    print("\nTodo en una sola línea: client.enviar_documento(documento)")
    print("=" * 70)


if __name__ == "__main__":
    main()
