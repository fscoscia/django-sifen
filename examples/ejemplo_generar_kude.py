"""
Ejemplo de generación de KuDE (representación gráfica en PDF).

Este ejemplo muestra cómo generar el KuDE de un documento electrónico
después de ser aprobado por SIFEN.
"""

import os
from decimal import Decimal
from datetime import datetime

from sifen import SifenClient
from sifen.config import SifenConfig, TipoAmbiente
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


def crear_documento_ejemplo():
    """Crea un documento electrónico de ejemplo."""
    
    # Fecha de emisión
    fecha_emision = datetime.now()
    
    # A - Identificación del DE
    identificacion = IdentificacionDE(
        iTiDE=1,  # Factura electrónica
        dDesTiDE="Factura electrónica",
        dNumTim="12345678",
        dEst="001",
        dPunExp="001",
        dNumDoc="0000001",
        dFeIniT="2024-01-01",
    )
    
    # B - Datos generales
    datos_generales = DatosGeneralesDE(
        dFeEmiDE=fecha_emision,
        iTipEmi=1,
        dCodSeg="123456789",
    )
    
    # D - Emisor
    emisor = Emisor(
        dRucEm="80012345",
        dDVEmi=6,
        iTipCont=1,
        dNomEmi="Empresa Demo S.A.",
        dNomFanEmi="Demo Store",
        dDirEmi="Av. Principal 1234",
        dNumCas=1234,
        cDepEmi=11,
        dDesDepEmi="Central",
        cDisEmi=1,
        dDesDisEmi="Asunción",
        cCiuEmi=1,
        dDesCiuEmi="Asunción",
        dTelEmi="021123456",
        dEmailE="contacto@demo.com.py",
        gActEco=[
            ActividadEconomica(
                cActEco="47190",
                dDesActEco="Venta al por menor en comercios no especializados"
            )
        ]
    )
    
    # E - Receptor
    receptor = Receptor(
        iNatRec=1,
        iTiOpe=1,
        dNomRec="Cliente Demo",
        dRucRec="1234567",
        dDVRec="8",
        dDirRec="Calle Ejemplo 456",
        cDepRec=11,
        dDesDepRec="Central",
        cDisRec=1,
        dDesDisRec="Asunción",
        cCiuRec=1,
        dDesCiuRec="Asunción",
        dTelRec="0981234567",
        dEmailRec="cliente@example.com",
    )
    
    # E - Items
    items = []
    
    # Item 1: Producto gravado 10%
    item1 = Item(
        dCodInt="PROD001",
        dDesProSer="Notebook HP 15-DY2021LA",
        cUniMed=77,
        dDesUniMed="Unidad",
        dCantProSer=Decimal("1"),
        gValorItem=ValorItem(
            dPUniProSer=Decimal("5000000"),
            dTotOpeItem=Decimal("5000000"),
            gCamIVA=IVAItem(
                iAfecIVA=1,
                dDesAfecIVA="Gravado IVA",
                dPropIVA=Decimal("100"),
                dTasaIVA=Decimal("10"),
                dBasGravIVA=Decimal("4545454.55"),
                dLiqIVAItem=Decimal("454545.45"),
            )
        )
    )
    items.append(item1)
    
    # Item 2: Producto gravado 5%
    item2 = Item(
        dCodInt="PROD002",
        dDesProSer="Mouse Inalámbrico Logitech",
        cUniMed=77,
        dDesUniMed="Unidad",
        dCantProSer=Decimal("2"),
        gValorItem=ValorItem(
            dPUniProSer=Decimal("150000"),
            dTotOpeItem=Decimal("300000"),
            gCamIVA=IVAItem(
                iAfecIVA=1,
                dDesAfecIVA="Gravado IVA",
                dPropIVA=Decimal("100"),
                dTasaIVA=Decimal("5"),
                dBasGravIVA=Decimal("285714.29"),
                dLiqIVAItem=Decimal("14285.71"),
            )
        )
    )
    items.append(item2)
    
    # Item 3: Producto exento
    item3 = Item(
        dCodInt="PROD003",
        dDesProSer="Libro de Programación Python",
        cUniMed=77,
        dDesUniMed="Unidad",
        dCantProSer=Decimal("1"),
        gValorItem=ValorItem(
            dPUniProSer=Decimal("200000"),
            dTotOpeItem=Decimal("200000"),
            gCamIVA=IVAItem(
                iAfecIVA=2,
                dDesAfecIVA="Exento",
                dPropIVA=Decimal("100"),
                dTasaIVA=Decimal("0"),
                dBasGravIVA=Decimal("0"),
                dLiqIVAItem=Decimal("0"),
            )
        )
    )
    items.append(item3)
    
    # F - Totales
    totales = Totales(
        dSubExe=Decimal("200000"),
        dSub5=Decimal("300000"),
        dSub10=Decimal("5000000"),
        dTotOpe=Decimal("5500000"),
        dTotIVA=Decimal("468831.16"),
        dBaseGrav5=Decimal("285714.29"),
        dBaseGrav10=Decimal("4545454.55"),
        dLiqTotIVA5=Decimal("14285.71"),
        dLiqTotIVA10=Decimal("454545.45"),
        dTotGralOpe=Decimal("5500000"),
        cMoneOpe="PYG",
        dDesMoneOpe="Guaraní",
        gCamIVA=[
            SubtotalIVA(
                iAfecIVA=1,
                dDesAfecIVA="Gravado IVA 5%",
                dBasGravIVA=Decimal("285714.29"),
                dLiqIVA=Decimal("14285.71"),
                dTasaIVA=Decimal("5"),
            ),
            SubtotalIVA(
                iAfecIVA=1,
                dDesAfecIVA="Gravado IVA 10%",
                dBasGravIVA=Decimal("4545454.55"),
                dLiqIVA=Decimal("454545.45"),
                dTasaIVA=Decimal("10"),
            ),
        ]
    )
    
    # Condición de operación (contado)
    condicion = CondicionOperacion(
        iCondOpe=1,
        dDesCondOpe="Contado",
        gPaConEIni=[
            Pago(
                iTiPago=1,
                dDesTiPag="Efectivo",
                dMonTiPag=Decimal("5500000"),
                cMoneTiPag="PYG",
                dDesMoneTiPag="Guaraní",
            )
        ]
    )
    
    # Crear documento
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
    
    return documento


def main():
    """Función principal del ejemplo."""
    
    print("=" * 80)
    print("EJEMPLO: Generación de KuDE (PDF)")
    print("=" * 80)
    print()
    
    # 1. Configurar cliente
    print("1. Configurando cliente SIFEN...")
    
    # Obtener credenciales de variables de entorno
    cert_path = os.getenv("SIFEN_CERT_PATH", "/path/to/certificado.p12")
    cert_password = os.getenv("SIFEN_CERT_PASSWORD", "password")
    csc = os.getenv("SIFEN_CSC", "ABCD0000000000000000000000000000")
    csc_id = os.getenv("SIFEN_CSC_ID", "0001")
    
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo=cert_path,
        certificado_contrasena=cert_password,
        csc=csc,
        csc_id=csc_id,
    )
    
    client = SifenClient(config)
    print("   ✓ Cliente configurado")
    print()
    
    # 2. Crear documento
    print("2. Creando documento de ejemplo...")
    documento = crear_documento_ejemplo()
    print(f"   ✓ Documento creado: {documento.gTimb.dDesTiDE}")
    print(f"   - Emisor: {documento.gEmis.dNomEmi}")
    print(f"   - Receptor: {documento.gDatRec.dNomRec}")
    print(f"   - Items: {len(documento.gCamItem)}")
    print(f"   - Total: Gs. {documento.gTotSub.dTotGralOpe:,.0f}".replace(",", "."))
    print()
    
    # 3. Generar CDC (necesario para el KuDE)
    print("3. Generando CDC...")
    cdc = documento.generate_cdc()
    print(f"   ✓ CDC generado: {cdc}")
    print()
    
    # 4. Generar KuDE
    print("4. Generando KuDE (PDF)...")
    
    # Ruta de salida
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"kude_{cdc}.pdf")
    
    # Logo (opcional)
    logo_path = os.getenv("SIFEN_LOGO_PATH")
    
    try:
        pdf_bytes = client.generar_kude(
            documento=documento,
            output_path=output_path,
            logo_path=logo_path
        )
        
        print(f"   ✓ KuDE generado exitosamente")
        print(f"   - Tamaño: {len(pdf_bytes):,} bytes")
        print(f"   - Guardado en: {output_path}")
        print()
        
        # 5. Información adicional
        print("5. Información del KuDE:")
        print(f"   - Formato: PDF (A4)")
        print(f"   - Incluye: Encabezado, datos emisor/receptor, ítems, totales")
        print(f"   - QR Code: {'Sí' if logo_path else 'Sí (sin logo)'}")
        print(f"   - CDC: {cdc}")
        print()
        
        print("=" * 80)
        print("✓ Ejemplo completado exitosamente")
        print("=" * 80)
        print()
        print("Notas:")
        print("- El KuDE es la representación gráfica del documento electrónico")
        print("- Puede ser impreso o enviado digitalmente al cliente")
        print("- El código QR permite consultar el documento en SIFEN")
        print("- Válido por 6 meses según especificaciones SIFEN")
        print()
        
    except ImportError as e:
        print(f"   ✗ Error: {e}")
        print()
        print("Para generar KuDE necesitas instalar las dependencias:")
        print("   pip install reportlab qrcode[pil]")
        print()
        
    except Exception as e:
        print(f"   ✗ Error al generar KuDE: {e}")
        print()


if __name__ == "__main__":
    main()
