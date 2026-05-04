"""
Tests para calculadoras.
"""

import unittest
from decimal import Decimal

from sifen.utils import (
    calcular_iva_item,
    calcular_valor_item,
    calcular_totales,
    redondear_moneda,
    calcular_precio_con_iva,
    calcular_precio_sin_iva,
)
from sifen.models import Item


class TestCalculadoras(unittest.TestCase):
    """Tests para funciones de cálculo."""
    
    def test_calcular_iva_item_10(self):
        """Test de cálculo de IVA al 10%."""
        iva = calcular_iva_item(
            precio_unitario=Decimal('100000'),
            cantidad=Decimal('10'),
            tasa_iva=10
        )
        
        self.assertEqual(iva.iAfecIVA, 1)
        self.assertEqual(iva.dTasaIVA, Decimal('10'))
        self.assertEqual(iva.dBasGravIVA, Decimal('1000000.00'))
        self.assertEqual(iva.dLiqIVAItem, Decimal('100000.00'))
    
    def test_calcular_iva_item_5(self):
        """Test de cálculo de IVA al 5%."""
        iva = calcular_iva_item(
            precio_unitario=Decimal('100000'),
            cantidad=Decimal('10'),
            tasa_iva=5
        )
        
        self.assertEqual(iva.iAfecIVA, 2)
        self.assertEqual(iva.dTasaIVA, Decimal('5'))
        self.assertEqual(iva.dBasGravIVA, Decimal('1000000.00'))
        self.assertEqual(iva.dLiqIVAItem, Decimal('50000.00'))
    
    def test_calcular_iva_item_exento(self):
        """Test de cálculo de IVA exento."""
        iva = calcular_iva_item(
            precio_unitario=Decimal('100000'),
            cantidad=Decimal('10'),
            tasa_iva=0
        )
        
        self.assertEqual(iva.iAfecIVA, 3)
        self.assertEqual(iva.dLiqIVAItem, Decimal('0.00'))
    
    def test_calcular_valor_item(self):
        """Test de cálculo de valor de ítem."""
        valor = calcular_valor_item(
            precio_unitario=Decimal('100000'),
            cantidad=Decimal('10'),
            tasa_iva=10
        )
        
        self.assertEqual(valor.dPUniProSer, Decimal('100000'))
        self.assertEqual(valor.dTotOpeItem, Decimal('1000000.00'))
        self.assertEqual(valor.dTotOpeGs, Decimal('1100000.00'))
    
    def test_calcular_valor_item_con_descuento(self):
        """Test de cálculo de valor con descuento."""
        valor = calcular_valor_item(
            precio_unitario=Decimal('100000'),
            cantidad=Decimal('10'),
            tasa_iva=10,
            descuento=Decimal('100000')
        )
        
        self.assertEqual(valor.dDescItem, Decimal('100000'))
        self.assertEqual(valor.dTotOpeItem, Decimal('900000.00'))
    
    def test_redondear_moneda(self):
        """Test de redondeo de moneda."""
        self.assertEqual(
            redondear_moneda(Decimal('1234.567')),
            Decimal('1234.57')
        )
        self.assertEqual(
            redondear_moneda(Decimal('1234.564')),
            Decimal('1234.56')
        )
    
    def test_calcular_precio_con_iva(self):
        """Test de cálculo de precio con IVA."""
        precio_con_iva = calcular_precio_con_iva(
            Decimal('100000'),
            10
        )
        self.assertEqual(precio_con_iva, Decimal('110000.00'))
    
    def test_calcular_precio_sin_iva(self):
        """Test de cálculo de precio sin IVA."""
        precio_sin_iva = calcular_precio_sin_iva(
            Decimal('110000'),
            10
        )
        self.assertEqual(precio_sin_iva, Decimal('100000.00'))


if __name__ == '__main__':
    unittest.main()
