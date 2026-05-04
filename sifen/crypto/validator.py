"""
Módulo para validación de firmas digitales XML.

Basado en la funcionalidad de validación de SignatureHelper.java.
"""

from typing import Optional
from dataclasses import dataclass
from lxml import etree
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding
import base64

from sifen.exceptions import SignatureException


DSIG_NS = "http://www.w3.org/2000/09/xmldsig#"


@dataclass
class SignatureValidationResult:
    """
    Resultado de la validación de una firma digital.
    
    Attributes:
        is_valid: Si la firma es válida.
        reason: Razón de invalidez (si aplica).
        certificate_subject: Información del sujeto del certificado.
    """
    is_valid: bool
    reason: Optional[str] = None
    certificate_subject: Optional[dict] = None


class XMLSignatureValidator:
    """
    Validador de firmas digitales XML según XMLDSig.
    """
    
    def __init__(self, xml_content: str):
        """
        Inicializa el validador.
        
        Args:
            xml_content: Contenido XML como string.
        """
        try:
            self.root = etree.fromstring(xml_content.encode('utf-8'))
        except Exception as e:
            raise SignatureException(
                f"Error al parsear XML: {str(e)}"
            ) from e
    
    def validate(self) -> SignatureValidationResult:
        """
        Valida la firma digital del documento XML.
        
        Returns:
            Resultado de la validación.
        """
        try:
            # 1. Encontrar el elemento Signature
            signature_elem = self._find_signature()
            if signature_elem is None:
                return SignatureValidationResult(
                    is_valid=False,
                    reason="No se encontró elemento Signature en el XML"
                )
            
            # 2. Extraer componentes de la firma
            signed_info = signature_elem.find(f'{{{DSIG_NS}}}SignedInfo')
            signature_value = signature_elem.find(f'{{{DSIG_NS}}}SignatureValue')
            key_info = signature_elem.find(f'{{{DSIG_NS}}}KeyInfo')
            
            if signed_info is None or signature_value is None or key_info is None:
                return SignatureValidationResult(
                    is_valid=False,
                    reason="Estructura de firma incompleta"
                )
            
            # 3. Extraer certificado
            certificate = self._extract_certificate(key_info)
            if certificate is None:
                return SignatureValidationResult(
                    is_valid=False,
                    reason="No se pudo extraer el certificado de la firma"
                )
            
            # 4. Validar digest del elemento referenciado
            reference = signed_info.find(f'{{{DSIG_NS}}}Reference')
            if not self._validate_digest(reference):
                return SignatureValidationResult(
                    is_valid=False,
                    reason="El digest del elemento referenciado no coincide",
                    certificate_subject=self._get_certificate_subject(certificate)
                )
            
            # 5. Validar firma del SignedInfo
            if not self._validate_signature(signed_info, signature_value, certificate):
                return SignatureValidationResult(
                    is_valid=False,
                    reason="La firma digital no es válida",
                    certificate_subject=self._get_certificate_subject(certificate)
                )
            
            # Firma válida
            return SignatureValidationResult(
                is_valid=True,
                certificate_subject=self._get_certificate_subject(certificate)
            )
            
        except Exception as e:
            return SignatureValidationResult(
                is_valid=False,
                reason=f"Error durante la validación: {str(e)}"
            )
    
    def _find_signature(self) -> Optional[etree.Element]:
        """Encuentra el elemento Signature en el XML."""
        signatures = self.root.xpath(
            '//ds:Signature',
            namespaces={'ds': DSIG_NS}
        )
        return signatures[0] if signatures else None
    
    def _extract_certificate(self, key_info: etree.Element) -> Optional[x509.Certificate]:
        """
        Extrae el certificado X.509 del KeyInfo.
        
        Args:
            key_info: Elemento KeyInfo.
        
        Returns:
            Certificado X.509 o None.
        """
        try:
            x509_cert_elem = key_info.find(
                f'.//{{{DSIG_NS}}}X509Certificate'
            )
            
            if x509_cert_elem is None or not x509_cert_elem.text:
                return None
            
            # Decodificar base64
            cert_der = base64.b64decode(x509_cert_elem.text)
            
            # Cargar certificado
            certificate = x509.load_der_x509_certificate(
                cert_der,
                backend=default_backend()
            )
            
            return certificate
            
        except Exception:
            return None
    
    def _validate_digest(self, reference: etree.Element) -> bool:
        """
        Valida el digest del elemento referenciado.
        
        Args:
            reference: Elemento Reference.
        
        Returns:
            True si el digest es válido.
        """
        try:
            # Obtener URI del elemento referenciado
            uri = reference.get('URI')
            if not uri or not uri.startswith('#'):
                return False
            
            reference_id = uri[1:]  # Remover '#'
            
            # Encontrar elemento referenciado
            referenced_elem = self.root.xpath(f'//*[@Id="{reference_id}"]')
            if not referenced_elem:
                return False
            
            # Obtener digest esperado
            digest_value_elem = reference.find(f'{{{DSIG_NS}}}DigestValue')
            if digest_value_elem is None or not digest_value_elem.text:
                return False
            
            expected_digest = digest_value_elem.text.strip()
            
            # Calcular digest actual
            c14n_xml = etree.tostring(
                referenced_elem[0],
                method='c14n',
                exclusive=True,
                with_comments=False
            )
            
            digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
            digest.update(c14n_xml)
            actual_digest = base64.b64encode(digest.finalize()).decode('utf-8')
            
            return actual_digest == expected_digest
            
        except Exception:
            return False
    
    def _validate_signature(
        self,
        signed_info: etree.Element,
        signature_value: etree.Element,
        certificate: x509.Certificate
    ) -> bool:
        """
        Valida la firma del SignedInfo.
        
        Args:
            signed_info: Elemento SignedInfo.
            signature_value: Elemento SignatureValue.
            certificate: Certificado del firmante.
        
        Returns:
            True si la firma es válida.
        """
        try:
            # Obtener valor de la firma
            if not signature_value.text:
                return False
            
            signature_bytes = base64.b64decode(signature_value.text)
            
            # Canonicalizar SignedInfo
            c14n_signed_info = etree.tostring(
                signed_info,
                method='c14n',
                exclusive=True,
                with_comments=False
            )
            
            # Verificar firma con la clave pública del certificado
            public_key = certificate.public_key()
            
            try:
                public_key.verify(
                    signature_bytes,
                    c14n_signed_info,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                return True
            except Exception:
                return False
                
        except Exception:
            return False
    
    def _get_certificate_subject(self, certificate: x509.Certificate) -> dict:
        """
        Extrae información del subject del certificado.
        
        Args:
            certificate: Certificado X.509.
        
        Returns:
            Diccionario con información del subject.
        """
        try:
            subject = certificate.subject
            return {
                'common_name': subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value if subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME) else None,
                'organization': subject.get_attributes_for_oid(x509.NameOID.ORGANIZATION_NAME)[0].value if subject.get_attributes_for_oid(x509.NameOID.ORGANIZATION_NAME) else None,
                'country': subject.get_attributes_for_oid(x509.NameOID.COUNTRY_NAME)[0].value if subject.get_attributes_for_oid(x509.NameOID.COUNTRY_NAME) else None,
            }
        except Exception:
            return {}


def validate_xml_signature(xml_content: str) -> SignatureValidationResult:
    """
    Valida la firma digital de un documento XML.
    
    Args:
        xml_content: Contenido XML como string.
    
    Returns:
        Resultado de la validación.
    """
    validator = XMLSignatureValidator(xml_content)
    return validator.validate()
