"""
Módulo de generación y parseo XML para SIFEN.

Proporciona funcionalidades para:
- Generar XML desde objetos Python
- Parsear XML a objetos Python
- Validar estructura XML
"""

from sifen.xml.generator import (
    XMLGenerator,
    generate_xml,
    generate_xml_element,
)


__all__ = [
    "XMLGenerator",
    "generate_xml",
    "generate_xml_element",
]
