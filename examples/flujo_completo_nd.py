"""
Ejemplo de flujo completo: Factura + Nota de Débito

Este ejemplo muestra cómo:
1. Enviar una factura
2. Guardar su CDC
3. Crear una nota de débito que referencia esa factura
"""

from decimal import Decimal
from datetime import datetime
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
    NotaCreditoDebito,
    DocumentoAsociado,
)
from sifen.utils import calcular_valor_item, calcular_totales
from sifen.models.totales import CondicionOperacion, Pago
from sifen.models.nota_credito_debito import MOTIVO_RECUPERO_COSTO, DESCRIPCIONES_MOTIVOS
from sifen.models.documento_asociado import (
    TIPO_DOC_ASOCIADO_ELECTRONICO,
    DESCRIPCIONES_TIPO_DOC_ASOCIADO,
)
from sifen.constants import TIPO_FACTURA_ELECTRONICA, TIPO_NOTA_DEBITO_ELECTRONICA
import random


def main():
    """Flujo completo de factura + nota de débito."""

    print("\n" + "=" * 70)
    print("FLUJO COMPLETO: FACTURA + NOTA DE DÉBITO")
    print("=" * 70)

    # Configurar cliente
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/Users/fscoscia/Girolabs/facturacion-electronica/django-sifen/JOANA NICOLE SAWATZKY VDA DE REGIER.pfx",
        certificado_contrasena="Sk59vkhu?!",
        csc="ABCD0000000000000000000000000000",
        csc_id="0001",
    )

    client = SifenClient(config)

    # ========================================
    # PASO 1: ENVIAR FACTURA ORIGINAL
    # ========================================
    print("\n" + "=" * 70)
    print("PASO 1: Enviando Factura Original")
    print("=" * 70)

    # Crear item
    item_factura = Item(
        dCodInt="PROD001",
        dDesProSer="PRODUCTO DE PRUEBA - SIN VALOR COMERCIAL",
        cUniMed=77,
        dCantProSer=Decimal("5"),
        gValorItem=calcular_valor_item(
            precio_unitario=Decimal("100000"),
            cantidad=Decimal("5"),
            tasa_iva=10,
        ),
    )

    totales_factura = calcular_totales([item_factura])

    # Crear factura
    factura = DocumentoElectronico(
        dVerFor=150,
        gTimb=IdentificacionDE(
            iTiDE=TIPO_FACTURA_ELECTRONICA,
            dDesTiDE="Factura electrónica",
            dNumTim=80159272,
            dEst="001",
            dPunExp="001",
            dNumDoc="0000046",
            dFeIniT=datetime.strptime("2026-04-16", "%Y-%m-%d").date(),
        ),
        gDatGralOpe=DatosGeneralesDE(
            dFeEmiDE=datetime.now(),
            iTipEmi=1,
            dDesTipEmi="Normal",
            dCodSeg=str(random.randint(100000000, 999999999)),
            dInfoEmi="Factura de prueba",
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
        gCamItem=[item_factura],
        gTotSub=totales_factura,
        gPaConEIni=CondicionOperacion(
            iCondOpe=1,
            dDesCondOpe="Contado",
            gPaConEIni=[
                Pago(
                    iTiPago=1,
                    dDesTiPag="Efectivo",
                    dMonTiPag=totales_factura.dTotGralOpe,
                )
            ],
        ),
    )

    print(f"\n✓ Factura creada")
    print(f"  Número: 001-001-0000046")
    print(f"  Total: Gs. {totales_factura.dTotGralOpe:,.0f}")

    # Enviar factura
    print(f"\nEnviando factura a SIFEN...")
    try:
        respuesta_factura = client.enviar_documento(factura)

        if respuesta_factura.aprobado:
            cdc_factura = respuesta_factura.cdc
            print(f"\n✓ FACTURA APROBADA!")
            print(f"  CDC: {cdc_factura}")
            print(f"  Protocolo: {respuesta_factura.numero_protocolo}")

            # ========================================
            # PASO 2: CREAR NOTA DE DÉBITO
            # ========================================
            print("\n" + "=" * 70)
            print("PASO 2: Creando Nota de Débito")
            print("=" * 70)
            print(f"\nReferenciando factura con CDC: {cdc_factura}")

            # Crear item de ND (cargo adicional por recupero de costo)
            item_nd = Item(
                dCodInt="CARGO001",
                dDesProSer="CARGO POR RECUPERO DE COSTO - FLETE",
                cUniMed=77,
                dCantProSer=Decimal("1"),
                gValorItem=calcular_valor_item(
                    precio_unitario=Decimal("50000"),
                    cantidad=Decimal("1"),
                    tasa_iva=10,
                ),
            )

            totales_nd = calcular_totales([item_nd])

            # Crear grupo de Nota de Débito
            nota_debito = NotaCreditoDebito(
                iMotEmi=MOTIVO_RECUPERO_COSTO,
                dDesMotEmi=DESCRIPCIONES_MOTIVOS[MOTIVO_RECUPERO_COSTO],
            )

            # IMPORTANTE: Referenciar la factura original usando su CDC
            doc_asociado = DocumentoAsociado(
                iTipDocAso=TIPO_DOC_ASOCIADO_ELECTRONICO,
                dDesTipDocAso=DESCRIPCIONES_TIPO_DOC_ASOCIADO[
                    TIPO_DOC_ASOCIADO_ELECTRONICO
                ],
                dCdCDERef=cdc_factura,  # ← CDC de la factura que acabamos de enviar
            )

            # Crear nota de débito
            nd = DocumentoElectronico(
                dVerFor=150,
                gTimb=IdentificacionDE(
                    iTiDE=TIPO_NOTA_DEBITO_ELECTRONICA,
                    dDesTiDE="Nota de débito electrónica",
                    dNumTim=80159272,
                    dEst="001",
                    dPunExp="001",
                    dNumDoc="0000047",
                    dFeIniT=datetime.strptime("2026-04-16", "%Y-%m-%d").date(),
                ),
                gDatGralOpe=DatosGeneralesDE(
                    dFeEmiDE=datetime.now(),
                    iTipEmi=1,
                    dDesTipEmi="Normal",
                    dCodSeg=str(random.randint(100000000, 999999999)),
                    dInfoEmi="Nota de débito por recupero de costo",
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
                gCamItem=[item_nd],
                gTotSub=totales_nd,
                gCamNCDE=nota_debito,
                gCamDEAsoc=doc_asociado,  # ← Referencia a la factura original
            )

            print(f"\n✓ Nota de Débito creada")
            print(f"  Número: 001-001-0000047")
            print(f"  Motivo: {DESCRIPCIONES_MOTIVOS[MOTIVO_RECUPERO_COSTO]}")
            print(f"  Total: Gs. {totales_nd.dTotGralOpe:,.0f}")

            # Enviar nota de débito
            print(f"\nEnviando Nota de Débito a SIFEN...")
            respuesta_nd = client.enviar_documento(nd)

            if respuesta_nd.aprobado:
                print(f"\n✓ NOTA DE DÉBITO APROBADA!")
                print(f"  CDC: {respuesta_nd.cdc}")
                print(f"  Protocolo: {respuesta_nd.numero_protocolo}")

                # Resumen
                print("\n" + "=" * 70)
                print("RESUMEN DEL FLUJO")
                print("=" * 70)
                print(f"\n1. Factura Original:")
                print(f"   CDC: {cdc_factura}")
                print(f"   Total: Gs. {totales_factura.dTotGralOpe:,.0f}")
                print(f"\n2. Nota de Débito:")
                print(f"   CDC: {respuesta_nd.cdc}")
                print(f"   Total: Gs. {totales_nd.dTotGralOpe:,.0f}")
                print(f"\n3. Saldo Final:")
                print(
                    f"   Gs. {totales_factura.dTotGralOpe + totales_nd.dTotGralOpe:,.0f}"
                )
                print("=" * 70)
            else:
                print(f"\n✗ Nota de Débito rechazada")
                print(f"  Código: {respuesta_nd.codigo}")
                print(f"  Mensaje: {respuesta_nd.mensaje}")
        else:
            print(f"\n✗ Factura rechazada")
            print(f"  Código: {respuesta_factura.codigo}")
            print(f"  Mensaje: {respuesta_factura.mensaje}")
            print(f"\n  No se puede continuar sin una factura aprobada")

    except Exception as e:
        import traceback

        print(f"\n✗ Error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
