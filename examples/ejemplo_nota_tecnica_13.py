"""
Ejemplo de uso de Nota Técnica 13 para cálculo de IVA.

La Nota Técnica 13 establece una fórmula especial para calcular la base exenta
en ítems con afectación IVA tipo 4 (Gravado Parcial).

Referencia:
https://ekuatia.set.gov.py/portal/ekuatia/detail?content-id=/repository/collaboration/
sites/ekuatia/documents/documentacion/documentacion-tecnica/NT_E_KUATIA_013_MT_V150.pdf
"""

from decimal import Decimal
from sifen.utils.calculators import calcular_iva_item, calcular_base_exenta_nt13


def ejemplo_sin_nt13():
    """Ejemplo de cálculo SIN Nota Técnica 13."""
    
    print("=" * 70)
    print("Ejemplo: Cálculo SIN Nota Técnica 13")
    print("=" * 70)
    
    # Ítem con afectación tipo 1 (Gravado IVA 10%)
    iva_item = calcular_iva_item(
        precio_unitario=Decimal('1000'),
        cantidad=Decimal('10'),
        tasa_iva=10,
        proporcion=Decimal('100'),
        habilitar_nt13=False,  # NT-13 deshabilitada
        afectacion_iva=1  # Gravado IVA 10%
    )
    
    print(f"\nÍtem: 10 unidades a Gs. 1,000 c/u")
    print(f"Afectación: {iva_item.iAfecIVA} - {iva_item.dDesAfecIVA}")
    print(f"Proporción IVA: {iva_item.dPropIVA}%")
    print(f"Tasa IVA: {iva_item.dTasaIVA}%")
    print(f"Base Gravada: Gs. {iva_item.dBasGravIVA:,.2f}")
    print(f"Liquidación IVA: Gs. {iva_item.dLiqIVAItem:,.2f}")
    print(f"Base Exenta: {iva_item.dBasExe if iva_item.dBasExe else 'N/A'}")
    print("\n✓ Sin NT-13, no se calcula base exenta")


def ejemplo_con_nt13_afectacion_4():
    """Ejemplo de cálculo CON Nota Técnica 13 - Afectación tipo 4."""
    
    print("\n\n" + "=" * 70)
    print("Ejemplo: Cálculo CON Nota Técnica 13 - Afectación Tipo 4")
    print("=" * 70)
    
    # Ítem con afectación tipo 4 (Gravado Parcial)
    # Caso: 50% gravado, 50% exento
    iva_item = calcular_iva_item(
        precio_unitario=Decimal('1000'),
        cantidad=Decimal('10'),
        tasa_iva=10,
        proporcion=Decimal('50'),  # 50% gravado
        habilitar_nt13=True,  # NT-13 habilitada
        afectacion_iva=4  # Gravado Parcial
    )
    
    print(f"\nÍtem: 10 unidades a Gs. 1,000 c/u")
    print(f"Total operación: Gs. 10,000")
    print(f"Afectación: {iva_item.iAfecIVA} - {iva_item.dDesAfecIVA}")
    print(f"Proporción IVA: {iva_item.dPropIVA}% (50% gravado, 50% exento)")
    print(f"Tasa IVA: {iva_item.dTasaIVA}%")
    print(f"\nResultados:")
    print(f"  Base Gravada: Gs. {iva_item.dBasGravIVA:,.2f}")
    print(f"  Liquidación IVA: Gs. {iva_item.dLiqIVAItem:,.2f}")
    print(f"  Base Exenta (NT-13): Gs. {iva_item.dBasExe:,.2f}")
    
    print(f"\n✓ Con NT-13, se calcula base exenta con fórmula especial")
    print(f"  Fórmula: [100 * 10000 * (100 - 50)] / [10000 + (10 * 50)]")
    print(f"  Resultado: Gs. {iva_item.dBasExe:,.2f}")


def ejemplo_comparacion():
    """Comparación de diferentes proporciones con NT-13."""
    
    print("\n\n" + "=" * 70)
    print("Comparación: Diferentes Proporciones con NT-13")
    print("=" * 70)
    
    total = Decimal('10000')
    tasa = 10
    
    proporciones = [Decimal('25'), Decimal('50'), Decimal('75')]
    
    print(f"\nTotal operación: Gs. {total:,.2f}")
    print(f"Tasa IVA: {tasa}%")
    print(f"\n{'Proporción':<12} {'Base Gravada':<15} {'Base Exenta':<15} {'IVA':<15}")
    print("-" * 70)
    
    for prop in proporciones:
        iva_item = calcular_iva_item(
            precio_unitario=total,
            cantidad=Decimal('1'),
            tasa_iva=tasa,
            proporcion=prop,
            habilitar_nt13=True,
            afectacion_iva=4
        )
        
        print(f"{prop}%{'':<9} "
              f"Gs. {iva_item.dBasGravIVA:>10,.2f}  "
              f"Gs. {iva_item.dBasExe:>10,.2f}  "
              f"Gs. {iva_item.dLiqIVAItem:>10,.2f}")


def ejemplo_calculo_directo():
    """Ejemplo de cálculo directo de base exenta."""
    
    print("\n\n" + "=" * 70)
    print("Cálculo Directo de Base Exenta según NT-13")
    print("=" * 70)
    
    total_op = Decimal('10000')
    prop_iva = Decimal('50')
    tasa_iva = Decimal('10')
    
    base_exenta = calcular_base_exenta_nt13(total_op, prop_iva, tasa_iva)
    
    print(f"\nDatos:")
    print(f"  Total Operación: Gs. {total_op:,.2f}")
    print(f"  Proporción IVA: {prop_iva}%")
    print(f"  Tasa IVA: {tasa_iva}%")
    
    print(f"\nFórmula NT-13:")
    print(f"  dBasExe = [100 * dTotOpeItem * (100 – dPropIVA)] / [10000 + (dTasaIVA * dPropIVA)]")
    print(f"  dBasExe = [100 * {total_op} * (100 - {prop_iva})] / [10000 + ({tasa_iva} * {prop_iva})]")
    
    numerador = 100 * total_op * (100 - prop_iva)
    denominador = 10000 + (tasa_iva * prop_iva)
    
    print(f"\nCálculo:")
    print(f"  Numerador: 100 * {total_op} * {100 - prop_iva} = {numerador:,.2f}")
    print(f"  Denominador: 10000 + ({tasa_iva} * {prop_iva}) = {denominador:,.2f}")
    print(f"  Base Exenta: {numerador:,.2f} / {denominador:,.2f} = Gs. {base_exenta:,.2f}")


def ejemplo_uso_en_config():
    """Muestra cómo habilitar NT-13 en la configuración."""
    
    print("\n\n" + "=" * 70)
    print("Uso en Configuración")
    print("=" * 70)
    
    print("""
La Nota Técnica 13 se habilita en la configuración de SIFEN:

```python
from sifen import SifenConfig, TipoAmbiente

# Opción 1: Habilitar NT-13 (por defecto está habilitada)
config = SifenConfig(
    ambiente=TipoAmbiente.PROD,
    certificado_archivo="/path/to/cert.pfx",
    certificado_contrasena="password",
    csc="ABCD1234...",
    csc_id="0001",
    habilitar_nota_tecnica_13=True  # ← Habilitada por defecto
)

# Opción 2: Deshabilitar NT-13 (no recomendado)
config = SifenConfig(
    ...,
    habilitar_nota_tecnica_13=False  # Solo para testing
)

# Opción 3: Desde variables de entorno
# SIFEN_HABILITAR_NOTA_TECNICA_13=true
config = SifenConfig.from_env()
```

**Recomendación:** Mantener NT-13 habilitada para cumplir con las
especificaciones oficiales de SIFEN.

**¿Cuándo se aplica?**
- Solo para ítems con afectación IVA tipo 4 (Gravado Parcial)
- Calcula automáticamente el campo dBasExe (Base Exenta)
- Sigue la fórmula oficial de la Nota Técnica 13
    """)


if __name__ == "__main__":
    ejemplo_sin_nt13()
    ejemplo_con_nt13_afectacion_4()
    ejemplo_comparacion()
    ejemplo_calculo_directo()
    ejemplo_uso_en_config()
    
    print("\n" + "=" * 70)
    print("Resumen")
    print("=" * 70)
    print("✓ NT-13 habilitada por defecto en SifenConfig")
    print("✓ Se aplica automáticamente para afectación IVA tipo 4")
    print("✓ Calcula base exenta con fórmula oficial de SIFEN")
    print("✓ Garantiza cumplimiento normativo")
    print("=" * 70)
