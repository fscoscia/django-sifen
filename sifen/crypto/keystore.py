"""
Módulo para manejo de certificados digitales PFX/PKCS12.

Basado en SSLContextHelper.java de la librería Java.
"""

from typing import Tuple
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography import x509

from sifen.exceptions import CertificateException


def load_pfx_certificate(
    pfx_data: bytes,
    password: str
) -> Tuple[RSAPrivateKey, x509.Certificate]:
    """
    Carga un certificado PFX/PKCS12 y extrae la clave privada y el certificado.
    
    Args:
        pfx_data: Bytes del archivo PFX.
        password: Contraseña del certificado.
    
    Returns:
        Tupla (clave_privada, certificado).
        
    Raises:
        CertificateException: Si hay error al cargar el certificado.
    """
    try:
        # Cargar el archivo PFX
        private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
            pfx_data,
            password.encode('utf-8') if password else None,
            backend=default_backend()
        )
        
        if private_key is None:
            raise CertificateException(
                "No se encontró clave privada en el certificado PFX"
            )
        
        if certificate is None:
            raise CertificateException(
                "No se encontró certificado en el archivo PFX"
            )
        
        # Verificar que sea RSA
        if not isinstance(private_key, RSAPrivateKey):
            raise CertificateException(
                f"Tipo de clave no soportado: {type(private_key).__name__}. "
                "Solo se soportan claves RSA."
            )
        
        return private_key, certificate
        
    except ValueError as e:
        raise CertificateException(
            f"Error al cargar el certificado PFX. "
            f"Verifique que la contraseña sea correcta: {str(e)}"
        ) from e
    except Exception as e:
        raise CertificateException(
            f"Error inesperado al cargar el certificado: {str(e)}"
        ) from e


def get_certificate_info(certificate: x509.Certificate) -> dict:
    """
    Extrae información del certificado X.509.
    
    Args:
        certificate: Certificado X.509.
    
    Returns:
        Diccionario con información del certificado.
    """
    subject = certificate.subject
    issuer = certificate.issuer
    
    return {
        'subject': {
            'common_name': subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value if subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME) else None,
            'organization': subject.get_attributes_for_oid(x509.NameOID.ORGANIZATION_NAME)[0].value if subject.get_attributes_for_oid(x509.NameOID.ORGANIZATION_NAME) else None,
            'country': subject.get_attributes_for_oid(x509.NameOID.COUNTRY_NAME)[0].value if subject.get_attributes_for_oid(x509.NameOID.COUNTRY_NAME) else None,
        },
        'issuer': {
            'common_name': issuer.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value if issuer.get_attributes_for_oid(x509.NameOID.COMMON_NAME) else None,
            'organization': issuer.get_attributes_for_oid(x509.NameOID.ORGANIZATION_NAME)[0].value if issuer.get_attributes_for_oid(x509.NameOID.ORGANIZATION_NAME) else None,
        },
        'serial_number': str(certificate.serial_number),
        'not_valid_before': certificate.not_valid_before_utc,
        'not_valid_after': certificate.not_valid_after_utc,
        'version': certificate.version.name,
    }


def validate_certificate(certificate: x509.Certificate) -> Tuple[bool, str]:
    """
    Valida que el certificado sea válido para uso.
    
    Nota: NO verifica la fecha de expiración (según requerimiento del usuario,
    similar a la librería Java).
    
    Args:
        certificate: Certificado a validar.
    
    Returns:
        Tupla (es_valido, mensaje).
    """
    try:
        # Verificar que tenga subject
        if not certificate.subject:
            return False, "El certificado no tiene información de subject"
        
        # Verificar que tenga clave pública
        public_key = certificate.public_key()
        if not public_key:
            return False, "El certificado no tiene clave pública"
        
        # Verificar que sea RSA
        if not isinstance(public_key, type(public_key)):
            return False, "El certificado no usa clave RSA"
        
        return True, "Certificado válido"
        
    except Exception as e:
        return False, f"Error al validar certificado: {str(e)}"
