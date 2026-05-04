"""
Ejemplo de envío de lote de documentos electrónicos.

Demuestra cómo enviar múltiples documentos en una sola petición.
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
    Receptor,
    Item,
    ActividadEconomica,
)
from sifen.utils import calcular_valor_item, calcular_totales
from sifen.models.totales import CondicionOperacion, Pago


def crear_documento(numero: int) -> DocumentoElectronico:
    """
    Crea un documento electrónico de ejemplo.
    
    Args:
        numero: Número del documento.
    
    Returns:
        DocumentoElectronico listo para enviar.
    """
    # Crear ítem
    item = Item(
        dCodInt=f"PROD{numero:03d}",
        dDesProSer=f"Producto {numero}",
        cUniMed=77,
        dCantProSer=Decimal('10'),
        gValorItem=calcular_valor_item(
            precio_unitario=Decimal('100000'),
            cantidad=Decimal('10'),
            tasa_iva=10,
        ),
    )
    
    # Calcular totales
    totales = calcular_totales([item])
    
    # Crear documento
    documento = DocumentoElectronico(
        dVerFor=150,
        gTimb=IdentificacionDE(
            iTiDE=1,
            dDesTiDE="Factura Electrónica",
            dNumTim=12345678,
            dEst="001",
            dPunExp="001",
            dNumDoc=f"{numero:07d}",
            dFeIniT=datetime.now(),
        ),
        gDatGralOpe=DatosGeneralesDE(
            dFeEmiDE=date.today(),
            iTipEmi=1,
            dDesTipEmi="Normal",
            dCodSeg="123456789",
        ),
        gEmis=Emisor(
            dRucEm="80012345-6",
            dDVEmi=6,
            iTipCont=1,
            dNomEmi="Empresa de Prueba S.A.",
            dDirEmi="Av. Principal 123",
            cDepEmi=1,
            cDisEmi=1,
            cCiuEmi=1,
            dTelEmi="021-123456",
            dEmailE="contacto@empresa.com.py",
            gActEco=[
                ActividadEconomica(
                    cActEco="47111",
                    dDesActEco="Venta al por menor"
                )
            ],
        ),
        gDatRec=Receptor(
            iNatRec=1,
            iTiOpe=1,
            dNumIDRec="80067890-1",
            dNomRec=f"Cliente {numero} S.R.L.",
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
    
    return documento


def main():
    """Ejemplo de envío de lote."""
    
    print("=" * 70)
    print("Ejemplo: Envío de Lote de Documentos Electrónicos")
    print("=" * 70)
    
    # 1. Configurar cliente
    print("\n1. Configurando cliente SIFEN...")
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/path/to/certificado.pfx",
        certificado_contrasena="password",
        csc="ABCD0000000000000000000000000000",
        csc_id="0001",
    )
    
    client = SifenClient(config)
    print("   ✓ Cliente configurado")
    
    # 2. Crear múltiples documentos
    print("\n2. Creando documentos...")
    cantidad_documentos = 5
    documentos = []
    
    for i in range(1, cantidad_documentos + 1):
        doc = crear_documento(i)
        documentos.append(doc)
        print(f"   ✓ Documento {i} creado")
    
    print(f"\n   Total: {len(documentos)} documentos")
    
    # 3. Enviar lote (TODO: descomentar cuando tengas certificado válido)
    print("\n3. Enviando lote a SIFEN...")
    print("   ⚠ Comentado - requiere certificado válido")
    print("   Para enviar, descomenta el siguiente código:")
    print("""
    try:
        respuesta = client.enviar_lote(documentos)
        
        print(f"\\n   ✓ Lote enviado!")
        print(f"   Número de lote: {respuesta.numero_lote}")
        print(f"   Total documentos: {respuesta.cantidad_documentos}")
        print(f"   Aprobados: {respuesta.documentos_aprobados}")
        print(f"   Rechazados: {respuesta.documentos_rechazados}")
        
        # Mostrar detalle de cada documento
        print(f"\\n   Detalle de documentos:")
        for i, detalle in enumerate(respuesta.detalles, 1):
            estado = "✓ Aprobado" if detalle.aprobado else "✗ Rechazado"
            print(f"   {i}. {estado} - CDC: {detalle.cdc[:20]}...")
            print(f"      Mensaje: {detalle.mensaje}")
        
        # 4. Consultar estado del lote
        if respuesta.numero_lote:
            print(f"\\n4. Consultando estado del lote...")
            consulta = client.consultar_lote(respuesta.numero_lote)
            
            if consulta.encontrado:
                print(f"   ✓ Lote encontrado")
                print(f"   Estado: {consulta.estado}")
                print(f"   Documentos: {consulta.cantidad_documentos}")
                
                for doc in consulta.documentos:
                    print(f"   - CDC: {doc.cdc[:20]}... Estado: {doc.estado}")
            else:
                print(f"   ✗ Lote no encontrado")
    
    except ValueError as e:
        print(f"   ✗ Error de validación: {e}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    """)
    
    # Resumen
    print("\n" + "=" * 70)
    print("Resumen")
    print("=" * 70)
    print(f"Documentos creados: {len(documentos)}")
    print(f"Límite por lote: 50 documentos")
    print("\nVentajas del envío por lote:")
    print("- Menor tiempo de procesamiento")
    print("- Menos peticiones HTTP")
    print("- Procesamiento asíncrono en SIFEN")
    print("- Ideal para facturación masiva")
    print("\nFlujo:")
    print("1. client.enviar_lote(documentos) → Retorna número de lote")
    print("2. client.consultar_lote(numero_lote) → Consultar estado")
    print("=" * 70)


if __name__ == "__main__":
    main()
