"""
Ejemplo de flujo completo: Nota de Remisión Electrónica

Este ejemplo muestra cómo:
1. Crear una nota de remisión para traslado de mercaderías
2. Especificar el motivo de emisión y responsable
3. Incluir información de transporte (opcional)
"""

from decimal import Decimal
from datetime import datetime, date
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
    NotaRemision,
    Transporte,
    LocalSalida,
    LocalEntrega,
    VehiculoTraslado,
    Transportista,
)
from sifen.models.totales import Totales
from sifen.models.nota_remision import (
    MOTIVO_TRASLADO_LOCALES,
    RESPONSABLE_EMISOR,
    DESCRIPCIONES_MOTIVO,
    DESCRIPCIONES_RESPONSABLE,
)
from sifen.models.transporte import (
    TIPO_TRANSPORTE_PROPIO,
    MODALIDAD_TERRESTRE,
    RESPONSABLE_FLETE_EMISOR,
    DESCRIPCIONES_TIPO_TRANSPORTE,
    DESCRIPCIONES_MODALIDAD,
)
from sifen.constants import TIPO_NOTA_REMISION_ELECTRONICA
import random


def main():
    """Flujo completo de nota de remisión."""

    print("\n" + "=" * 70)
    print("FLUJO COMPLETO: NOTA DE REMISIÓN ELECTRÓNICA")
    print("=" * 70)
    print("\nLa nota de remisión se usa para documentar el traslado de mercaderías")
    print("sin que implique una venta inmediata.")

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
    # PASO 1: CREAR NOTA DE REMISIÓN
    # ========================================
    print("\n" + "=" * 70)
    print("PASO 1: Creando Nota de Remisión")
    print("=" * 70)

    # Crear items (productos a trasladar)
    # Para nota de remisión NO se incluye gValorItem (valores comerciales)
    cantidad = Decimal("10")

    item = Item(
        dCodInt="PROD001",
        dDesProSer="PRODUCTO PARA TRASLADO - SIN VALOR COMERCIAL",
        cUniMed=77,
        dCantProSer=cantidad,
    )

    # Totales para nota de remisión (no se envían a SIFEN, solo para referencia interna)
    totales = Totales(
        dTotOpe=Decimal("0"),
        dTotDesc=Decimal("0"),
        dTotDescGlotem=Decimal("0"),
        dTotAntItem=Decimal("0"),
        dTotAnt=Decimal("0"),
        dPorcDescTotal=Decimal("0"),
        dDescTotal=Decimal("0"),
        dAnticipo=Decimal("0"),
        dRedon=Decimal("0"),
        dTotIVA=Decimal("0"),
        dTotGralOpe=Decimal("0"),
    )

    # Crear grupo de Nota de Remisión
    nota_remision = NotaRemision(
        # Motivo de emisión
        iMotEmiNR=MOTIVO_TRASLADO_LOCALES,
        dDesMotEmiNR=DESCRIPCIONES_MOTIVO[MOTIVO_TRASLADO_LOCALES],
        # Responsable de la emisión
        iRespEmiNR=RESPONSABLE_EMISOR,
        dDesRespEmiNR=DESCRIPCIONES_RESPONSABLE[RESPONSABLE_EMISOR],
        # Kilómetros estimados (opcional)
        dKmR="150",
        # Fecha futura de emisión de factura (opcional)
        # Se informa cuando no se ha emitido aún la factura electrónica
        # dFecEm=date(2026, 6, 15),
    )

    # Crear grupo de Transporte
    from datetime import date, timedelta

    hoy = date.today()

    # Local de salida (mismo que el emisor)
    local_salida = LocalSalida(
        dDirLocSal="Av. Principal 123",
        dNumCasSal=123,
        cDepSal=16,
        dDesDepSal="BOQUERON",
        cCiuSal=6413,
        dDesCiuSal="COL.FERNHEIN",
    )

    # Local de entrega
    local_entrega = LocalEntrega(
        dDirLocEnt="Av. Secundaria 456",
        dNumCasEnt=456,
        cDepEnt=16,
        dDesDepEnt="BOQUERON",
        cCiuEnt=6413,
        dDesCiuEnt="COL.FERNHEIN",
    )

    # Vehículo de traslado
    vehiculo = VehiculoTraslado(
        dTiVehTras="Camión",
        dMarVeh="Mercedes",
        dTipIdenVeh=1,  # 1=Número de identificación, 2=Número de matrícula
        dNroIDVeh="ABC123",
    )

    # Transportista
    transportista = Transportista(
        iNatTrans=1,  # 1=Contribuyente, 2=No contribuyente
        dNomTrans="Transportes S.A.",
        dNumIDChof="1234567",
        dNomChof="Juan Pérez",
        dRucTrans="80159272",
        dDVTrans="0",
        dDomFisc="Av. Transportistas 123",
        dDirChof="Calle Chofer 456",
    )

    transporte = Transporte(
        # Tipo de transporte
        iTipTrans=TIPO_TRANSPORTE_PROPIO,
        dDesTipTrans=DESCRIPCIONES_TIPO_TRANSPORTE[TIPO_TRANSPORTE_PROPIO],
        # Modalidad del transporte
        iModTrans=MODALIDAD_TERRESTRE,
        dDesModTrans=DESCRIPCIONES_MODALIDAD[MODALIDAD_TERRESTRE],
        # Responsable del costo del flete
        iRespFlete=RESPONSABLE_FLETE_EMISOR,
        # Fechas de traslado (obligatorias para nota de remisión)
        dIniTras=hoy,
        dFinTras=hoy + timedelta(days=1),
        # Locales
        gCamSal=local_salida,
        gCamEnt=[local_entrega],
        # Vehículos
        gVehTras=[vehiculo],
        # Transportista
        gCamTrans=transportista,
    )

    # Crear la nota de remisión
    nre = DocumentoElectronico(
        dVerFor=150,
        gTimb=IdentificacionDE(
            iTiDE=TIPO_NOTA_REMISION_ELECTRONICA,
            dDesTiDE="Nota de remisión electrónica",
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
            dInfoEmi="Nota de remisión para traslado de mercaderías",
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
            cPaisRec="PRY",
            dDesPaisRe="Paraguay",
            iTiContRec=2,
            dRucRec="80159272",
            dDVRec="0",
            dNomRec="DE generado en ambiente de prueba - sin valor comercial ni fiscal",
            dDirRec="Av. Secundaria 456",
            dNumCasRec=456,
            cDepRec=16,
            dDesDepRec="BOQUERON",
            cDisRec=259,
            dDesDisRec="FILADELFIA",
            cCiuRec=6413,
            dDesCiuRec="COL.FERNHEIN",
        ),
        gCamItem=[item],
        gTotSub=totales,
        gCamNRE=nota_remision,
        gTransp=transporte,
    )

    print("\n✓ Nota de Remisión creada")
    print("  Número: 001-001-0000001")
    print(f"  Motivo: {nota_remision.dDesMotEmiNR}")
    print(f"  Responsable: {nota_remision.dDesRespEmiNR}")
    if nota_remision.dKmR:
        print(f"  Kilómetros estimados: {nota_remision.dKmR} km")
    print(f"  Cantidad de ítems: {len([item])}")

    # Enviar nota de remisión
    print(f"\nEnviando Nota de Remisión a SIFEN...")
    try:
        respuesta = client.enviar_documento(nre)

        if respuesta.aprobado:
            print(f"\n✓ NOTA DE REMISIÓN APROBADA!")
            print(f"  CDC: {respuesta.cdc}")
            print(f"  Protocolo: {respuesta.numero_protocolo}")

            # Resumen
            print("\n" + "=" * 70)
            print("RESUMEN")
            print("=" * 70)
            print(f"\n1. Emisor:")
            print(f"   RUC: 80159272-0")
            print(f"\n2. Receptor:")
            print(f"   RUC: 80000000-1")
            print(f"   Nombre: CLIENTE DE PRUEBA S.A.")
            print(f"\n3. Traslado:")
            print(f"   Motivo: {nota_remision.dDesMotEmiNR}")
            print(f"   Responsable: {nota_remision.dDesRespEmiNR}")
            if nota_remision.dKmR:
                print(f"   Distancia: {nota_remision.dKmR} km")
            print(f"   Total: Gs. {totales.dTotGralOpe:,.0f}")
            print(f"   CDC: {respuesta.cdc}")
            print("=" * 70)
        else:
            print(f"\n✗ Nota de Remisión rechazada")
            print(f"  Código: {respuesta.codigo}")
            print(f"  Mensaje: {respuesta.mensaje}")

    except Exception as e:
        import traceback

        print(f"\n✗ Error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
