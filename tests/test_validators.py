"""
Tests para validadores.
"""

import unittest
from sifen.utils import (
    validar_ruc,
    calcular_dv_ruc,
    validar_cdc,
    calcular_dv_cdc,
    validar_email,
    validar_telefono,
)


class TestValidadores(unittest.TestCase):
    """Tests para funciones de validación."""
    
    def test_calcular_dv_ruc(self):
        """Test de cálculo de DV de RUC."""
        # Casos conocidos
        self.assertEqual(calcular_dv_ruc("80012345"), 6)
        self.assertEqual(calcular_dv_ruc("80067890"), 1)
        self.assertEqual(calcular_dv_ruc("1234567"), 0)
    
    def test_validar_ruc_valido(self):
        """Test de validación de RUC válido."""
        self.assertTrue(validar_ruc("80012345", "6"))
        self.assertTrue(validar_ruc("80067890", "1"))
        self.assertTrue(validar_ruc("80012345-6"))
    
    def test_validar_ruc_invalido(self):
        """Test de validación de RUC inválido."""
        self.assertFalse(validar_ruc("80012345", "5"))
        self.assertFalse(validar_ruc("80067890", "2"))
        self.assertFalse(validar_ruc("abc"))
    
    def test_validar_cdc_valido(self):
        """Test de validación de CDC válido."""
        # CDC de ejemplo con DV correcto
        base = "0100100100000011202405041230008001234560"
        dv = calcular_dv_cdc(base)
        cdc = base + str(dv)
        self.assertTrue(validar_cdc(cdc))
    
    def test_validar_cdc_invalido(self):
        """Test de validación de CDC inválido."""
        self.assertFalse(validar_cdc("123"))  # Muy corto
        self.assertFalse(validar_cdc("0" * 44))  # DV incorrecto
        self.assertFalse(validar_cdc("abc" * 15))  # No numérico
    
    def test_validar_email_valido(self):
        """Test de validación de email válido."""
        self.assertTrue(validar_email("test@example.com"))
        self.assertTrue(validar_email("user.name@domain.com.py"))
        self.assertTrue(validar_email("contact+tag@company.org"))
    
    def test_validar_email_invalido(self):
        """Test de validación de email inválido."""
        self.assertFalse(validar_email(""))
        self.assertFalse(validar_email("notanemail"))
        self.assertFalse(validar_email("@example.com"))
        self.assertFalse(validar_email("user@"))
    
    def test_validar_telefono_valido(self):
        """Test de validación de teléfono válido."""
        self.assertTrue(validar_telefono("021123456"))
        self.assertTrue(validar_telefono("0981-123456"))
        self.assertTrue(validar_telefono("021 123 456"))
    
    def test_validar_telefono_invalido(self):
        """Test de validación de teléfono inválido."""
        self.assertFalse(validar_telefono(""))
        self.assertFalse(validar_telefono("123"))  # Muy corto
        self.assertFalse(validar_telefono("abc"))  # No numérico


if __name__ == '__main__':
    unittest.main()
