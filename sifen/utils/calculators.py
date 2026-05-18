"""
Calculadoras para montos, IVA y totales.

Proporciona funciones para calcular automáticamente valores del DE.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional

from sifen.models.items import Item, ValorItem, IVAItem
from sifen.models.totales import Totales, SubtotalIVA


def calcular_base_exenta_nt13(
    total_operacion: Decimal, proporcion_iva: Decimal, tasa_iva: Decimal
) -> Decimal:
    """
    Calcula la base exenta según Nota Técnica 13 de SIFEN.

    Esta fórmula se aplica para ítems con afectación IVA tipo 4 (Gravado Parcial)
    cuando está habilitada la Nota Técnica 13.

    Fórmula NT-13:
    dBasExe = [100 * dTotOpeItem * (100 – dPropIVA)] / [10000 + (dTasaIVA * dPropIVA)]

    Referencia:
    https://ekuatia.set.gov.py/portal/ekuatia/detail?content-id=/repository/collaboration/
    sites/ekuatia/documents/documentacion/documentacion-tecnica/NT_E_KUATIA_013_MT_V150.pdf

    Args:
        total_operacion: Total de la operación del ítem (dTotOpeItem).
        proporcion_iva: Proporción de IVA 0-100 (dPropIVA).
        tasa_iva: Tasa de IVA (dTasaIVA).

    Returns:
        Base exenta calculada según NT-13.

    Example:
        >>> calcular_base_exenta_nt13(
        ...     Decimal('1000'),
        ...     Decimal('50'),
        ...     Decimal('10')
        ... )
        Decimal('476.19')
    """
    cien = Decimal("100")
    diez_mil = Decimal("10000")

    # Numerador: 100 * dTotOpeItem * (100 – dPropIVA)
    numerador = cien * total_operacion * (cien - proporcion_iva)

    # Denominador: 10000 + (dTasaIVA * dPropIVA)
    denominador = diez_mil + (tasa_iva * proporcion_iva)

    # Calcular y redondear
    base_exenta = (numerador / denominador).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    return base_exenta


def calcular_iva_item(
    precio_unitario: Decimal,
    cantidad: Decimal,
    tasa_iva: int,
    proporcion: Decimal = Decimal("100"),
    habilitar_nt13: bool = True,
    afectacion_iva: Optional[int] = None,
) -> IVAItem:
    """
    Calcula el IVA de un ítem.

    Args:
        precio_unitario: Precio unitario del producto.
        cantidad: Cantidad del producto.
        tasa_iva: Tasa de IVA (5, 10, o 0 para exento).
        proporcion: Proporción de IVA (0-100).
        habilitar_nt13: Si se debe aplicar Nota Técnica 13 para afectación tipo 4.
        afectacion_iva: Tipo de afectación IVA (1-4). Si no se especifica, se determina automáticamente.

    Returns:
        IVAItem calculado.
    """
    # Total del ítem (precio * cantidad)
    # El precio incluye IVA, entonces dTotOpeItem incluye IVA
    total_item = precio_unitario * cantidad

    # Tasa decimal
    tasa_decimal = Decimal(str(tasa_iva))

    # Fórmula según Manual Técnico SIFEN v150 (E735):
    # dBasGravIVA = (dTotOpeItem * (dPropIVA/100)) / divisor
    # donde divisor = 1.10 para IVA 10%, 1.05 para IVA 5%

    if tasa_iva == 10:
        divisor = Decimal("1.10")
    elif tasa_iva == 5:
        divisor = Decimal("1.05")
    else:
        divisor = Decimal("1")

    # Aplicar proporción y dividir por divisor
    base_gravada = ((total_item * proporcion / Decimal("100")) / divisor).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    # Fórmula según Manual Técnico SIFEN v150 (E736):
    # dLiqIVAItem = dBasGravIVA * (dTasaIVA/100)
    liq_iva = (base_gravada * tasa_decimal / Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    # Verificar que base + IVA = total (ajustar IVA si hay diferencia por redondeo)
    total_item_rounded = total_item.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    suma_calculada = base_gravada + liq_iva
    if suma_calculada != total_item_rounded:
        # Ajustar el IVA para que la suma sea exacta
        liq_iva = total_item_rounded - base_gravada

    # Determinar afectación si no se especificó
    if afectacion_iva is None:
        if tasa_iva == 10:
            afectacion = 1
            descripcion = "Gravado IVA"
        elif tasa_iva == 5:
            afectacion = 2
            descripcion = "Gravado IVA"
        else:
            afectacion = 3
            descripcion = "Exento"
    else:
        afectacion = afectacion_iva
        if afectacion == 1:
            descripcion = "Gravado IVA"
        elif afectacion == 2:
            descripcion = "Gravado IVA"
        elif afectacion == 3:
            descripcion = "Exento"
        elif afectacion == 4:
            descripcion = "Gravado Parcial"
        else:
            descripcion = "Desconocido"

    # Calcular base exenta si aplica NT-13 y es afectación tipo 4
    base_exenta = None
    if habilitar_nt13 and afectacion == 4:
        base_exenta = calcular_base_exenta_nt13(total_item, proporcion, tasa_decimal)

    return IVAItem(
        iAfecIVA=afectacion,
        dDesAfecIVA=descripcion,
        dPropIVA=proporcion,
        dTasaIVA=tasa_iva,
        dBasGravIVA=base_gravada.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        dLiqIVAItem=liq_iva,
    )


def calcular_valor_item(
    precio_unitario: Decimal,
    cantidad: Decimal,
    tasa_iva: int = 10,
    descuento: Decimal = Decimal("0"),
) -> ValorItem:
    """
    Calcula el valor completo de un ítem.

    Args:
        precio_unitario: Precio unitario.
        cantidad: Cantidad.
        tasa_iva: Tasa de IVA (5, 10, o 0).
        descuento: Descuento a aplicar.

    Returns:
        ValorItem calculado.
    """
    # Total sin descuento
    total_sin_desc = precio_unitario * cantidad

    # Total con descuento
    total_item = (total_sin_desc - descuento).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    # Calcular IVA
    iva_item = calcular_iva_item(precio_unitario, cantidad, tasa_iva)

    # Total con IVA
    total_con_iva = (total_item + iva_item.dLiqIVAItem).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    return ValorItem(
        dPUniProSer=precio_unitario,
        dDescItem=descuento if descuento > 0 else None,
        dTotOpeItem=total_item,
        dTotOpeGs=total_con_iva,
        gCamIVA=iva_item,
    )


def calcular_totales(items: List[Item]) -> Totales:
    """
    Calcula los totales de un documento a partir de sus ítems.

    Args:
        items: Lista de ítems del documento.

    Returns:
        Totales calculados.
    """
    # Inicializar acumuladores
    subtotal_exento = Decimal("0")
    subtotal_5 = Decimal("0")
    subtotal_10 = Decimal("0")
    base_grav_5 = Decimal("0")
    base_grav_10 = Decimal("0")
    total_iva_5 = Decimal("0")
    total_iva_10 = Decimal("0")
    total_operacion = Decimal("0")

    # Acumular por cada ítem
    for item in items:
        valor = item.gValorItem

        # Según Manual Técnico F008: dTotOpe = suma de EA008 (dTotOpeItem)
        total_operacion += valor.dTotOpeItem

        if valor.gCamIVA:
            iva = valor.gCamIVA

            # Clasificar según afectación
            # dSubXX y dTotOpe son suma de dTotOpeItem (con IVA incluido)
            # dBasGravIVA es la base gravada (sin IVA)
            if iva.iAfecIVA == 1:  # Gravado 10%
                subtotal_10 += valor.dTotOpeItem
                base_grav_10 += iva.dBasGravIVA
                total_iva_10 += iva.dLiqIVAItem
            elif iva.iAfecIVA == 2:  # Gravado 5%
                subtotal_5 += valor.dTotOpeItem
                base_grav_5 += iva.dBasGravIVA
                total_iva_5 += iva.dLiqIVAItem
            elif iva.iAfecIVA == 3:  # Exento
                subtotal_exento += valor.dTotOpeItem

    # Redondear
    subtotal_exento = subtotal_exento.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    subtotal_5 = subtotal_5.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    subtotal_10 = subtotal_10.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total_iva_5 = total_iva_5.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total_iva_10 = total_iva_10.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total_operacion = total_operacion.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Total IVA
    total_iva = (total_iva_5 + total_iva_10).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    # Total general: igual a dTotOpe
    # Según Manual Técnico F014: dTotGralOpe = F008 - F013 + F025
    # Para operaciones simples sin redondeo ni comisión: dTotGralOpe = dTotOpe
    # dTotOpe ya incluye IVA (suma de dTotOpeItem)
    total_general = total_operacion

    # Crear subtotales por tasa
    subtotales_iva = []

    if subtotal_10 > 0:
        subtotales_iva.append(
            SubtotalIVA(
                iAfecIVA=1,
                dDesAfecIVA="Gravado IVA",
                dBasGravIVA=base_grav_10.quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                ),
                dLiqIVA=total_iva_10,
                dTasaIVA=10,
            )
        )

    if subtotal_5 > 0:
        subtotales_iva.append(
            SubtotalIVA(
                iAfecIVA=2,
                dDesAfecIVA="Gravado IVA",
                dBasGravIVA=base_grav_5.quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                ),
                dLiqIVA=total_iva_5,
                dTasaIVA=5,
            )
        )

    # Calcular total base gravada IVA
    total_base_grav = (base_grav_5 + base_grav_10).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    return Totales(
        dSubExe=subtotal_exento,
        dSubExo=Decimal("0"),
        dSub5=subtotal_5,  # Siempre incluir aunque sea 0
        dSub10=subtotal_10 if subtotal_10 > 0 else None,
        dTotOpe=total_operacion,
        dTotDesc=Decimal("0"),  # Total descuentos
        dTotDescGlotem=Decimal("0"),  # Descuentos globales por ítem
        dTotAntItem=Decimal("0"),  # Anticipos por ítem
        dTotAnt=Decimal("0"),  # Total anticipos
        dPorcDescTotal=Decimal("0"),  # Porcentaje descuento total
        dDescTotal=Decimal("0"),  # Descuento total
        dAnticipo=Decimal("0"),  # Anticipo
        dRedon=Decimal("0"),  # Redondeo
        dTotGralOpe=total_general,
        dIVA5=total_iva_5,  # Siempre incluir aunque sea 0
        dIVA10=total_iva_10 if total_iva_10 > 0 else None,
        dTotIVA=total_iva,
        dBaseGrav5=base_grav_5.quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        ),  # Siempre incluir aunque sea 0
        dBaseGrav10=(
            base_grav_10.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if base_grav_10 > 0
            else None
        ),
        dTBasGraIVA=total_base_grav if total_base_grav > 0 else None,
        gCamIVA=subtotales_iva,
        dLiqTotIVA5=total_iva_5 if total_iva_5 > 0 else None,
        dLiqTotIVA10=total_iva_10 if total_iva_10 > 0 else None,
        cMoneOpe="PYG",
        dDesMoneOpe="Guarani",
    )


def redondear_moneda(valor: Decimal, decimales: int = 2) -> Decimal:
    """
    Redondea un valor monetario.

    Args:
        valor: Valor a redondear.
        decimales: Número de decimales.

    Returns:
        Valor redondeado.
    """
    formato = "0." + "0" * decimales
    return valor.quantize(Decimal(formato), rounding=ROUND_HALF_UP)


def calcular_precio_con_iva(precio_sin_iva: Decimal, tasa_iva: int) -> Decimal:
    """
    Calcula el precio con IVA incluido.

    Args:
        precio_sin_iva: Precio sin IVA.
        tasa_iva: Tasa de IVA (5 o 10).

    Returns:
        Precio con IVA.
    """
    tasa_decimal = Decimal(str(tasa_iva)) / Decimal("100")
    precio_con_iva = precio_sin_iva * (Decimal("1") + tasa_decimal)
    return redondear_moneda(precio_con_iva)


def calcular_precio_sin_iva(precio_con_iva: Decimal, tasa_iva: int) -> Decimal:
    """
    Calcula el precio sin IVA a partir del precio con IVA.

    Args:
        precio_con_iva: Precio con IVA incluido.
        tasa_iva: Tasa de IVA (5 o 10).

    Returns:
        Precio sin IVA.
    """
    tasa_decimal = Decimal(str(tasa_iva)) / Decimal("100")
    precio_sin_iva = precio_con_iva / (Decimal("1") + tasa_decimal)
    return redondear_moneda(precio_sin_iva)
