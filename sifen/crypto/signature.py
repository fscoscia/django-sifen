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
import hashlib

from sifen.config import SifenConfig
from sifen.exceptions import SignatureException
from sifen.crypto.keystore import load_pfx_certificate

# Namespaces XML
DSIG_NS = "http://www.w3.org/2000/09/xmldsig#"
# No usar prefijo ds:, solo xmlns por defecto
NSMAP = {None: DSIG_NS}


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
            raise SignatureException(f"Error al cargar el certificado: {str(e)}") from e

    def sign_document(
        self,
        xml_element: etree.Element,
        reference_id: str,
        signature_parent: Optional[etree.Element] = None,
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
            # 1. Buscar gCamFuFD para insertar Signature antes de él
            sifen_ns = "http://ekuatia.set.gov.py/sifen/xsd"
            gcamfufd = signature_parent.find(f"{{{sifen_ns}}}gCamFuFD")

            # 2. Crear elemento Signature
            if gcamfufd is not None:
                # Insertar antes de gCamFuFD
                index = list(signature_parent).index(gcamfufd)
                signature = etree.Element(f"{{{DSIG_NS}}}Signature", nsmap=NSMAP)
                signature_parent.insert(index, signature)
            else:
                # Agregar al final si no hay gCamFuFD
                signature = etree.SubElement(
                    signature_parent, f"{{{DSIG_NS}}}Signature", nsmap=NSMAP
                )

            # 2. Crear SignedInfo
            signed_info = self._create_signed_info(signature, reference_id)

            # 3. Calcular firma del SignedInfo
            signature_value = self._calculate_signature(signed_info)

            # 4. Añadir SignatureValue
            sig_value_elem = etree.SubElement(signature, f"{{{DSIG_NS}}}SignatureValue")
            sig_value_elem.text = base64.b64encode(signature_value).decode("utf-8")

            # 5. Añadir KeyInfo con el certificado
            self._add_key_info(signature)

            return xml_element

        except Exception as e:
            raise SignatureException(
                f"Error al firmar el documento XML: {str(e)}"
            ) from e

    def _create_signed_info(
        self, signature_elem: etree.Element, reference_id: str
    ) -> etree.Element:
        """
        Crea el elemento SignedInfo.

        Args:
            signature_elem: Elemento Signature padre.
            reference_id: ID del elemento referenciado.

        Returns:
            Elemento SignedInfo.
        """
        signed_info = etree.SubElement(signature_elem, f"{{{DSIG_NS}}}SignedInfo")

        # CanonicalizationMethod
        c14n_method = etree.SubElement(
            signed_info,
            f"{{{DSIG_NS}}}CanonicalizationMethod",
            Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#",
        )

        # SignatureMethod
        sig_method = etree.SubElement(
            signed_info,
            f"{{{DSIG_NS}}}SignatureMethod",
            Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
        )

        # Reference
        reference = etree.SubElement(
            signed_info, f"{{{DSIG_NS}}}Reference", URI=f"#{reference_id}"
        )

        # Transforms
        transforms = etree.SubElement(reference, f"{{{DSIG_NS}}}Transforms")

        # Transform 1: Enveloped
        etree.SubElement(
            transforms,
            f"{{{DSIG_NS}}}Transform",
            Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature",
        )

        # Transform 2: Exclusive Canonicalization
        etree.SubElement(
            transforms,
            f"{{{DSIG_NS}}}Transform",
            Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#",
        )

        # DigestMethod
        etree.SubElement(
            reference,
            f"{{{DSIG_NS}}}DigestMethod",
            Algorithm="http://www.w3.org/2001/04/xmlenc#sha256",
        )

        # DigestValue (se calculará después)
        digest_value = etree.SubElement(reference, f"{{{DSIG_NS}}}DigestValue")

        # Calcular digest del elemento referenciado
        digest_value.text = self._calculate_digest(reference_id, signature_elem)

        return signed_info

    def _calculate_digest(
        self, reference_id: str, signature_elem: etree.Element
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
            raise SignatureException(f"No se encontró elemento con ID '{reference_id}'")

        # Canonicalizar el elemento
        c14n_xml = etree.tostring(
            referenced_elem[0], method="c14n", exclusive=True, with_comments=False
        )

        # Calcular SHA-256
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(c14n_xml)
        digest_bytes = digest.finalize()

        return base64.b64encode(digest_bytes).decode("utf-8")

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
            signed_info, method="c14n", exclusive=True, with_comments=False
        )

        # Firmar con RSA-SHA256
        signature = self._private_key.sign(
            c14n_signed_info, padding.PKCS1v15(), hashes.SHA256()
        )

        return signature

    def _add_key_info(self, signature_elem: etree.Element):
        """
        Añade el elemento KeyInfo con el certificado X.509.

        Args:
            signature_elem: Elemento Signature.
        """
        key_info = etree.SubElement(signature_elem, f"{{{DSIG_NS}}}KeyInfo")

        x509_data = etree.SubElement(key_info, f"{{{DSIG_NS}}}X509Data")

        x509_cert = etree.SubElement(x509_data, f"{{{DSIG_NS}}}X509Certificate")

        # Obtener certificado en formato PEM sin headers
        cert_pem = self._certificate.public_bytes(
            encoding=serialization.Encoding.PEM
        ).decode("utf-8")

        # Remover headers y newlines
        cert_base64 = cert_pem.replace("-----BEGIN CERTIFICATE-----", "")
        cert_base64 = cert_base64.replace("-----END CERTIFICATE-----", "")
        cert_base64 = cert_base64.replace("\n", "")

        x509_cert.text = cert_base64


def sign_xml_string(
    xml_string: str,
    config: SifenConfig,
    reference_id: str,
    csc: str = "ABCD0000000000000000000000000000",
) -> str:
    """
    Firma un XML en formato string y actualiza el código QR.

    Args:
        xml_string: XML como string.
        config: Configuración de SIFEN.
        reference_id: ID del elemento a referenciar.
        csc: Código Secreto del Contribuyente (CSC).

    Returns:
        XML firmado como string con QR actualizado.
    """
    # Parsear XML
    root = etree.fromstring(xml_string.encode("utf-8"))

    # Firmar
    signer = XMLSigner(config)
    signed_root = signer.sign_document(root, reference_id)

    # Actualizar QR con DigestValue y cHashQR
    update_qr_after_signature(signed_root, csc)

    # Convertir a string
    return etree.tostring(signed_root, encoding="unicode", pretty_print=True)


def sign_xml_element(
    xml_element: etree.Element, config: SifenConfig, reference_id: str
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


def update_qr_after_signature(
    signed_xml: etree.Element, csc: str = "ABCD0000000000000000000000000000"
) -> None:
    """
    Actualiza el código QR después de firmar el documento con el DigestValue y cHashQR.

    Args:
        signed_xml: Elemento XML ya firmado
        csc: Código Secreto del Contribuyente (CSC) - por defecto usa un valor de prueba
    """
    # 1. Extraer DigestValue de la firma
    digest_elem = signed_xml.find(f".//{{{DSIG_NS}}}DigestValue")
    if digest_elem is None:
        raise SignatureException("No se encontró DigestValue en la firma")

    digest_value = digest_elem.text
    # Convertir DigestValue base64 a hexadecimal de su representación ASCII
    # El QR usa la representación hexadecimal del string base64, no del contenido decodificado
    digest_hex_str = digest_value.encode("utf-8").hex()

    # 2. Buscar el elemento dCarQR actual
    sifen_ns = "http://ekuatia.set.gov.py/sifen/xsd"
    dcar_qr_elem = signed_xml.find(f".//{{{sifen_ns}}}gCamFuFD/{{{sifen_ns}}}dCarQR")
    if dcar_qr_elem is None:
        raise SignatureException("No se encontró elemento dCarQR")

    # 3. Parsear la URL actual para obtener los parámetros
    current_url = dcar_qr_elem.text
    if not current_url:
        raise SignatureException("dCarQR está vacío")

    # Extraer parámetros de la URL manualmente (no usar parse_qs para mantener formato exacto)
    from urllib.parse import urlparse

    parsed = urlparse(current_url)
    query_string = parsed.query

    # Parsear parámetros manualmente
    params_dict = {}
    for param in query_string.split("&"):
        if "=" in param:
            key, value = param.split("=", 1)
            params_dict[key] = value

    # Obtener valores
    n_version = params_dict.get("nVersion", "")
    cdc_id = params_dict.get("Id", "")
    d_fe_emi_de = params_dict.get("dFeEmiDE", "")
    d_tot_gral_ope = params_dict.get("dTotGralOpe", "0")
    d_tot_iva = params_dict.get("dTotIVA", "0")
    c_items = params_dict.get("cItems", "")

    # Usar dRucRec o dNumIDRec según lo que esté en la URL original
    if "dRucRec" in params_dict:
        rec_param = f"dRucRec={params_dict['dRucRec']}"
    elif "dNumIDRec" in params_dict:
        rec_param = f"dNumIDRec={params_dict['dNumIDRec']}"
    else:
        rec_param = "dRucRec=0"

    # IdCSC fijo
    id_csc = "0001"

    # 4. Paso 1: Concatenar datos para el hash
    # Según manual ejemplo: nVersion=150&Id=...&dFeEmiDE=...&dRucRec=...&dTotGralOpe=...&dTotIVA=...&cItems=...&DigestValue=...&IdCSC=...
    datos_paso1 = f"nVersion={n_version}&Id={cdc_id}&dFeEmiDE={d_fe_emi_de}&{rec_param}&dTotGralOpe={d_tot_gral_ope}&dTotIVA={d_tot_iva}&cItems={c_items}&DigestValue={digest_hex_str}&IdCSC={id_csc}"

    # 5. Paso 2: Concatenar con CSC al final
    datos_paso2 = datos_paso1 + csc

    # 6. Paso 3: Calcular SHA-256 del Paso 2
    c_hash_qr = hashlib.sha256(datos_paso2.encode("utf-8")).hexdigest()

    # 7. Paso 4: Construir URL final
    base_url = parsed.scheme + "://" + parsed.netloc + parsed.path
    nueva_url = f"{base_url}?{datos_paso1}&cHashQR={c_hash_qr}"

    # 8. Actualizar el elemento dCarQR
    dcar_qr_elem.text = nueva_url

