"""
Ejemplo de uso del SifenClient.

Demuestra cómo usar la interfaz simplificada del cliente principal.
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
from sifen.utils import (
    calcular_valor_item,
    calcular_totales,
    validar_ruc,
    formatear_ruc,
)
from sifen.models.totales import CondicionOperacion, Pago


def main():
    """Ejemplo completo de uso del SifenClient."""
    
    print("=" * 70)
    print("Ejemplo: Uso del SifenClient")
    print("=" * 70)
    
    # 1. Configurar el cliente
    print("\n1. Configurando cliente SIFEN...")
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/path/to/certificado.pfx",
        certificado_contrasena="password",
        csc="ABCD0000000000000000000000000000",
        csc_id="0001",
    )
    
    # Opción A: Configuración global
    SifenClient.set_config(config)
    client = SifenClient()
    
    # Opción B: Configuración por instancia
    # client = SifenClient(config)
    
    print("   ✓ Cliente configurado")
    
    # 2. Validar RUC (método estático)
    print("\n2. Validando RUC...")
    ruc = "80012345"
    dv = SifenClient.calcular_dv_ruc(ruc)
    print(f"   RUC: {ruc}")
    print(f"   DV calculado: {dv}")
    print(f"   RUC formateado: {SifenClient.formatear_ruc(ruc, str(dv))}")
    
    if SifenClient.validar_ruc(ruc, str(dv)):
        print("   ✓ RUC válido")
    else:
        print("   ✗ RUC inválido")
    
    # 3. Consultar RUC en SIFEN
    print("\n3. Consultando RUC en SIFEN...")
    try:
        respuesta_ruc = client.consultar_ruc("80012345", "6")
        if respuesta_ruc.encontrado:
            print(f"   ✓ RUC encontrado: {respuesta_ruc.contribuyente.nombre}")
        else:
            print(f"   ✗ RUC no encontrado")
    except Exception as e:
        print(f"   ⚠ Error al consultar: {e}")
    
    # 4. Crear documento con utilidades
    print("\n4. Creando documento electrónico...")
    
    # Crear ítems usando calculadoras
    item1 = Item(
        dCodInt="PROD001",
        dDesProSer="Producto de Prueba",
        cUniMed=77,
        dCantProSer=Decimal('10'),
        gValorItem=calcular_valor_item(
            precio_unitario=Decimal('100000'),
            cantidad=Decimal('10'),
            tasa_iva=10,
        ),
    )
    
    items = [item1]
    
    # Calcular totales automáticamente
    totales = calcular_totales(items)
    
    # Crear documento
    documento = DocumentoElectronico(
        dVerFor=150,
        gTimb=IdentificacionDE(
            iTiDE=1,
            dDesTiDE="Factura Electrónica",
            dNumTim=12345678,
            dEst="001",
            dPunExp="001",
            dNumDoc="0000001",
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
            dNomRec="Cliente de Prueba S.R.L.",
        ),
        gCamItem=items,
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
    
    print("   ✓ Documento creado")
    
    # 5. Validar documento
    print("\n5. Validando documento...")
    is_valid, error = client.validar_documento(documento)
    if is_valid:
        print("   ✓ Documento válido")
    else:
        print(f"   ✗ Documento inválido: {error}")
        return
    
    # 6. Generar XML (sin enviar)
    print("\n6. Generando XML...")
    try:
        xml = client.generar_xml(documento)
        print(f"   ✓ XML generado ({len(xml)} caracteres)")
        print(f"   CDC: {documento.CDC}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return
    
    # 7. Enviar documento (TODO: descomentar cuando tengas certificado válido)
    print("\n7. Enviando documento a SIFEN...")
    print("   ⚠ Comentado - requiere certificado válido")
    print("   Para enviar, descomenta el siguiente código:")
    print("""
    try:
        respuesta = client.enviar_documento(documento)
        
        if respuesta.aprobado:
            print(f"   ✓ Documento aprobado!")
            print(f"   CDC: {respuesta.cdc}")
            print(f"   Protocolo: {respuesta.numero_protocolo}")
            
            # 8. Consultar estado
            consulta = client.consultar_documento(respuesta.cdc)
            print(f"   Estado: {consulta.estado}")
        else:
            print(f"   ✗ Documento rechazado")
            print(f"   Código: {respuesta.codigo}")
            print(f"   Mensaje: {respuesta.mensaje}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    """)
    
    # Resumen
    print("\n" + "=" * 70)
    print("Resumen")
    print("=" * 70)
    print(f"Cliente: Configurado y listo")
    print(f"Documento: Válido")
    print(f"CDC: {documento.CDC}")
    print(f"Total: Gs. {totales.dTotGralOpe:,.0f}")
    print("\nEl SifenClient simplifica todo el proceso:")
    print("- Validación automática")
    print("- Generación de CDC")
    print("- Generación de XML")
    print("- Firma digital")
    print("- Envío a SIFEN")
    print("\nTodo en una sola línea: client.enviar_documento(documento)")
    print("=" * 70)


if __name__ == "__main__":
    main()
