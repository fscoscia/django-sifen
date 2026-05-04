"""
Módulo para firma digital de documentos XML usando XMLDSig.

Basado en SignatureHelper.java de la librería Java.
"""

from typing import Optional, Tuple
from lxml import etree
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography import x509
import base64

from sifen.config import SifenConfig
from sifen.exceptions import SignatureException
from sifen.crypto.keystore import load_pfx_certificate


# Namespaces XML
DSIG_NS = "http://www.w3.org/2000/09/xmldsig#"
NSMAP = {'ds': DSIG_NS}


class XMLSigner:
    """
    Clase para firmar documentos XML con XMLDSig.
    
    Implementa la firma digital enveloped según el estándar XML Signature
    requerido por SIFEN.
    """
    
    def __init__(self, config: SifenConfig):
        """
        Inicializa el firmador XML.
        
        Args:
            config: Configuración de SIFEN con el certificado.
        """
        self.config = config
        self._private_key = None
        self._certificate = None
        self._load_certificate()
    
    def _load_certificate(self):
        """Carga el certificado y la clave privada desde la configuración."""
        try:
            cert_bytes = self.config.get_certificado_bytes()
            password = self.config.certificado_contrasena
            
            self._private_key, self._certificate = load_pfx_certificate(
                cert_bytes, password
            )
        except Exception as e:
            raise SignatureException(
                f"Error al cargar el certificado: {str(e)}"
            ) from e
    
    def sign_document(
        self,
        xml_element: etree.Element,
        reference_id: str,
        signature_parent: Optional[etree.Element] = None
    ) -> etree.Element:
        """
        Firma un documento XML con XMLDSig.
        
        Args:
            xml_element: Elemento XML a firmar (debe tener un ID).
            reference_id: ID del elemento a referenciar en la firma.
            signature_parent: Elemento padre donde insertar la firma.
                            Si es None, se inserta en xml_element.
        
        Returns:
            Elemento XML con la firma añadida.
            
        Raises:
            SignatureException: Si hay error en la firma.
        """
        if signature_parent is None:
            signature_parent = xml_element
        
        try:
            # 1. Crear elemento Signature
            signature = etree.SubElement(
                signature_parent,
                f"{{{DSIG_NS}}}Signature",
                nsmap=NSMAP
            )
            
            # 2. Crear SignedInfo
            signed_info = self._create_signed_info(signature, reference_id)
            
            # 3. Calcular firma del SignedInfo
            signature_value = self._calculate_signature(signed_info)
            
            # 4. Añadir SignatureValue
            sig_value_elem = etree.SubElement(
                signature,
                f"{{{DSIG_NS}}}SignatureValue"
            )
            sig_value_elem.text = base64.b64encode(signature_value).decode('utf-8')
            
            # 5. Añadir KeyInfo con el certificado
            self._add_key_info(signature)
            
            return xml_element
            
        except Exception as e:
            raise SignatureException(
                f"Error al firmar el documento XML: {str(e)}"
            ) from e
    
    def _create_signed_info(
        self,
        signature_elem: etree.Element,
        reference_id: str
    ) -> etree.Element:
        """
        Crea el elemento SignedInfo.
        
        Args:
            signature_elem: Elemento Signature padre.
            reference_id: ID del elemento referenciado.
        
        Returns:
            Elemento SignedInfo.
        """
        signed_info = etree.SubElement(
            signature_elem,
            f"{{{DSIG_NS}}}SignedInfo"
        )
        
        # CanonicalizationMethod
        c14n_method = etree.SubElement(
            signed_info,
            f"{{{DSIG_NS}}}CanonicalizationMethod",
            Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"
        )
        
        # SignatureMethod
        sig_method = etree.SubElement(
            signed_info,
            f"{{{DSIG_NS}}}SignatureMethod",
            Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"
        )
        
        # Reference
        reference = etree.SubElement(
            signed_info,
            f"{{{DSIG_NS}}}Reference",
            URI=f"#{reference_id}"
        )
        
        # Transforms
        transforms = etree.SubElement(
            reference,
            f"{{{DSIG_NS}}}Transforms"
        )
        
        # Transform 1: Enveloped
        etree.SubElement(
            transforms,
            f"{{{DSIG_NS}}}Transform",
            Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"
        )
        
        # Transform 2: Exclusive Canonicalization
        etree.SubElement(
            transforms,
            f"{{{DSIG_NS}}}Transform",
            Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"
        )
        
        # DigestMethod
        etree.SubElement(
            reference,
            f"{{{DSIG_NS}}}DigestMethod",
            Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"
        )
        
        # DigestValue (se calculará después)
        digest_value = etree.SubElement(
            reference,
            f"{{{DSIG_NS}}}DigestValue"
        )
        
        # Calcular digest del elemento referenciado
        digest_value.text = self._calculate_digest(reference_id, signature_elem)
        
        return signed_info
    
    def _calculate_digest(
        self,
        reference_id: str,
        signature_elem: etree.Element
    ) -> str:
        """
        Calcula el digest SHA-256 del elemento referenciado.
        
        Args:
            reference_id: ID del elemento a hashear.
            signature_elem: Elemento Signature (para encontrar el elemento referenciado).
        
        Returns:
            Digest en base64.
        """
        # Encontrar el elemento con el ID especificado
        root = signature_elem.getroottree().getroot()
        referenced_elem = root.xpath(f'//*[@Id="{reference_id}"]')
        
        if not referenced_elem:
            raise SignatureException(
                f"No se encontró elemento con ID '{reference_id}'"
            )
        
        # Canonicalizar el elemento
        c14n_xml = etree.tostring(
            referenced_elem[0],
            method='c14n',
            exclusive=True,
            with_comments=False
        )
        
        # Calcular SHA-256
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(c14n_xml)
        digest_bytes = digest.finalize()
        
        return base64.b64encode(digest_bytes).decode('utf-8')
    
    def _calculate_signature(self, signed_info: etree.Element) -> bytes:
        """
        Calcula la firma del SignedInfo.
        
        Args:
            signed_info: Elemento SignedInfo a firmar.
        
        Returns:
            Firma en bytes.
        """
        # Canonicalizar SignedInfo
        c14n_signed_info = etree.tostring(
            signed_info,
            method='c14n',
            exclusive=True,
            with_comments=False
        )
        
        # Firmar con RSA-SHA256
        signature = self._private_key.sign(
            c14n_signed_info,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        return signature
    
    def _add_key_info(self, signature_elem: etree.Element):
        """
        Añade el elemento KeyInfo con el certificado X.509.
        
        Args:
            signature_elem: Elemento Signature.
        """
        key_info = etree.SubElement(
            signature_elem,
            f"{{{DSIG_NS}}}KeyInfo"
        )
        
        x509_data = etree.SubElement(
            key_info,
            f"{{{DSIG_NS}}}X509Data"
        )
        
        x509_cert = etree.SubElement(
            x509_data,
            f"{{{DSIG_NS}}}X509Certificate"
        )
        
        # Obtener certificado en formato PEM sin headers
        cert_pem = self._certificate.public_bytes(
            encoding=serialization.Encoding.PEM
        ).decode('utf-8')
        
        # Remover headers y newlines
        cert_base64 = cert_pem.replace('-----BEGIN CERTIFICATE-----', '')
        cert_base64 = cert_base64.replace('-----END CERTIFICATE-----', '')
        cert_base64 = cert_base64.replace('\n', '')
        
        x509_cert.text = cert_base64


def sign_xml_string(
    xml_string: str,
    config: SifenConfig,
    reference_id: str
) -> str:
    """
    Firma un string XML.
    
    Args:
        xml_string: XML como string.
        config: Configuración de SIFEN.
        reference_id: ID del elemento a referenciar.
    
    Returns:
        XML firmado como string.
    """
    # Parsear XML
    root = etree.fromstring(xml_string.encode('utf-8'))
    
    # Firmar
    signer = XMLSigner(config)
    signed_root = signer.sign_document(root, reference_id)
    
    # Convertir a string
    return etree.tostring(
        signed_root,
        encoding='unicode',
        pretty_print=True
    )


def sign_xml_element(
    xml_element: etree.Element,
    config: SifenConfig,
    reference_id: str
) -> etree.Element:
    """
    Firma un elemento XML.
    
    Args:
        xml_element: Elemento XML.
        config: Configuración de SIFEN.
        reference_id: ID del elemento a referenciar.
    
    Returns:
        Elemento XML firmado.
    """
    signer = XMLSigner(config)
    return signer.sign_document(xml_element, reference_id)
