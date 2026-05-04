"""
Módulo de criptografía y firma digital para SIFEN.

Proporciona funcionalidades para:
- Firma digital de documentos XML (XMLDSig)
- Validación de firmas digitales
- Manejo de certificados PFX/PKCS12
"""

from sifen.crypto.signature import (
    XMLSigner,
    sign_xml_string,
    sign_xml_element,
)

from sifen.crypto.validator import (
    XMLSignatureValidator,
    SignatureValidationResult,
    validate_xml_signature,
)

from sifen.crypto.keystore import (
    load_pfx_certificate,
    get_certificate_info,
    validate_certificate,
)


__all__ = [
    # Firma
    "XMLSigner",
    "sign_xml_string",
    "sign_xml_element",
    # Validación
    "XMLSignatureValidator",
    "SignatureValidationResult",
    "validate_xml_signature",
    # Certificados
    "load_pfx_certificate",
    "get_certificate_info",
    "validate_certificate",
]
