"""
Ejemplo de flujo completo: Factura + Nota de Crédito

Este ejemplo muestra cómo:
1. Enviar una factura
2. Guardar su CDC
3. Crear una nota de crédito que referencia esa factura
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
from sifen.models.nota_credito_debito import MOTIVO_DEVOLUCION, DESCRIPCIONES_MOTIVOS
from sifen.models.documento_asociado import (
    TIPO_DOC_ASOCIADO_ELECTRONICO,
    DESCRIPCIONES_TIPO_DOC_ASOCIADO,
)
from sifen.constants import TIPO_FACTURA_ELECTRONICA, TIPO_NOTA_CREDITO_ELECTRONICA
import random


def main():
    """Flujo completo de factura + nota de crédito."""

    print("\n" + "=" * 70)
    print("FLUJO COMPLETO: FACTURA + NOTA DE CRÉDITO")
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
            dNumDoc="0000101",
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
    print(f"  Número: 001-001-0000040")
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
            # PASO 2: CREAR NOTA DE CRÉDITO
            # ========================================
            print("\n" + "=" * 70)
            print("PASO 2: Creando Nota de Crédito")
            print("=" * 70)
            print(f"\nReferenciando factura con CDC: {cdc_factura}")

            # Crear item de NC (mismo producto, devolución parcial)
            item_nc = Item(
                dCodInt="PROD001",
                dDesProSer="DEVOLUCIÓN - PRODUCTO DE PRUEBA",
                cUniMed=77,
                dCantProSer=Decimal("2"),  # Devolviendo 2 de 5
                gValorItem=calcular_valor_item(
                    precio_unitario=Decimal("100000"),
                    cantidad=Decimal("2"),
                    tasa_iva=10,
                ),
            )

            totales_nc = calcular_totales([item_nc])

            # Crear grupo de Nota de Crédito
            nota_credito = NotaCreditoDebito(
                iMotEmi=MOTIVO_DEVOLUCION,
                dDesMotEmi=DESCRIPCIONES_MOTIVOS[MOTIVO_DEVOLUCION],
            )

            # IMPORTANTE: Referenciar la factura original usando su CDC
            doc_asociado = DocumentoAsociado(
                iTipDocAso=TIPO_DOC_ASOCIADO_ELECTRONICO,
                dDesTipDocAso=DESCRIPCIONES_TIPO_DOC_ASOCIADO[
                    TIPO_DOC_ASOCIADO_ELECTRONICO
                ],
                dCdCDERef=cdc_factura,  # ← CDC de la factura que acabamos de enviar
            )

            # Crear nota de crédito
            nc = DocumentoElectronico(
                dVerFor=150,
                gTimb=IdentificacionDE(
                    iTiDE=TIPO_NOTA_CREDITO_ELECTRONICA,
                    dDesTiDE="Nota de crédito electrónica",
                    dNumTim=80159272,
                    dEst="001",
                    dPunExp="001",
                    dNumDoc="0000041",
                    dFeIniT=datetime.strptime("2026-04-16", "%Y-%m-%d").date(),
                ),
                gDatGralOpe=DatosGeneralesDE(
                    dFeEmiDE=datetime.now(),
                    iTipEmi=1,
                    dDesTipEmi="Normal",
                    dCodSeg=str(random.randint(100000000, 999999999)),
                    dInfoEmi="Nota de crédito por devolución parcial",
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
                gCamItem=[item_nc],
                gTotSub=totales_nc,
                gCamNCDE=nota_credito,
                gCamDEAsoc=doc_asociado,  # ← Referencia a la factura original
            )

            print(f"\n✓ Nota de Crédito creada")
            print(f"  Número: 001-001-0000041")
            print(f"  Motivo: {DESCRIPCIONES_MOTIVOS[MOTIVO_DEVOLUCION]}")
            print(f"  Total: Gs. {totales_nc.dTotGralOpe:,.0f}")

            # Enviar nota de crédito
            print(f"\nEnviando Nota de Crédito a SIFEN...")
            respuesta_nc = client.enviar_documento(nc)

            if respuesta_nc.aprobado:
                print(f"\n✓ NOTA DE CRÉDITO APROBADA!")
                print(f"  CDC: {respuesta_nc.cdc}")
                print(f"  Protocolo: {respuesta_nc.numero_protocolo}")

                # Resumen
                print("\n" + "=" * 70)
                print("RESUMEN DEL FLUJO")
                print("=" * 70)
                print(f"\n1. Factura Original:")
                print(f"   CDC: {cdc_factura}")
                print(f"   Total: Gs. {totales_factura.dTotGralOpe:,.0f}")
                print(f"\n2. Nota de Crédito:")
                print(f"   CDC: {respuesta_nc.cdc}")
                print(f"   Total: Gs. {totales_nc.dTotGralOpe:,.0f}")
                print(f"\n3. Saldo Final:")
                print(
                    f"   Gs. {totales_factura.dTotGralOpe - totales_nc.dTotGralOpe:,.0f}"
                )
                print("=" * 70)
            else:
                print(f"\n✗ Nota de Crédito rechazada")
                print(f"  Código: {respuesta_nc.codigo}")
                print(f"  Mensaje: {respuesta_nc.mensaje}")
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
