"""
Ejemplo de creación de un Documento Electrónico usando los modelos de datos.

Este script demuestra cómo crear un DE completo con todos sus campos.
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


def crear_documento_ejemplo():
    """Crea un documento electrónico de ejemplo."""
    
    print("=" * 60)
    print("Creando Documento Electrónico de Ejemplo")
    print("=" * 60)
    
    # 1. Identificación del DE
    print("\n1. Creando identificación del DE...")
    identificacion = IdentificacionDE(
        iTiDE=1,  # Factura electrónica
        dDesTiDE="Factura Electrónica",
        dNumTim=12345678,
        dEst="001",  # Establecimiento
        dPunExp="001",  # Punto de expedición
        dNumDoc="0000001",  # Número de documento
        dFeIniT=datetime.now(),
    )
    print("   ✓ Identificación creada")
    
    # 2. Datos generales
    print("\n2. Creando datos generales...")
    datos_generales = DatosGeneralesDE(
        dFeEmiDE=date.today(),
        iTipEmi=1,  # Normal
        dDesTipEmi="Normal",
        dCodSeg="123456789",  # Código de seguridad (9 dígitos)
    )
    print("   ✓ Datos generales creados")
    
    # 3. Emisor
    print("\n3. Creando datos del emisor...")
    emisor = Emisor(
        dRucEm="80012345-6",
        dDVEmi=6,
        iTipCont=1,  # Persona jurídica
        dDesTipCont="Persona Jurídica",
        dNomEmi="Empresa de Prueba S.A.",
        dNomFanEmi="Empresa Prueba",
        dDirEmi="Av. Principal 123",
        dNumCas=123,
        cDepEmi=1,  # Central
        dDesDepEmi="Central",
        cDisEmi=1,  # Asunción
        dDesDisEmi="Asunción",
        cCiuEmi=1,
        dDesCiuEmi="Asunción",
        dTelEmi="021-123456",
        dEmailE="contacto@empresaprueba.com.py",
        gActEco=[
            ActividadEconomica(
                cActEco="47111",
                dDesActEco="Venta al por menor en comercios no especializados"
            )
        ],
    )
    print("   ✓ Emisor creado")
    
    # 4. Receptor
    print("\n4. Creando datos del receptor...")
    receptor = Receptor(
        iNatRec=1,  # Contribuyente
        dDesNatRec="Contribuyente",
        iTiOpe=1,  # B2B
        dDesTiOpe="B2B",
        iTiContRec=1,
        dDesTiContRec="RUC",
        dNumIDRec="80067890-1",
        dNomRec="Cliente de Prueba S.R.L.",
        dDirRec="Calle Secundaria 456",
        cDepRec=1,
        dDesDepRec="Central",
        cDisRec=1,
        dDesDisRec="Asunción",
        cCiuRec=1,
        dDesCiuRec="Asunción",
        dTelRec="021-654321",
        dEmailRec="cliente@prueba.com.py",
    )
    print("   ✓ Receptor creado")
    
    # 5. Items
    print("\n5. Creando ítems...")
    items = [
        Item(
            dCodInt="PROD001",
            dDesProSer="Producto de Prueba 1",
            cUniMed=77,  # Unidad
            dDesUniMed="Unidad",
            dCantProSer=Decimal('10'),
            gValorItem=ValorItem(
                dPUniProSer=Decimal('100000'),  # 100.000 Gs por unidad
                dTotOpeItem=Decimal('1000000'),  # 1.000.000 Gs total
                dTotOpeGs=Decimal('1100000'),  # 1.100.000 Gs con IVA
                gCamIVA=IVAItem(
                    iAfecIVA=1,  # Gravado IVA 10%
                    dDesAfecIVA="Gravado IVA 10%",
                    dPropIVA=Decimal('100'),
                    dTasaIVA=Decimal('10'),
                    dBasGravIVA=Decimal('1000000'),
                    dLiqIVAItem=Decimal('100000'),  # 10% de 1.000.000
                ),
            ),
        ),
        Item(
            dCodInt="PROD002",
            dDesProSer="Producto de Prueba 2",
            cUniMed=77,
            dDesUniMed="Unidad",
            dCantProSer=Decimal('5'),
            gValorItem=ValorItem(
                dPUniProSer=Decimal('200000'),  # 200.000 Gs por unidad
                dTotOpeItem=Decimal('1000000'),  # 1.000.000 Gs total
                dTotOpeGs=Decimal('1100000'),  # 1.100.000 Gs con IVA
                gCamIVA=IVAItem(
                    iAfecIVA=1,  # Gravado IVA 10%
                    dDesAfecIVA="Gravado IVA 10%",
                    dPropIVA=Decimal('100'),
                    dTasaIVA=Decimal('10'),
                    dBasGravIVA=Decimal('1000000'),
                    dLiqIVAItem=Decimal('100000'),
                ),
            ),
        ),
    ]
    print(f"   ✓ {len(items)} ítems creados")
    
    # 6. Totales
    print("\n6. Calculando totales...")
    totales = Totales(
        dSub10=Decimal('2000000'),  # Subtotal gravado 10%
        dTotOpe=Decimal('2000000'),  # Total operación
        gCamIVA=[
            SubtotalIVA(
                iAfecIVA=1,
                dDesAfecIVA="Gravado IVA 10%",
                dBasGravIVA=Decimal('2000000'),
                dLiqIVA=Decimal('200000'),
                dTasaIVA=Decimal('10'),
            )
        ],
        dTotIVA=Decimal('200000'),  # Total IVA
        dLiqTotIVA10=Decimal('200000'),
        dTotGralOpe=Decimal('2200000'),  # Total general (con IVA)
        cMoneOpe="PYG",
        dDesMoneOpe="Guaraní",
    )
    print("   ✓ Totales calculados")
    
    # 7. Condición de operación (contado)
    print("\n7. Definiendo condición de operación...")
    condicion = CondicionOperacion(
        iCondOpe=1,  # Contado
        dDesCondOpe="Contado",
        gPaConEIni=[
            Pago(
                iTiPago=1,  # Efectivo
                dDesTiPag="Efectivo",
                dMonTiPag=Decimal('2200000'),
                cMoneTiPag="PYG",
                dDesMoneTiPag="Guaraní",
            )
        ],
    )
    print("   ✓ Condición de operación definida")
    
    # 8. Crear documento completo
    print("\n8. Ensamblando documento electrónico...")
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
    print("   ✓ Documento ensamblado")
    
    # 9. Validar documento
    print("\n9. Validando documento...")
    is_valid, error = documento.validate()
    if is_valid:
        print("   ✓ Documento válido")
    else:
        print(f"   ✗ Documento inválido: {error}")
        return None
    
    # 10. Generar CDC
    print("\n10. Generando CDC...")
    cdc = documento.generate_cdc()
    print(f"   ✓ CDC generado: {cdc}")
    
    # 11. Mostrar resumen
    print("\n" + "=" * 60)
    print("Resumen del Documento Electrónico")
    print("=" * 60)
    print(f"Tipo: {identificacion.dDesTiDE}")
    print(f"Número: {identificacion.dEst}-{identificacion.dPunExp}-{identificacion.dNumDoc}")
    print(f"CDC: {cdc}")
    print(f"Emisor: {emisor.dNomEmi}")
    print(f"Receptor: {receptor.dNomRec}")
    print(f"Items: {len(items)}")
    print(f"Total: Gs. {totales.dTotGralOpe:,.0f}")
    print(f"Condición: {condicion.dDesCondOpe}")
    print("=" * 60)
    
    return documento


def main():
    """Función principal."""
    documento = crear_documento_ejemplo()
    
    if documento:
        print("\n✓ Documento electrónico creado exitosamente")
        print("\nPróximo paso: Convertir a XML y firmar digitalmente")
        print("(Esto se implementará en la Fase 4)")
    else:
        print("\n✗ Error al crear el documento electrónico")


if __name__ == "__main__":
    main()
