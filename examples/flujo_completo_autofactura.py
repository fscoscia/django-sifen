"""
Ejemplo de flujo completo: Autofactura Electrónica

Este ejemplo muestra cómo:
1. Crear una autofactura para compra a un no contribuyente
2. Incluir los datos del vendedor (proveedor sin factura)
3. Referenciar una constancia de no contribuyente
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
    Autofactura,
    DocumentoAsociado,
)
from sifen.utils import calcular_valor_item, calcular_totales
from sifen.models.totales import CondicionOperacion, Pago
from sifen.models.autofactura import (
    NATURALEZA_NO_CONTRIBUYENTE,
    TIPO_DOC_CEDULA_PARAGUAYA,
    DESCRIPCIONES_NATURALEZA,
    DESCRIPCIONES_TIPO_DOC,
)
from sifen.models.documento_asociado import (
    TIPO_DOC_ASOCIADO_CONSTANCIA,
    TIPO_CONSTANCIA_NO_CONTRIBUYENTE,
    DESCRIPCIONES_TIPO_DOC_ASOCIADO,
    DESCRIPCIONES_TIPO_CONSTANCIA,
)
from sifen.constants import TIPO_AUTOFACTURA_ELECTRONICA
import random


def main():
    """Flujo completo de autofactura."""

    print("\n" + "=" * 70)
    print("FLUJO COMPLETO: AUTOFACTURA ELECTRÓNICA")
    print("=" * 70)
    print("\nLa autofactura se usa cuando compras a un proveedor que no emite")
    print("factura (ej: productor agrícola, no contribuyente, etc.)")

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
    # PASO 1: CREAR AUTOFACTURA
    # ========================================
    print("\n" + "=" * 70)
    print("PASO 1: Creando Autofactura")
    print("=" * 70)

    # Crear item (producto comprado al no contribuyente)
    # IMPORTANTE: Para autofacturas NO se calcula IVA
    # El cálculo es simplemente: precio unitario × cantidad (E721 * E711)
    from sifen.models.items import ValorItem

    precio_unitario = Decimal("5000")
    cantidad = Decimal("100")
    total_item = precio_unitario * cantidad  # 500,000

    item = Item(
        dCodInt="PROD001",
        dDesProSer="COMPRA DE PRODUCTOS AGRÍCOLAS - SIN VALOR COMERCIAL",
        cUniMed=77,
        dCantProSer=cantidad,
        gValorItem=ValorItem(
            dPUniProSer=precio_unitario,  # E701 - Precio unitario
            dTotOpeItem=total_item,  # E710 - Total operación = precio × cantidad
            # NO incluir gCamIVA para autofacturas
        ),
    )

    # Para autofacturas, los totales NO incluyen desglose de IVA
    from sifen.models.totales import Totales

    totales = Totales(
        dTotOpe=total_item,  # F005 - Total de la operación
        dTotDesc=Decimal("0"),  # F006 - Total de descuentos
        dTotDescGlotem=Decimal("0"),  # Total de descuentos globales por ítem
        dTotAntItem=Decimal("0"),  # Total de anticipos por ítem
        dTotAnt=Decimal("0"),  # F007 - Total de anticipos
        dPorcDescTotal=Decimal("0"),  # Porcentaje de descuento total
        dDescTotal=Decimal("0"),  # Descuento total
        dAnticipo=Decimal("0"),  # Anticipo
        dRedon=Decimal("0"),  # Redondeo
        dTotIVA=Decimal("0"),  # F009 - Total IVA (0 para autofacturas)
        dTotGralOpe=total_item,  # F013 - Total general = total operación (sin IVA)
        # NO incluir gCamIVA para autofacturas
    )

    # Crear grupo de Autofactura con datos del vendedor
    autofactura = Autofactura(
        # Naturaleza del vendedor
        iNatVen=NATURALEZA_NO_CONTRIBUYENTE,
        dDesNatVen=DESCRIPCIONES_NATURALEZA[NATURALEZA_NO_CONTRIBUYENTE],
        # Documento de identidad del vendedor
        iTipIDVen=TIPO_DOC_CEDULA_PARAGUAYA,
        dDTipIDVen=DESCRIPCIONES_TIPO_DOC[TIPO_DOC_CEDULA_PARAGUAYA],
        dNumIDVen="9999999",  # Cédula del vendedor (no debe ser RUC activo)
        # Datos del vendedor
        dNomVen="Juan Pérez Productor",
        dDirVen="Ruta 9 Km 45, Colonia Agrícola",
        dNumCasVen=0,  # Sin número de casa
        # Ubicación del vendedor (opcional pero recomendado)
        cDepVen=16,  # Boquerón
        dDesDepVen="BOQUERON",
        cDisVen=259,  # Filadelfia
        dDesDisVen="FILADELFIA",
        cCiuVen=6413,  # Col. Fernheim
        dDesCiuVen="COL.FERNHEIN",
        # Lugar donde se realizó la transacción
        dDirProv="Ruta 9 Km 45, Colonia Agrícola",
        cDepProv=16,
        dDesDepProv="BOQUERON",
        cDisProv=259,
        dDesDisProv="FILADELFIA",
        cCiuProv=6413,
        dDesCiuProv="COL.FERNHEIN",
    )

    # Crear documento asociado (constancia de no contribuyente)
    # NOTA: dNumCons y dNumControl son opcionales según el XSD
    doc_asociado = DocumentoAsociado(
        iTipDocAso=TIPO_DOC_ASOCIADO_CONSTANCIA,
        dDesTipDocAso=DESCRIPCIONES_TIPO_DOC_ASOCIADO[TIPO_DOC_ASOCIADO_CONSTANCIA],
        iTipCons=TIPO_CONSTANCIA_NO_CONTRIBUYENTE,
        dDesTipCons=DESCRIPCIONES_TIPO_CONSTANCIA[TIPO_CONSTANCIA_NO_CONTRIBUYENTE],
        # dNumCons y dNumControl son opcionales
    )

    # Crear la autofactura
    afe = DocumentoElectronico(
        dVerFor=150,
        gTimb=IdentificacionDE(
            iTiDE=TIPO_AUTOFACTURA_ELECTRONICA,  # 4
            dDesTiDE="Autofactura electrónica",
            dNumTim=80159272,
            dEst="001",
            dPunExp="001",
            dNumDoc="0000001",
            dFeIniT=datetime.strptime("2026-04-16", "%Y-%m-%d").date(),
        ),
        gDatGralOpe=DatosGeneralesDE(
            dFeEmiDE=datetime.now(),
            iTipEmi=1,
            dDesTipEmi="Normal",
            dCodSeg=str(random.randint(100000000, 999999999)),
            dInfoEmi="Autofactura por compra a no contribuyente",
            dInfoFisc="Información de interés del Fisco respecto al DE",
            # Para autofactura, iTipTra es requerido
            iTipTra=1,
            dDesTipTra="Venta de mercadería",
            iTImp=1,
            dDesTImp="IVA",
            cMoneOpe="PYG",
            dDesMoneOpe="guarani",
        ),
        gEmis=Emisor(
            # El emisor es quien COMPRA (el que emite la autofactura)
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
            # IMPORTANTE: Para autofacturas según manual SIFEN:
            # - RUC del receptor = RUC del emisor
            # - iNatRec = 1 (Contribuyente) - Error 1315
            # - iTiOpe = 2 (B2C) - Error 1316
            # - iTiContRec = 1 (No contribuyente) - Error 1302 (obligatorio)
            iNatRec=1,  # 1 = Contribuyente (requisito para autofacturas)
            iTiOpe=2,  # 2 = B2C (requisito para autofacturas)
            iTiContRec=1,  # 1 = No contribuyente (obligatorio)
            dRucRec="80159272",  # Mismo RUC que el emisor
            dDVRec="0",
            dNomRec="DE generado en ambiente de prueba - sin valor comercial ni fiscal",
        ),
        gCamItem=[item],
        gTotSub=totales,
        gCamAE=autofactura,  # ← Grupo de autofactura con datos del vendedor
        gCamDEAsoc=doc_asociado,  # ← Referencia a constancia
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

    print(f"\n✓ Autofactura creada")
    print(f"  Número: 001-001-0000048")
    print(f"  Vendedor: {autofactura.dNomVen}")
    print(f"  Cédula: {autofactura.dNumIDVen}")
    print(f"  Total: Gs. {totales.dTotGralOpe:,.0f}")

    # Enviar autofactura
    print(f"\nEnviando Autofactura a SIFEN...")
    try:
        respuesta = client.enviar_documento(afe)

        if respuesta.aprobado:
            print(f"\n✓ AUTOFACTURA APROBADA!")
            print(f"  CDC: {respuesta.cdc}")
            print(f"  Protocolo: {respuesta.numero_protocolo}")

            # Resumen
            print("\n" + "=" * 70)
            print("RESUMEN")
            print("=" * 70)
            print(f"\n1. Comprador (Emisor de la autofactura):")
            print(f"   RUC: 80159272-0")
            print(f"\n2. Vendedor (Proveedor sin factura):")
            print(f"   Nombre: {autofactura.dNomVen}")
            print(f"   Cédula: {autofactura.dNumIDVen}")
            print(f"   Naturaleza: {autofactura.dDesNatVen}")
            print(f"\n3. Transacción:")
            print(f"   Total: Gs. {totales.dTotGralOpe:,.0f}")
            print(f"   CDC: {respuesta.cdc}")
            print("=" * 70)
        else:
            print(f"\n✗ Autofactura rechazada")
            print(f"  Código: {respuesta.codigo}")
            print(f"  Mensaje: {respuesta.mensaje}")

    except Exception as e:
        import traceback

        print(f"\n✗ Error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
