"""
Ejemplo de factura en dólares (USD) - NO factura de exportación.

Este ejemplo muestra cómo crear una factura electrónica normal (iTiDE=1)
pero con moneda en dólares americanos (USD) en lugar de guaraníes (PYG).

Casos de uso:
- Venta local pero facturada en dólares
- Cliente local que paga en dólares
- Operaciones B2B con moneda extranjera
"""

from datetime import datetime
from decimal import Decimal
import random

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
)
from sifen.utils import calcular_valor_item, calcular_totales
from sifen.models.totales import CondicionOperacion, Pago


def crear_factura_dolares():
    """
    Crea una factura electrónica en dólares (USD).

    Diferencias clave con factura en guaraníes:
    1. cMoneOpe = "USD" (en lugar de "PYG")
    2. dTiCam = tipo de cambio (ej: 7000 Gs por USD)
    3. Los montos se expresan en USD
    4. cMoneTiPag = "USD" en los pagos
    """

    print("=" * 70)
    print("FACTURA ELECTRÓNICA EN DÓLARES (USD)")
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

    # 2. Crear items en USD
    print("\n2. Creando items en USD...")

    codigo_seguridad = str(random.randint(100000000, 999999999))

    # Item 1: Producto en USD
    cantidad1 = Decimal("5")
    precio_usd_1 = Decimal("100.00")  # USD 100.00 por unidad

    item1 = Item(
        dCodInt="PROD-USD-001",
        dDesProSer="DOCUMENTO ELECTRÓNICO SIN VALOR COMERCIAL NI FISCAL - GENERADO EN AMBIENTE DE PRUEBA - Producto en USD",
        cUniMed=77,  # Unidad
        dCantProSer=cantidad1,
        gValorItem=calcular_valor_item(
            precio_unitario=precio_usd_1,
            cantidad=cantidad1,
            tasa_iva=10,  # IVA 10%
        ),
    )

    # Item 2: Servicio en USD
    cantidad2 = Decimal("2")
    precio_usd_2 = Decimal("250.00")  # USD 250.00 por unidad

    item2 = Item(
        dCodInt="SERV-USD-001",
        dDesProSer="DOCUMENTO ELECTRÓNICO SIN VALOR COMERCIAL NI FISCAL - GENERADO EN AMBIENTE DE PRUEBA - Servicio en USD",
        cUniMed=77,
        dCantProSer=cantidad2,
        gValorItem=calcular_valor_item(
            precio_unitario=precio_usd_2,
            cantidad=cantidad2,
            tasa_iva=10,
        ),
    )

    items = [item1, item2]
    print(f"   ✓ {len(items)} items creados")
    print(
        f"   - Item 1: {cantidad1} x USD {precio_usd_1} = USD {cantidad1 * precio_usd_1}"
    )
    print(
        f"   - Item 2: {cantidad2} x USD {precio_usd_2} = USD {cantidad2 * precio_usd_2}"
    )

    # 3. Calcular totales
    print("\n3. Calculando totales...")
    totales = calcular_totales(items)

    # IMPORTANTE: Configurar moneda en USD
    totales.cMoneOpe = "USD"
    # Descripción según tabla SIFEN (OBLIGATORIO para monedas != PYG)
    totales.dDesMoneOpe = "US Dollar"

    # Tipo de cambio (obligatorio cuando la moneda NO es PYG)
    tipo_cambio = Decimal("7000.00")  # 1 USD = 7000 Gs
    totales.dTiCam = tipo_cambio
    totales.dCondTiCam = Decimal("1")  # Condición de tipo de cambio (1 = Global)

    # Calcular total en guaraníes (OBLIGATORIO para monedas extranjeras)
    total_guaranies = totales.dTotGralOpe * tipo_cambio
    totales.dTotalGs = total_guaranies  # Total general en guaraníes

    print(f"   ✓ Totales calculados")
    print(f"   - Subtotal: USD {totales.dTotOpe}")
    print(f"   - IVA: USD {totales.dTotIVA}")
    print(f"   - Total: USD {totales.dTotGralOpe}")
    print(f"   - Tipo de cambio: 1 USD = Gs {tipo_cambio}")
    print(f"   - Equivalente en Gs: {total_guaranies:,.0f}")

    # 4. Crear documento
    print("\n4. Creando documento electrónico...")

    documento = DocumentoElectronico(
        dVerFor=150,
        gTimb=IdentificacionDE(
            iTiDE=1,  # Factura electrónica NORMAL (NO exportación)
            dDesTiDE="Factura electrónica",
            dNumTim=80159272,
            dEst="001",
            dPunExp="001",
            dNumDoc="0000048",  # Incrementar según tus necesidades
            dFeIniT=datetime.strptime("2026-04-16", "%Y-%m-%d").date(),
        ),
        gDatGralOpe=DatosGeneralesDE(
            dFeEmiDE=datetime.now(),
            iTipEmi=1,
            dDesTipEmi="Normal",
            dCodSeg=codigo_seguridad,
            dInfoEmi="Factura en dólares americanos",
            dInfoFisc="Información de interés del Fisco respecto al DE",
            iTipTra=1,
            dDesTipTra="Venta de mercadería",
            iTImp=1,
            dDesTImp="IVA",
            cMoneOpe="USD",  # ← CLAVE: Moneda en USD
            dDesMoneOpe="US Dollar",  # Según tabla SIFEN (obligatorio)
            dCondTiCam=Decimal("1"),  # Condición tipo cambio: 1=Global
            dTiCam=Decimal("7000.00"),  # Tipo de cambio: 1 USD = 7000 Gs
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
            iNatRec=1,  # Contribuyente
            iTiOpe=1,  # B2B
            iTiContRec=2,  # RUC
            dRucRec="80090941",
            dDVRec="0",
            dNomRec="GIROLABS SOCIEDAD ANONIMA",
        ),
        gCamItem=items,
        gTotSub=totales,
        gPaConEIni=CondicionOperacion(
            iCondOpe=1,  # Contado
            dDesCondOpe="Contado",
            gPaConEIni=[
                Pago(
                    iTiPago=1,  # Efectivo
                    dDesTiPag="Efectivo",
                    dMonTiPag=totales.dTotGralOpe,
                    cMoneTiPag="USD",  # ← CLAVE: Pago en USD
                    dDesMoneTiPag="US Dollar",  # Descripción de moneda de pago
                    dTiCamTiPag=tipo_cambio,  # Tipo de cambio para el pago
                )
            ],
        ),
    )

    print("   ✓ Documento creado")
    print(f"   CDC: {documento.CDC}")

    return client, documento


def enviar_factura_dolares():
    """Envía la factura en dólares a SIFEN."""

    client, documento = crear_factura_dolares()

    # 5. Validar documento
    print("\n5. Validando documento...")
    is_valid, error = client.validar_documento(documento)
    if is_valid:
        print("   ✓ Documento válido")
    else:
        print(f"   ✗ Documento inválido: {error}")
        return

    # 6. Generar XML para debug
    print("\n6. Generando XML...")
    xml = client.generar_xml(documento)
    # Guardar XML para inspección
    with open("/tmp/factura_usd.xml", "w") as f:
        f.write(xml)
    print(f"   XML guardado en /tmp/factura_usd.xml")

    # 7. Enviar a SIFEN
    print("\n7. Enviando documento a SIFEN...")
    try:
        respuesta = client.enviar_documento(documento)

        if respuesta.aprobado:
            print(f"   ✓ FACTURA APROBADA!")
            print(f"   CDC: {respuesta.cdc}")
            print(f"   Protocolo: {respuesta.numero_protocolo}")

            # 8. Consultar estado
            print("\n8. Consultando estado del documento...")
            consulta = client.consultar_documento(respuesta.cdc)
            print(f"   Estado: {consulta.estado}")

        else:
            print(f"   ✗ FACTURA RECHAZADA")
            print(f"   Código: {respuesta.codigo}")
            print(f"   Mensaje: {respuesta.mensaje}")
            if respuesta.xml_respuesta:
                print(f"\n   Respuesta SIFEN:\n{respuesta.xml_respuesta[:2000]}")

    except Exception as e:
        import traceback

        print(f"   ✗ Error: {e}")
        traceback.print_exc()

    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"Tipo de documento: Factura Electrónica (iTiDE=1)")
    print(f"Moneda: USD (Dólar Americano)")
    print(f"Tipo de cambio: 1 USD = Gs {documento.gTotSub.dTiCam}")
    print(f"Total USD: {documento.gTotSub.dTotGralOpe}")
    print(f"Total Gs: {documento.gTotSub.dTotGralOpe * documento.gTotSub.dTiCam:,.0f}")
    print("\nPuntos clave:")
    print("✓ NO es factura de exportación (iTiDE=1, no iTiDE=2)")
    print("✓ Moneda configurada en USD (cMoneOpe='USD')")
    print("✓ Tipo de cambio especificado (dTiCam)")
    print("✓ Pagos también en USD (cMoneTiPag='USD')")
    print("=" * 70)


def main():
    """Función principal."""

    print("\n" + "=" * 70)
    print("EJEMPLO: FACTURA EN DÓLARES (NO EXPORTACIÓN)")
    print("=" * 70)
    print("\nEste ejemplo crea una factura electrónica normal pero en USD.")
    print("Útil para ventas locales facturadas en moneda extranjera.")
    print("=" * 70)

    # Ejecutar el ejemplo
    enviar_factura_dolares()


if __name__ == "__main__":
    main()
