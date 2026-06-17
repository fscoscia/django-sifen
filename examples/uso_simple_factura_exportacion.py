"""
Ejemplo simplificado de uso de Factura de Exportación para proyectos externos.

Este ejemplo muestra cómo un proyecto que instale django-sifen puede crear
y enviar una Factura de Exportación de forma simple.
"""

from datetime import datetime, date
from decimal import Decimal

# Importar desde django-sifen
from sifen.client import SifenClient
from sifen.config import SifenConfig, TipoAmbiente
from sifen.models import (
    DocumentoElectronico,
    IdentificacionDE,
    DatosGeneralesDE,
    Emisor,
    Receptor,
    Item,
    ActividadEconomica,
)
from sifen.utils import calcular_valor_item, calcular_totales
from sifen.models.totales import CondicionOperacion, Pago


def crear_factura_exportacion_simple():
    """
    Ejemplo simple de cómo crear una Factura de Exportación.
    
    La Factura de Exportación se implementa como:
    - Tipo de documento: iTiDE=1 (Factura Electrónica)
    - Información de exportación en campo dInfoFisc
    """
    
    # 1. Información de exportación (según Decreto 10797/2013)
    info_exportacion = (
        "a) Tipo de Operación: Exportación Definitiva, "
        "b) Condición de Negociación: FOB, "
        "c) País de Destino: Brasil, "
        "d) Empresa Fletera o Exportador Nacional: NAVIERA SA, "
        "e) Agente de Transporte: LOGISTICA SRL, "
        "f) Instrucciones de Pago para el cliente: "
        "Beneficiario: MI EMPRESA SA, Banco: BANCO ITAU, "
        "Nº de cuenta: 1234567890, Código SWIFT: ITAUPYPA, "
        "g) Número/s de Conocimiento/s de Embarque: BL-2026-001234, "
        "h) Número/s de Manifiesto/s Internacional/es de Carga: MIC-2026-005678, "
        "i) Número de barcaza o remolcador: N/A, "
        "j) Conforme Decreto 10797/2013"
    )
    
    # 2. Crear identificación (iTiDE=1, NO iTiDE=2)
    identificacion = IdentificacionDE(
        iTiDE=1,  # Factura Electrónica (NO usar iTiDE=2)
        dDesTiDE="Factura Electrónica",
        dNumTim=12345678,
        dEst="001",
        dPunExp="001",
        dNumDoc="0000001",
        dFeIniT=date.today(),
    )
    
    # 3. Datos generales CON información de exportación
    datos_generales = DatosGeneralesDE(
        dFeEmiDE=datetime.now(),
        iTipEmi=1,
        dCodSeg="123456789",
        dInfoFisc=info_exportacion,  # ← AQUÍ va la info de exportación
        iTipTra=1,
        iTImp=1,
        cMoneOpe="USD",  # Moneda de exportación
    )
    
    # 4. Emisor (exportador paraguayo)
    emisor = Emisor(
        dRucEm="80012345-6",
        dDVEmi=6,
        iTipCont=1,
        dNomEmi="MI EMPRESA EXPORTADORA SA",
        dDirEmi="Av. Exportadores 1234",
        cDepEmi=1,
        cDisEmi=1,
        cCiuEmi=1,
        dTelEmi="021-123456",
        dEmailE="exportaciones@miempresa.com.py",
        gActEco=[
            ActividadEconomica(
                cActEco="46900",
                dDesActEco="Venta al por mayor"
            )
        ],
    )
    
    # 5. Receptor (importador extranjero)
    receptor = Receptor(
        iNatRec=2,  # No residente
        iTiOpe=2,   # B2B con no residente
        cPaisRec="BRA",
        dNomRec="EMPRESA IMPORTADORA LTDA",
        dNumIDRec="12.345.678/0001-90",
    )
    
    # 6. Items (productos exportados - exonerados de IVA)
    item = Item(
        dCodInt="PROD-001",
        dDesProSer="Producto para exportación",
        cUniMed=77,
        dCantProSer=Decimal("100"),
        cPaisOrig="PRY",
        gValorItem=calcular_valor_item(
            precio_unitario=Decimal("50"),  # USD 50
            cantidad=Decimal("100"),
            tasa_iva=0,  # Exonerado (exportación)
            afectacion_iva=3,  # 3 = Exonerado
        ),
    )
    
    # 7. Calcular totales
    totales = calcular_totales([item])
    totales.cMoneOpe = "USD"
    totales.dTiCam = Decimal("7000")  # Tipo de cambio
    
    # 8. Condición de pago
    condicion = CondicionOperacion(
        iCondOpe=1,  # Contado
        gPaConEIni=[
            Pago(
                iTiPago=4,  # Transferencia
                dMonTiPag=Decimal("5000"),
                cMoneTiPag="USD",
            )
        ],
    )
    
    # 9. Crear documento completo
    documento = DocumentoElectronico(
        dVerFor=150,
        gTimb=identificacion,
        gDatGralOpe=datos_generales,
        gEmis=emisor,
        gDatRec=receptor,
        gCamItem=[item],
        gTotSub=totales,
        gPaConEIni=condicion,
    )
    
    return documento


def main():
    """Ejemplo de uso completo."""
    
    print("=" * 70)
    print("EJEMPLO DE USO: FACTURA DE EXPORTACIÓN")
    print("=" * 70)
    
    # 1. Configurar cliente SIFEN
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,  # o TipoAmbiente.PROD
        certificado_archivo="/path/to/certificado.pfx",
        certificado_contrasena="password",
        csc="ABCD0000000000000000000000000000",
        csc_id="0001",
    )
    
    client = SifenClient(config)
    
    # 2. Crear factura de exportación
    print("\n1. Creando factura de exportación...")
    documento = crear_factura_exportacion_simple()
    print(f"   ✓ CDC: {documento.CDC}")
    
    # 3. Enviar a SIFEN (sincrónico - respuesta inmediata)
    print("\n2. Enviando a SIFEN...")
    try:
        respuesta = client.enviar_documento(documento)
        
        if respuesta.aprobado:
            print("   ✓ APROBADO!")
            print(f"   Protocolo: {respuesta.numero_protocolo}")
            print(f"   CDC: {respuesta.cdc}")
        else:
            print("   ✗ RECHAZADO")
            print(f"   Motivo: {respuesta.mensaje}")
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 70)
    print("RESUMEN:")
    print("- La Factura de Exportación usa iTiDE=1 (Factura normal)")
    print("- La información de exportación va en el campo dInfoFisc")
    print("- Todo se maneja con client.enviar_documento()")
    print("=" * 70)


if __name__ == "__main__":
    # NOTA: Este ejemplo requiere configurar un certificado válido
    print("\n⚠ IMPORTANTE:")
    print("Este ejemplo requiere:")
    print("1. Certificado PFX válido")
    print("2. RUC habilitado para exportación en SIFEN")
    print("3. Configurar las credenciales en SifenConfig")
    print("\nPara ejecutar, descomenta la línea main() y configura tus credenciales.")
    print("=" * 70)
    
    # Descomentar para ejecutar:
    # main()
