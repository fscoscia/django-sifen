"""
Constantes y URLs para la librería SIFEN.
"""

# Versión del SDK
SDK_VERSION = "0.1.0"
SIFEN_VERSION = "150"

# URLs base para ambientes
URL_BASE_DEV = "https://sifen-test.set.gov.py"
URL_BASE_PROD = "https://sifen.set.gov.py"

# URLs de consulta QR
URL_CONSULTA_QR_DEV = "https://ekuatia.set.gov.py/consultas-test/qr?"
URL_CONSULTA_QR_PROD = "https://ekuatia.set.gov.py/consultas/qr?"

# Endpoints de servicios web
PATH_RECIBE = "/de/ws/sync/recibe.wsdl"
PATH_RECIBE_LOTE = "/de/ws/async/recibe-lote.wsdl"
PATH_EVENTO = "/de/ws/eventos/evento.wsdl"
PATH_EVENTO_LOTE = "/de/ws/eventos/lote-evento.wsdl"
PATH_CONSULTA_LOTE = "/de/ws/consultas/consulta-lote.wsdl"
PATH_CONSULTA_RUC = "/de/ws/consultas/consulta-ruc.wsdl"
PATH_CONSULTA = "/de/ws/consultas/consulta.wsdl"

# Namespaces XML
NAMESPACE_SIFEN = "http://ekuatia.set.gov.py/sifen/xsd"
NAMESPACE_SOAP = "http://www.w3.org/2003/05/soap-envelope"
NAMESPACE_DS = "http://www.w3.org/2000/09/xmldsig#"

# Timeouts HTTP (en segundos)
HTTP_CONNECT_TIMEOUT = 30
HTTP_READ_TIMEOUT = 120

# CSC de prueba (solo para ambiente de desarrollo)
CSC_DEV_ID_1 = "0001"
CSC_DEV_VALUE_1 = "ABCD0000000000000000000000000000"
CSC_DEV_ID_2 = "0002"
CSC_DEV_VALUE_2 = "EFGH0000000000000000000000000000"

# Algoritmos criptográficos
DIGEST_ALGORITHM = "sha256"
SIGNATURE_ALGORITHM = "rsa-sha256"
CANONICALIZATION_METHOD = "http://www.w3.org/TR/2001/REC-xml-c14n-20010315"

# Códigos de estado de documentos
ESTADO_APROBADO = "aprobado"
ESTADO_RECHAZADO = "rechazado"
ESTADO_PENDIENTE = "pendiente"
ESTADO_CANCELADO = "cancelado"

# Tipos de documento electrónico
TIPO_FACTURA_ELECTRONICA = 1
TIPO_FACTURA_ELECTRONICA_EXPORTACION = 2
TIPO_FACTURA_ELECTRONICA_IMPORTACION = 3
TIPO_AUTOFACTURA_ELECTRONICA = 4
TIPO_NOTA_CREDITO_ELECTRONICA = 5
TIPO_NOTA_DEBITO_ELECTRONICA = 6
TIPO_NOTA_REMISION_ELECTRONICA = 7
TIPO_COMPROBANTE_RETENCION_ELECTRONICO = 8
