"""
Ejemplo completo: Crear documento, generar XML y firmar digitalmente.

Este script demuestra el flujo completo desde la creación del DE hasta el XML firmado.
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
from lxml import etree


def crear_documento_ejemplo():
    """Crea un documento electrónico de ejemplo."""
    
    # 1. Identificación
    identificacion = IdentificacionDE(
        iTiDE=1,
        dDesTiDE="Factura Electrónica",
        dNumTim=12345678,
        dEst="001",
        dPunExp="001",
        dNumDoc="0000001",
        dFeIniT=datetime.now(),
    )
    
    # 2. Datos generales
    datos_generales = DatosGeneralesDE(
        dFeEmiDE=date.today(),
        iTipEmi=1,
        dDesTipEmi="Normal",
        dCodSeg="123456789",
    )
    
    # 3. Emisor
    emisor = Emisor(
        dRucEm="80012345-6",
        dDVEmi=6,
        iTipCont=1,
        dDesTipCont="Persona Jurídica",
        dNomEmi="Empresa de Prueba S.A.",
        dDirEmi="Av. Principal 123",
        cDepEmi=1,
        cDisEmi=1,
        cCiuEmi=1,
        dTelEmi="021-123456",
        dEmailE="contacto@empresaprueba.com.py",
        gActEco=[
            ActividadEconomica(
                cActEco="47111",
                dDesActEco="Venta al por menor"
            )
        ],
    )
    
    # 4. Receptor
    receptor = Receptor(
        iNatRec=1,
        dDesNatRec="Contribuyente",
        iTiOpe=1,
        dDesTiOpe="B2B",
        dNumIDRec="80067890-1",
        dNomRec="Cliente de Prueba S.R.L.",
    )
    
    # 5. Items
    items = [
        Item(
            dCodInt="PROD001",
            dDesProSer="Producto de Prueba",
            cUniMed=77,
            dDesUniMed="Unidad",
            dCantProSer=Decimal('10'),
            gValorItem=ValorItem(
                dPUniProSer=Decimal('100000'),
                dTotOpeItem=Decimal('1000000'),
                dTotOpeGs=Decimal('1100000'),
                gCamIVA=IVAItem(
                    iAfecIVA=1,
                    dDesAfecIVA="Gravado IVA 10%",
                    dPropIVA=Decimal('100'),
                    dTasaIVA=Decimal('10'),
                    dBasGravIVA=Decimal('1000000'),
                    dLiqIVAItem=Decimal('100000'),
                ),
            ),
        ),
    ]
    
    # 6. Totales
    totales = Totales(
        dSub10=Decimal('1000000'),
        dTotOpe=Decimal('1000000'),
        gCamIVA=[
            SubtotalIVA(
                iAfecIVA=1,
                dDesAfecIVA="Gravado IVA 10%",
                dBasGravIVA=Decimal('1000000'),
                dLiqIVA=Decimal('100000'),
                dTasaIVA=Decimal('10'),
            )
        ],
        dTotIVA=Decimal('100000'),
        dLiqTotIVA10=Decimal('100000'),
        dTotGralOpe=Decimal('1100000'),
        cMoneOpe="PYG",
        dDesMoneOpe="Guaraní",
    )
    
    # 7. Condición
    condicion = CondicionOperacion(
        iCondOpe=1,
        dDesCondOpe="Contado",
        gPaConEIni=[
            Pago(
                iTiPago=1,
                dDesTiPag="Efectivo",
                dMonTiPag=Decimal('1100000'),
            )
        ],
    )
    
    # 8. Crear documento
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
    """Función principal."""
    print("=" * 70)
    print("Ejemplo: Generar XML y Firmar Digitalmente")
    print("=" * 70)
    
    # 1. Crear documento
    print("\n1. Creando documento electrónico...")
    documento = crear_documento_ejemplo()
    print("   ✓ Documento creado")
    
    # 2. Validar documento
    print("\n2. Validando documento...")
    is_valid, error = documento.validate()
    if not is_valid:
        print(f"   ✗ Error: {error}")
        return
    print("   ✓ Documento válido")
    
    # 3. Generar CDC
    print("\n3. Generando CDC...")
    cdc = documento.generate_cdc()
    print(f"   ✓ CDC: {cdc}")
    
    # 4. Generar XML
    print("\n4. Generando XML...")
    try:
        xml_string = generate_xml(documento)
        print("   ✓ XML generado")
        print("\nXML sin firmar (primeras líneas):")
        print("-" * 70)
        lines = xml_string.split('\n')[:20]
        print('\n'.join(lines))
        print("   ...")
        print("-" * 70)
    except Exception as e:
        print(f"   ✗ Error al generar XML: {e}")
        return
    
    # 5. Firmar XML (requiere certificado)
    print("\n5. Firmando XML...")
    print("   ⚠ Para firmar necesitas configurar un certificado PFX válido")
    print("   Ejemplo de configuración:")
    print("""
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/path/to/cert.pfx",
        certificado_contrasena="password",
        csc="ABCD0000000000000000000000000000",
        csc_id="0001",
    )
    
    # Parsear XML
    root = etree.fromstring(xml_string.encode('utf-8'))
    
    # Firmar
    signed_root = sign_xml_element(root, config, reference_id=documento.Id)
    
    # Convertir a string
    xml_firmado = etree.tostring(signed_root, encoding='unicode', pretty_print=True)
    """)
    
    # 6. Guardar XML (opcional)
    print("\n6. Guardando XML en archivo...")
    try:
        filename = f"DE_{cdc}.xml"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(xml_string)
        print(f"   ✓ XML guardado en: {filename}")
    except Exception as e:
        print(f"   ✗ Error al guardar: {e}")
    
    # Resumen
    print("\n" + "=" * 70)
    print("Resumen")
    print("=" * 70)
    print(f"CDC: {cdc}")
    print(f"Tipo: Factura Electrónica")
    print(f"Número: 001-001-0000001")
    print(f"Total: Gs. 1.100.000")
    print(f"Archivo: {filename if 'filename' in locals() else 'N/A'}")
    print("\nPróximo paso:")
    print("- Firmar el XML con tu certificado digital")
    print("- Enviar a SIFEN usando los servicios web (Fase 5)")
    print("=" * 70)


if __name__ == "__main__":
    main()
