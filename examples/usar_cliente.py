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
    NotaCreditoDebito,
    DocumentoAsociado,
)
from sifen.models.nota_credito_debito import (
    MOTIVO_DEVOLUCION,
    MOTIVO_AJUSTE_PRECIO,
    DESCRIPCIONES_MOTIVOS,
)
from sifen.models.documento_asociado import (
    TIPO_DOC_ASOCIADO_ELECTRONICO,
    DESCRIPCIONES_TIPO_DOC_ASOCIADO,
)
from sifen.utils import (
    calcular_valor_item,
    calcular_totales,
    validar_ruc,
    formatear_ruc,
)
from sifen.models.items import IVAItem
from sifen.models.totales import CondicionOperacion, Pago, SubtotalIVA
from sifen.constants import (
    TIPO_FACTURA_ELECTRONICA,
    TIPO_NOTA_CREDITO_ELECTRONICA,
    TIPO_NOTA_DEBITO_ELECTRONICA,
    TIPO_NOTA_REMISION_ELECTRONICA,
    TIPO_AUTOFACTURA_ELECTRONICA,
)


def enviar_sincronico_ejemplo():
    """Ejemplo de envío sincrónico de un documento electrónico."""

    print("=" * 70)
    print("Ejemplo: Envío Sincrónico")
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

    client = SifenClient(config)
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

    # Generar código de seguridad aleatorio (9 dígitos)
    import random

    codigo_seguridad = str(random.randint(100000000, 999999999))
    print(f"   Código de seguridad generado: {codigo_seguridad}")

    # Crear ítems usando calculadoras
    cantidad = Decimal("10")
    item1 = Item(
        dCodInt="PROD002",
        dDesProSer="DOCUMENTO ELECTRÓNICO SIN VALOR COMERCIAL NI FISCAL - GENERADO EN AMBIENTE DE PRUEBA",
        cUniMed=77,
        dCantProSer=cantidad,
        gValorItem=calcular_valor_item(
            precio_unitario=Decimal("100000"),
            cantidad=cantidad,
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
            dNumDoc="0000049",
            dFeIniT=datetime.strptime("2026-04-16", "%Y-%m-%d").date(),
        ),
        gDatGralOpe=DatosGeneralesDE(
            dFeEmiDE=datetime.now(),
            iTipEmi=1,
            dDesTipEmi="Normal",
            dCodSeg=codigo_seguridad,
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

        # Firmar el XML
        print("\n   Firmando XML...")
        xml_firmado = client.firmar_xml(xml, documento.CDC)
        print(f"   ✓ XML firmado ({len(xml_firmado)} caracteres)")
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


def main():
    """Función principal para ejecutar ejemplos."""

    print("\n" + "=" * 70)
    print("EJEMPLOS DE USO DEL SIFEN CLIENT")
    print("=" * 70)
    print("\nTipos de Documentos Disponibles:")
    print("=" * 70)
    print("1. Factura Electrónica (iTiDE=1)")
    print("2. Envío por Lote de Facturas")
    print("3. Autofactura Electrónica (iTiDE=4)")
    print("4. Nota de Crédito Electrónica (iTiDE=5)")
    print("5. Nota de Débito Electrónica (iTiDE=6)")
    print("6. Nota de Remisión Electrónica (iTiDE=7)")
    print("=" * 70)
    print("\nDescomenta la función que desees probar:")
    print("=" * 70)

    # Descomenta la opción que desees probar:

    # 1. Factura Electrónica (envío sincrónico)
    enviar_sincronico_ejemplo()

    # 2. Envío por lote de facturas
    # enviar_lote_ejemplo()

    # 3. Nota de Crédito
    # enviar_nota_credito_ejemplo()

    # 4. Nota de Débito
    # enviar_nota_debito_ejemplo()

    # 5. Nota de Remisión
    # enviar_nota_remision_ejemplo()

    # 6. Autofactura
    # enviar_autofactura_ejemplo()


def enviar_lote_ejemplo():
    """Ejemplo de envío de lote de documentos."""

    print("\n" + "=" * 70)
    print("Ejemplo: Envío de Lote")
    print("=" * 70)

    # Configurar cliente (reutilizar la misma configuración)
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

    # Crear múltiples documentos
    print("\n2. Creando documentos para el lote...")
    documentos = []

    import random

    # Crear 2 documentos para el lote
    for i in range(1, 3):
        item = Item(
            dCodInt=f"PROD003",
            dDesProSer=f"DOCUMENTO ELECTRÓNICO SIN VALOR COMERCIAL NI FISCAL - GENERADO EN AMBIENTE DE PRUEBA #{i}",
            cUniMed=77,
            dCantProSer=Decimal("10"),
            gValorItem=calcular_valor_item(
                precio_unitario=Decimal("100000"),
                cantidad=Decimal("10"),
                tasa_iva=10,
            ),
        )

        totales = calcular_totales([item])

        # Número de documento único para cada documento del lote
        num_doc = f"{34 + i:07d}"  # 0000024, 0000025, etc.

        documento = DocumentoElectronico(
            dVerFor=150,
            gTimb=IdentificacionDE(
                iTiDE=1,
                dDesTiDE="Factura electrónica",
                dNumTim=80159272,
                dEst="001",
                dPunExp="001",
                dNumDoc=num_doc,
                dFeIniT=datetime.strptime("2026-04-16", "%Y-%m-%d").date(),
            ),
            gDatGralOpe=DatosGeneralesDE(
                dFeEmiDE=datetime.now(),
                iTipEmi=1,
                dDesTipEmi="Normal",
                dCodSeg=str(
                    random.randint(100000000, 999999999)
                ),  # Código aleatorio único
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
            gCamItem=[item],
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

        documentos.append(documento)
        print(f"   ✓ Documento {i} creado (CDC: {documento.CDC})")

    print(f"\n   Total: {len(documentos)} documentos creados")

    # Enviar lote
    print(f"\n3. Enviando lote de {len(documentos)} documentos...")

    try:
        respuesta = client.enviar_lote(documentos)

        print(f"\n   ✓ Lote enviado!")
        print(f"   Número de lote: {respuesta.numero_lote}")
        print(f"   Total documentos: {respuesta.cantidad_documentos}")
        print(f"   Aprobados: {respuesta.documentos_aprobados}")
        print(f"   Rechazados: {respuesta.documentos_rechazados}")

        print(f"\n   Detalle de documentos:")
        for i, detalle in enumerate(respuesta.detalles, 1):
            estado = "✓ Aprobado" if detalle.aprobado else "✗ Rechazado"
            print(f"   {i}. {estado}")
            print(f"      CDC: {detalle.cdc}")
            print(f"      Mensaje: {detalle.mensaje}")

        # if respuesta.numero_lote:
        #     print(f"\n4. Consultando estado del lote...")
        #     consulta = client.consultar_lote(respuesta.numero_lote)

        #     if consulta.encontrado:
        #         print(f"   ✓ Lote encontrado")
        #         print(f"   Estado: {consulta.estado}")
        #         print(f"   Documentos procesados: {consulta.cantidad_documentos}")
        #     else:
        #         print(f"   ✗ Lote no encontrado")

    except Exception as e:
        import traceback

        print(f"   ✗ Error: {e}")
        traceback.print_exc()

    print("\n" + "=" * 70)
    print("Resumen del Lote")
    print("=" * 70)
    print(f"Documentos enviados: {len(documentos)}")
    print(f"Límite por lote: 50 documentos")
    print("\nVentajas del envío por lote:")
    print("- Menor tiempo de procesamiento")
    print("- Menos peticiones HTTP")
    print("- Procesamiento asíncrono en SIFEN")
    print("- Ideal para facturación masiva")
    print("=" * 70)


def enviar_nota_credito_ejemplo():
    """Ejemplo de envío de Nota de Crédito Electrónica."""

    print("\n" + "=" * 70)
    print("Ejemplo: Nota de Crédito Electrónica")
    print("=" * 70)

    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/Users/fscoscia/Girolabs/facturacion-electronica/django-sifen/JOANA NICOLE SAWATZKY VDA DE REGIER.pfx",
        certificado_contrasena="Sk59vkhu?!",
        csc="ABCD0000000000000000000000000000",
        csc_id="0001",
    )

    client = SifenClient(config)
    print("   ✓ Cliente configurado")

    import random

    codigo_seguridad = str(random.randint(100000000, 999999999))

    # Item con precio negativo para nota de crédito
    cantidad = Decimal("5")
    item = Item(
        dCodInt="NC001",
        dDesProSer="DEVOLUCIÓN - DOCUMENTO ELECTRÓNICO SIN VALOR COMERCIAL NI FISCAL - GENERADO EN AMBIENTE DE PRUEBA",
        cUniMed=77,
        dCantProSer=cantidad,
        gValorItem=calcular_valor_item(
            precio_unitario=Decimal("50000"),
            cantidad=cantidad,
            tasa_iva=10,
        ),
    )

    totales = calcular_totales([item])

    # Crear grupo de Nota de Crédito
    nota_credito = NotaCreditoDebito(
        iMotEmi=MOTIVO_DEVOLUCION,
        dDesMotEmi=DESCRIPCIONES_MOTIVOS[MOTIVO_DEVOLUCION],
    )

    # IMPORTANTE: Documento Asociado - Referencia a la factura original
    # Debes reemplazar este CDC con el de una factura real que hayas enviado previamente
    # El CDC tiene 44 caracteres y se obtiene al enviar una factura exitosamente
    doc_asociado = DocumentoAsociado(
        iTipDocAso=TIPO_DOC_ASOCIADO_ELECTRONICO,  # 1 = Documento electrónico
        dDesTipDocAso=DESCRIPCIONES_TIPO_DOC_ASOCIADO[TIPO_DOC_ASOCIADO_ELECTRONICO],
        dCdCDERef="01800159272001001000000342026041612345678901234567890123",  # CDC de la factura original (ejemplo)
    )

    documento = DocumentoElectronico(
        dVerFor=150,
        gTimb=IdentificacionDE(
            iTiDE=TIPO_NOTA_CREDITO_ELECTRONICA,
            dDesTiDE="Nota de crédito electrónica",
            dNumTim=80159272,
            dEst="001",
            dPunExp="001",
            dNumDoc="0000037",
            dFeIniT=datetime.strptime("2026-04-16", "%Y-%m-%d").date(),
        ),
        gDatGralOpe=DatosGeneralesDE(
            dFeEmiDE=datetime.now(),
            iTipEmi=1,
            dDesTipEmi="Normal",
            dCodSeg=codigo_seguridad,
            dInfoEmi="Nota de crédito por devolución de mercadería",
            dInfoFisc="Información de interés del Fisco respecto al DE",
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
        gCamItem=[item],
        gTotSub=totales,
        gCamNCDE=nota_credito,
        gCamDEAsoc=doc_asociado,
    )

    print(f"   ✓ Nota de Crédito creada (CDC: {documento.CDC})")

    try:
        respuesta = client.enviar_documento(documento)

        if respuesta.aprobado:
            print(f"   ✓ Nota de Crédito aprobada!")
            print(f"   CDC: {respuesta.cdc}")
            print(f"   Protocolo: {respuesta.numero_protocolo}")
        else:
            print(f"   ✗ Nota de Crédito rechazada")
            print(f"   Código: {respuesta.codigo}")
            print(f"   Mensaje: {respuesta.mensaje}")
    except Exception as e:
        import traceback

        print(f"   ✗ Error: {e}")
        traceback.print_exc()

    print("=" * 70)


def enviar_nota_debito_ejemplo():
    """Ejemplo de envío de Nota de Débito Electrónica."""

    print("\n" + "=" * 70)
    print("Ejemplo: Nota de Débito Electrónica")
    print("=" * 70)

    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/Users/fscoscia/Girolabs/facturacion-electronica/django-sifen/JOANA NICOLE SAWATZKY VDA DE REGIER.pfx",
        certificado_contrasena="Sk59vkhu?!",
        csc="ABCD0000000000000000000000000000",
        csc_id="0001",
    )

    client = SifenClient(config)
    print("   ✓ Cliente configurado")

    import random

    codigo_seguridad = str(random.randint(100000000, 999999999))

    # Item con cargo adicional
    cantidad = Decimal("1")
    item = Item(
        dCodInt="ND001",
        dDesProSer="CARGO ADICIONAL - DOCUMENTO ELECTRÓNICO SIN VALOR COMERCIAL NI FISCAL - GENERADO EN AMBIENTE DE PRUEBA",
        cUniMed=77,
        dCantProSer=cantidad,
        gValorItem=calcular_valor_item(
            precio_unitario=Decimal("25000"),
            cantidad=cantidad,
            tasa_iva=10,
        ),
    )

    totales = calcular_totales([item])

    # Crear grupo de Nota de Débito
    nota_debito = NotaCreditoDebito(
        iMotEmi=MOTIVO_AJUSTE_PRECIO,
        dDesMotEmi=DESCRIPCIONES_MOTIVOS[MOTIVO_AJUSTE_PRECIO],
    )

    documento = DocumentoElectronico(
        dVerFor=150,
        gTimb=IdentificacionDE(
            iTiDE=TIPO_NOTA_DEBITO_ELECTRONICA,
            dDesTiDE="Nota de débito electrónica",
            dNumTim=80159272,
            dEst="001",
            dPunExp="001",
            dNumDoc="0000038",
            dFeIniT=datetime.strptime("2026-04-16", "%Y-%m-%d").date(),
        ),
        gDatGralOpe=DatosGeneralesDE(
            dFeEmiDE=datetime.now(),
            iTipEmi=1,
            dDesTipEmi="Normal",
            dCodSeg=codigo_seguridad,
            dInfoEmi="Nota de débito por cargo adicional",
            dInfoFisc="Información de interés del Fisco respecto al DE",
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
        gCamItem=[item],
        gTotSub=totales,
        gCamNCDE=nota_debito,
    )

    print(f"   ✓ Nota de Débito creada (CDC: {documento.CDC})")

    try:
        respuesta = client.enviar_documento(documento)

        if respuesta.aprobado:
            print(f"   ✓ Nota de Débito aprobada!")
            print(f"   CDC: {respuesta.cdc}")
            print(f"   Protocolo: {respuesta.numero_protocolo}")
        else:
            print(f"   ✗ Nota de Débito rechazada")
            print(f"   Código: {respuesta.codigo}")
            print(f"   Mensaje: {respuesta.mensaje}")
    except Exception as e:
        import traceback

        print(f"   ✗ Error: {e}")
        traceback.print_exc()

    print("=" * 70)


def enviar_nota_remision_ejemplo():
    """Ejemplo de envío de Nota de Remisión Electrónica."""

    print("\n" + "=" * 70)
    print("Ejemplo: Nota de Remisión Electrónica")
    print("=" * 70)

    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/Users/fscoscia/Girolabs/facturacion-electronica/django-sifen/JOANA NICOLE SAWATZKY VDA DE REGIER.pfx",
        certificado_contrasena="Sk59vkhu?!",
        csc="ABCD0000000000000000000000000000",
        csc_id="0001",
    )

    client = SifenClient(config)
    print("   ✓ Cliente configurado")

    import random

    codigo_seguridad = str(random.randint(100000000, 999999999))

    # Items para remisión
    cantidad = Decimal("20")
    item = Item(
        dCodInt="REM001",
        dDesProSer="MERCADERÍA EN TRÁNSITO - DOCUMENTO ELECTRÓNICO SIN VALOR COMERCIAL NI FISCAL - GENERADO EN AMBIENTE DE PRUEBA",
        cUniMed=77,
        dCantProSer=cantidad,
        gValorItem=calcular_valor_item(
            precio_unitario=Decimal("75000"),
            cantidad=cantidad,
            tasa_iva=10,
        ),
    )

    totales = calcular_totales([item])

    documento = DocumentoElectronico(
        dVerFor=150,
        gTimb=IdentificacionDE(
            iTiDE=TIPO_NOTA_REMISION_ELECTRONICA,
            dDesTiDE="Nota de remisión electrónica",
            dNumTim=80159272,
            dEst="001",
            dPunExp="001",
            dNumDoc="0000039",
            dFeIniT=datetime.strptime("2026-04-16", "%Y-%m-%d").date(),
        ),
        gDatGralOpe=DatosGeneralesDE(
            dFeEmiDE=datetime.now(),
            iTipEmi=1,
            dDesTipEmi="Normal",
            dCodSeg=codigo_seguridad,
            dInfoEmi="Nota de remisión para traslado de mercadería",
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
        gCamItem=[item],
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

    print(f"   ✓ Nota de Remisión creada (CDC: {documento.CDC})")

    try:
        respuesta = client.enviar_documento(documento)

        if respuesta.aprobado:
            print(f"   ✓ Nota de Remisión aprobada!")
            print(f"   CDC: {respuesta.cdc}")
            print(f"   Protocolo: {respuesta.numero_protocolo}")
        else:
            print(f"   ✗ Nota de Remisión rechazada")
            print(f"   Código: {respuesta.codigo}")
            print(f"   Mensaje: {respuesta.mensaje}")
    except Exception as e:
        import traceback

        print(f"   ✗ Error: {e}")
        traceback.print_exc()

    print("=" * 70)


def enviar_autofactura_ejemplo():
    """Ejemplo de envío de Autofactura Electrónica."""

    print("\n" + "=" * 70)
    print("Ejemplo: Autofactura Electrónica")
    print("=" * 70)

    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/Users/fscoscia/Girolabs/facturacion-electronica/django-sifen/JOANA NICOLE SAWATZKY VDA DE REGIER.pfx",
        certificado_contrasena="Sk59vkhu?!",
        csc="ABCD0000000000000000000000000000",
        csc_id="0001",
    )

    client = SifenClient(config)
    print("   ✓ Cliente configurado")

    import random

    codigo_seguridad = str(random.randint(100000000, 999999999))

    # Item para autofactura
    cantidad = Decimal("15")
    item = Item(
        dCodInt="AUTO001",
        dDesProSer="COMPRA - DOCUMENTO ELECTRÓNICO SIN VALOR COMERCIAL NI FISCAL - GENERADO EN AMBIENTE DE PRUEBA",
        cUniMed=77,
        dCantProSer=cantidad,
        gValorItem=calcular_valor_item(
            precio_unitario=Decimal("120000"),
            cantidad=cantidad,
            tasa_iva=10,
        ),
    )

    totales = calcular_totales([item])

    documento = DocumentoElectronico(
        dVerFor=150,
        gTimb=IdentificacionDE(
            iTiDE=TIPO_AUTOFACTURA_ELECTRONICA,
            dDesTiDE="Autofactura electrónica",
            dNumTim=80159272,
            dEst="001",
            dPunExp="001",
            dNumDoc="0000040",
            dFeIniT=datetime.strptime("2026-04-16", "%Y-%m-%d").date(),
        ),
        gDatGralOpe=DatosGeneralesDE(
            dFeEmiDE=datetime.now(),
            iTipEmi=1,
            dDesTipEmi="Normal",
            dCodSeg=codigo_seguridad,
            dInfoEmi="Autofactura por compra a proveedor sin factura",
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
        gCamItem=[item],
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

    print(f"   ✓ Autofactura creada (CDC: {documento.CDC})")

    try:
        respuesta = client.enviar_documento(documento)

        if respuesta.aprobado:
            print(f"   ✓ Autofactura aprobada!")
            print(f"   CDC: {respuesta.cdc}")
            print(f"   Protocolo: {respuesta.numero_protocolo}")
        else:
            print(f"   ✗ Autofactura rechazada")
            print(f"   Código: {respuesta.codigo}")
            print(f"   Mensaje: {respuesta.mensaje}")
    except Exception as e:
        import traceback

        print(f"   ✗ Error: {e}")
        traceback.print_exc()

    print("=" * 70)


if __name__ == "__main__":
    main()
