"""
Ejemplo de creación de una Factura de Exportación.

Este script demuestra cómo crear una Factura Electrónica (iTiDE=1)
con información de exportación en el campo dInfoFisc.
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
from sifen.xml import generate_xml
from sifen.config import SifenConfig, TipoAmbiente
from sifen.crypto import sign_xml_element
from sifen.client import SifenClient
from lxml import etree
import os


def generar_info_exportacion(
    tipo_operacion: str,
    condicion_negociacion: str,  # CIF, FOB, etc.
    pais_destino: str,
    empresa_fletera: str,
    agente_transporte: str,
    beneficiario: str,
    banco: str,
    numero_cuenta: str,
    codigo_swift: str,
    carta_credito: str = "",
    conocimiento_embarque: str = "",
    manifiesto_carga: str = "",
    barcaza: str = "N/A",
    info_adicional: str = "",
) -> str:
    """
    Genera el campo dInfoFisc para Factura de Exportación.

    Según Art. 20 numeral 15 del Decreto Nº 10797/2013.
    Los campos deben estar separados por coma (,) y espacio.
    """
    partes = [
        f"a) Tipo de Operación: {tipo_operacion}",
        f"b) Condición de Negociación: {condicion_negociacion}",
        f"c) País de Destino: {pais_destino}",
        f"d) Empresa Fletera o Exportador Nacional: {empresa_fletera}",
        f"e) Agente de Transporte: {agente_transporte}",
        f"f) Instrucciones de Pago para el cliente: Beneficiario: {beneficiario}, "
        f"Banco: {banco}, Nº de cuenta: {numero_cuenta}, Código SWIFT: {codigo_swift}"
        + (f", Cartas de Crédito: {carta_credito}" if carta_credito else ""),
        f"g) Número/s de Conocimiento/s de Embarque: {conocimiento_embarque}",
        f"h) Número/s de Manifiesto/s Internacional/es de Carga: {manifiesto_carga}",
        f"i) Número de barcaza o remolcador: {barcaza}",
        f"j) {info_adicional if info_adicional else 'Conforme Decreto 10797/2013 Art. 20 numeral 15'}",
    ]

    return ", ".join(partes)


def crear_factura_exportacion():
    """Crea una factura de exportación de ejemplo."""

    print("=" * 70)
    print("Creando Factura de Exportación")
    print("=" * 70)

    # 1. Identificación del DE (iTiDE=1, NO iTiDE=2)
    print("\n1. Creando identificación del DE...")
    identificacion = IdentificacionDE(
        iTiDE=1,  # Factura Electrónica (NO usar iTiDE=2)
        dDesTiDE="Factura Electrónica",
        dNumTim=12345678,
        dEst="001",
        dPunExp="001",
        dNumDoc="0000001",
        dFeIniT=datetime.now(),
    )
    print("   ✓ Tipo de documento: Factura Electrónica (iTiDE=1)")

    # 2. Generar información de exportación
    print("\n2. Generando información de exportación...")
    info_exportacion = generar_info_exportacion(
        tipo_operacion="Exportación Definitiva",
        condicion_negociacion="FOB",
        pais_destino="Brasil",
        empresa_fletera="NAVIERA INTERNACIONAL SA",
        agente_transporte="LOGISTICA GLOBAL SRL",
        beneficiario="MI EMPRESA EXPORTADORA SA",
        banco="BANCO ITAU PARAGUAY",
        numero_cuenta="1234567890",
        codigo_swift="ITAUPYPA",
        carta_credito="LC-2026-001234",
        conocimiento_embarque="BL-2026-001234",
        manifiesto_carga="MIC-2026-005678",
        barcaza="N/A",
        info_adicional="Exportación conforme Decreto 10797/2013",
    )
    print("   ✓ Información de exportación generada")
    print(f"\n   Campo dInfoFisc:\n   {info_exportacion[:200]}...")

    # 3. Datos generales CON información de exportación
    print("\n3. Creando datos generales con info de exportación...")
    datos_generales = DatosGeneralesDE(
        dFeEmiDE=date.today(),
        iTipEmi=1,
        dDesTipEmi="Normal",
        dCodSeg="123456789",
        dInfoFisc=info_exportacion,  # ← AQUÍ VA LA INFO DE EXPORTACIÓN
        iTipTra=1,  # Venta de mercadería
        dDesTipTra="Venta de mercadería",
        iTImp=1,  # IVA
        dDesTImp="IVA",
        cMoneOpe="USD",  # Exportaciones generalmente en USD
        dDesMoneOpe="Dólar Americano",
    )
    print("   ✓ Datos generales creados con información de exportación")

    # 4. Emisor (exportador paraguayo)
    print("\n4. Creando datos del emisor (exportador)...")
    emisor = Emisor(
        dRucEm="80012345-6",
        dDVEmi=6,
        iTipCont=1,
        dDesTipCont="Persona Jurídica",
        dNomEmi="MI EMPRESA EXPORTADORA SA",
        dNomFanEmi="Exportadora SA",
        dDirEmi="Av. Exportadores 1234",
        dNumCas=1234,
        cDepEmi=1,
        dDesDepEmi="Central",
        cDisEmi=1,
        dDesDisEmi="Asunción",
        cCiuEmi=1,
        dDesCiuEmi="Asunción",
        dTelEmi="021-123456",
        dEmailE="exportaciones@miempresa.com.py",
        gActEco=[
            ActividadEconomica(
                cActEco="46900",
                dDesActEco="Venta al por mayor de productos diversos n.c.p.",
            )
        ],
    )
    print("   ✓ Emisor creado")

    # 5. Receptor (importador extranjero)
    print("\n5. Creando datos del receptor (importador extranjero)...")
    receptor = Receptor(
        iNatRec=2,  # No residente
        dDesNatRec="No residente",
        iTiOpe=2,  # B2B con no residente
        dDesTiOpe="B2B con no residente",
        cPaisRec="BRA",  # Brasil
        dDesPaisRe="Brasil",
        dNumIDRec="12.345.678/0001-90",  # CNPJ brasileño
        dNomRec="EMPRESA IMPORTADORA BRASILEIRA LTDA",
        dDirRec="Rua das Importações, 500",
        dTelRec="+55-11-98765-4321",
        dEmailRec="importacao@empresa.com.br",
    )
    print("   ✓ Receptor creado (importador extranjero)")

    # 6. Items (productos exportados)
    print("\n6. Creando ítems de exportación...")
    items = [
        Item(
            dCodInt="EXP-001",
            dDesProSer="Producto manufacturado para exportación - Modelo A",
            cUniMed=77,  # Unidad
            dDesUniMed="Unidad",
            dCantProSer=Decimal("100"),
            cPaisOrig="PRY",  # Origen Paraguay
            dDesPaisOrig="Paraguay",
            gValorItem=ValorItem(
                dPUniProSer=Decimal("50"),  # USD 50 por unidad
                dTotOpeItem=Decimal("5000"),  # USD 5,000 total
                dTotOpeGs=Decimal("35000000"),  # Equivalente en Gs (TC: 7000)
                gCamIVA=IVAItem(
                    iAfecIVA=3,  # Exonerado (exportación)
                    dDesAfecIVA="Exonerado",
                    dPropIVA=Decimal("100"),
                    dTasaIVA=Decimal("0"),
                    dBasGravIVA=Decimal("0"),
                    dLiqIVAItem=Decimal("0"),
                ),
            ),
        ),
        Item(
            dCodInt="EXP-002",
            dDesProSer="Producto manufacturado para exportación - Modelo B",
            cUniMed=77,
            dDesUniMed="Unidad",
            dCantProSer=Decimal("50"),
            cPaisOrig="PRY",
            dDesPaisOrig="Paraguay",
            gValorItem=ValorItem(
                dPUniProSer=Decimal("100"),  # USD 100 por unidad
                dTotOpeItem=Decimal("5000"),  # USD 5,000 total
                dTotOpeGs=Decimal("35000000"),  # Equivalente en Gs
                gCamIVA=IVAItem(
                    iAfecIVA=3,  # Exonerado
                    dDesAfecIVA="Exonerado",
                    dPropIVA=Decimal("100"),
                    dTasaIVA=Decimal("0"),
                    dBasGravIVA=Decimal("0"),
                    dLiqIVAItem=Decimal("0"),
                ),
            ),
        ),
    ]
    print(f"   ✓ {len(items)} ítems de exportación creados")

    # 7. Totales (exportación exonerada de IVA)
    print("\n7. Calculando totales...")
    totales = Totales(
        dSubExe=Decimal("10000"),  # Total exonerado en USD
        dTotOpe=Decimal("10000"),  # Total operación
        dTotGralOpe=Decimal("10000"),  # Total general (sin IVA)
        dTotIVA=Decimal("0"),  # Sin IVA (exportación)
        cMoneOpe="USD",
        dDesMoneOpe="Dólar Americano",
        dTiCam=Decimal("7000"),  # Tipo de cambio: 1 USD = 7000 Gs
    )
    print("   ✓ Totales calculados (exportación exonerada de IVA)")

    # 8. Condición de operación
    print("\n8. Definiendo condición de operación...")
    condicion = CondicionOperacion(
        iCondOpe=1,  # Contado
        dDesCondOpe="Contado",
        gPaConEIni=[
            Pago(
                iTiPago=4,  # Transferencia bancaria
                dDesTiPag="Transferencia bancaria",
                dMonTiPag=Decimal("10000"),
                cMoneTiPag="USD",
                dDesMoneTiPag="Dólar Americano",
            )
        ],
    )
    print("   ✓ Condición de operación definida")

    # 9. Crear documento completo
    print("\n9. Ensamblando factura de exportación...")
    documento = DocumentoElectronico(
        dVerFor=150,
        gTimb=identificacion,
        gDatGralOpe=datos_generales,
        gEmis=emisor,
        gDatRec=receptor,
        gCamItem=items,
        gTotSub=totales,
        gPaConEIni=condicion,
    )
    print("   ✓ Factura de exportación ensamblada")

    # 10. Validar documento
    print("\n10. Validando documento...")
    is_valid, error = documento.validate()
    if is_valid:
        print("   ✓ Documento válido")
    else:
        print(f"   ✗ Documento inválido: {error}")
        return None

    # 11. Generar CDC
    print("\n11. Generando CDC...")
    cdc = documento.generate_cdc()
    print(f"   ✓ CDC generado: {cdc}")

    # 12. Mostrar resumen
    print("\n" + "=" * 70)
    print("Resumen de la Factura de Exportación")
    print("=" * 70)
    print(f"Tipo: {identificacion.dDesTiDE} (iTiDE={identificacion.iTiDE})")
    print(
        f"Número: {identificacion.dEst}-{identificacion.dPunExp}-{identificacion.dNumDoc}"
    )
    print(f"CDC: {cdc}")
    print(f"\nExportador: {emisor.dNomEmi}")
    print(f"Importador: {receptor.dNomRec}")
    print(f"País destino: {receptor.dDesPaisRe}")
    print(f"\nItems: {len(items)}")
    print(f"Moneda: {totales.dDesMoneOpe}")
    print(f"Total: USD {totales.dTotGralOpe:,.2f}")
    print(f"Equivalente: Gs. {float(totales.dTotGralOpe) * float(totales.dTiCam):,.0f}")
    print(f"Tipo de cambio: {totales.dTiCam:,.0f} Gs/USD")
    print(f"\nCondición: {condicion.dDesCondOpe}")
    print(f"IVA: Exonerado (exportación)")
    print("\nInformación de exportación incluida en campo dInfoFisc")
    print("=" * 70)

    return documento


def main():
    """Función principal."""
    print("\n" + "=" * 70)
    print("EJEMPLO: FACTURA DE EXPORTACIÓN - FLUJO COMPLETO")
    print("=" * 70)
    print("\nNOTA: La Factura de Exportación se implementa como:")
    print("  - Tipo de documento: iTiDE=1 (Factura Electrónica)")
    print("  - Información de exportación en campo dInfoFisc (B006)")
    print("  - Según Art. 20 numeral 15 del Decreto Nº 10797/2013")
    print("=" * 70)

    # Paso 1: Crear documento
    documento = crear_factura_exportacion()

    if not documento:
        print("\n✗ Error al crear la factura de exportación")
        return

    cdc = documento.CDC

    # Paso 2: Generar XML
    print("\n" + "=" * 70)
    print("PASO 2: GENERAR XML")
    print("=" * 70)

    try:
        xml_string = generate_xml(documento)
        print("✓ XML generado exitosamente")
        print(f"\nTamaño del XML: {len(xml_string)} caracteres")

        # Guardar XML sin firmar
        output_dir = "examples/output"
        os.makedirs(output_dir, exist_ok=True)
        xml_file = f"{output_dir}/factura_exportacion_{cdc}_sin_firmar.xml"

        with open(xml_file, "w", encoding="utf-8") as f:
            f.write(xml_string)
        print(f"✓ XML guardado en: {xml_file}")

    except Exception as e:
        print(f"✗ Error al generar XML: {e}")
        import traceback

        traceback.print_exc()
        return

    # Paso 3: Firmar XML
    print("\n" + "=" * 70)
    print("PASO 3: FIRMAR XML")
    print("=" * 70)

    # Configurar certificado (usando la misma configuración de flujo_completo_nc.py)
    try:
        config = SifenConfig(
            ambiente=TipoAmbiente.DEV,
            certificado_archivo="/Users/fscoscia/Girolabs/facturacion-electronica/django-sifen/JOANA NICOLE SAWATZKY VDA DE REGIER.pfx",
            certificado_contrasena="Sk59vkhu?!",
            csc="ABCD0000000000000000000000000000",
            csc_id="0001",
        )

        print(f"✓ Certificado cargado: {config.certificado_archivo}")
        print(f"✓ Ambiente: {config.ambiente.value}")

        # Parsear y firmar XML
        root = etree.fromstring(xml_string.encode("utf-8"))
        signed_root = sign_xml_element(root, config, reference_id=cdc)
        xml_firmado = etree.tostring(signed_root, encoding="unicode", pretty_print=True)

        print("✓ XML firmado digitalmente")

        # Guardar XML firmado
        xml_firmado_file = f"{output_dir}/factura_exportacion_{cdc}_firmado.xml"
        with open(xml_firmado_file, "w", encoding="utf-8") as f:
            f.write(xml_firmado)
        print(f"✓ XML firmado guardado en: {xml_firmado_file}")

    except Exception as e:
        print(f"✗ Error al firmar XML: {e}")
        import traceback

        traceback.print_exc()
        return

    # Paso 4: Enviar a SIFEN
    print("\n" + "=" * 70)
    print("PASO 4: ENVIAR A SIFEN")
    print("=" * 70)

    try:
        client = SifenClient(config)
        print("✓ Cliente SIFEN inicializado")
        print(f"  Ambiente: {config.ambiente.value}")

        # Enviar documento (sincrónico)
        print("\nEnviando factura de exportación a SIFEN (sincrónico)...")
        respuesta = client.enviar_documento(documento)

        if respuesta.aprobado:
            print("✓ Factura de exportación APROBADA por SIFEN!")
            print(f"\nRespuesta de SIFEN:")
            print(f"  CDC: {respuesta.cdc}")
            print(f"  Protocolo: {respuesta.numero_protocolo}")
            print(f"  Estado: Aprobado")

            if hasattr(respuesta, "fecha_aprobacion"):
                print(f"  Fecha aprobación: {respuesta.fecha_aprobacion}")

            # Guardar respuesta
            import json

            response_file = f"{output_dir}/factura_exportacion_{cdc}_respuesta.json"
            with open(response_file, "w", encoding="utf-8") as f:
                json.dump(respuesta.to_dict(), f, indent=2, ensure_ascii=False)
            print(f"\n✓ Respuesta guardada en: {response_file}")

        else:
            print("✗ Factura RECHAZADA por SIFEN")
            print(f"\nMotivo del rechazo:")
            if hasattr(respuesta, "mensaje"):
                print(f"  {respuesta.mensaje}")
            if hasattr(respuesta, "errores") and respuesta.errores:
                for error in respuesta.errores:
                    print(f"  - {error}")

    except Exception as e:
        print(f"✗ Error al enviar a SIFEN: {e}")
        import traceback

        traceback.print_exc()
        return

    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)
    print("✓ Factura de Exportación procesada completamente")
    print(f"\nCDC: {cdc}")
    print("Tipo: Factura Electrónica de Exportación")
    print("Exportador: MI EMPRESA EXPORTADORA SA")
    print("Importador: EMPRESA IMPORTADORA BRASILEIRA LTDA (Brasil)")
    print("Total: USD 10,000.00")
    print(f"\nArchivos generados:")
    print(f"  - XML sin firmar: {xml_file}")
    if "xml_firmado_file" in locals():
        print(f"  - XML firmado: {xml_firmado_file}")
    if "response_file" in locals():
        print(f"  - Respuesta SIFEN: {response_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
