"""
Excepciones personalizadas para la librería SIFEN.
"""


class SifenException(Exception):
    """Excepción base para todos los errores de SIFEN."""
    
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ConfigurationException(SifenException):
    """Excepción para errores de configuración."""
    pass


class ValidationException(SifenException):
    """Excepción para errores de validación de datos."""
    pass


class SignatureException(SifenException):
    """Excepción para errores de firma digital."""
    pass


class CommunicationException(SifenException):
    """Excepción para errores de comunicación con SIFEN."""
    
    def __init__(self, message: str, code: str = None, status_code: int = None):
        super().__init__(message, code)
        self.status_code = status_code


class XMLParsingException(SifenException):
    """Excepción para errores de parseo XML."""
    pass


class CertificateException(SifenException):
    """Excepción para errores relacionados con certificados."""
    pass
