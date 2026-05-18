"""
Cliente principal para interactuar con SIFEN.
"""

from typing import Optional, List, Tuple
from threading import Lock

from sifen.config import SifenConfig
from sifen.exceptions import ConfigurationException


class SifenClient:
    """
    Cliente principal de la librería SIFEN.

    Esta clase proporciona una interfaz unificada para todas las operaciones
    con SIFEN, similar a la clase Sifen.java de la implementación Java.
    """

    _config: Optional[SifenConfig] = None
    _config_lock = Lock()

    @classmethod
    def set_config(cls, config: SifenConfig) -> None:
        """
        Establece la configuración global de SIFEN.

        Args:
            config: Instancia de SifenConfig con la configuración.

        Raises:
            ConfigurationException: Si la configuración es inválida.
        """
        if config is None:
            raise ConfigurationException("La configuración de Sifen no debe ser nula.")

        config.validar()

        with cls._config_lock:
            cls._config = config

    @classmethod
    def get_config(cls) -> Optional[SifenConfig]:
        """
        Obtiene la configuración global de SIFEN.

        Returns:
            La configuración establecida o None si no se ha configurado.
        """
        return cls._config

    @classmethod
    def _ensure_config(cls) -> SifenConfig:
        """
        Verifica que la configuración esté establecida.

        Returns:
            La configuración establecida.

        Raises:
            ConfigurationException: Si no se ha establecido la configuración.
        """
        if cls._config is None:
            raise ConfigurationException("Falta establecer la configuración de Sifen.")
        return cls._config

    def __init__(self, config: Optional[SifenConfig] = None):
        """
        Inicializa el cliente SIFEN.

        Args:
            config: Configuración opcional. Si no se proporciona, usa la global.
        """
        if config is not None:
            self.config = config
        else:
            self.config = self._ensure_config()

    def enviar_documento(self, documento) -> "RespuestaRecepcionDE":
        """
        Envía un Documento Electrónico a SIFEN.

        Este método realiza todo el flujo automáticamente:
        1. Valida el documento
        2. Genera el CDC
        3. Genera el XML
        4. Firma digitalmente
        5. Envía a SIFEN

        Args:
            documento: DocumentoElectronico a enviar.

        Returns:
            Respuesta de SIFEN.

        Raises:
            SifenException: Si hay error en el proceso.
        """
        from sifen.models.documento import DocumentoElectronico
        from sifen.xml import generate_xml
        from sifen.crypto import sign_xml_element
        from sifen.services import recibir_de
        from lxml import etree

        # 1. Validar documento
        is_valid, error = documento.validate()
        if not is_valid:
            from sifen.exceptions import ValidationException

            raise ValidationException(f"Documento inválido: {error}")

        # 2. Generar CDC si no existe
        if not documento.CDC:
            documento.generate_cdc()

        # 3. Generar XML
        xml_string = generate_xml(documento, self.config.ambiente)

        # 4. Firmar y actualizar QR
        from sifen.crypto.signature import update_qr_after_signature
        root = etree.fromstring(xml_string.encode("utf-8"))
        signed_root = sign_xml_element(root, self.config, documento.CDC)
        update_qr_after_signature(signed_root, self.config.csc)
        xml_firmado = etree.tostring(signed_root, encoding="unicode")

        # 5. Enviar a SIFEN
        return recibir_de(self.config, xml_firmado)

    def consultar_documento(self, cdc: str) -> "RespuestaConsultaDE":
        """
        Consulta el estado de un Documento Electrónico.

        Args:
            cdc: Código de Control del documento.

        Returns:
            Respuesta de SIFEN.
        """
        from sifen.services import consultar_de

        return consultar_de(self.config, cdc)

    def consultar_ruc(self, ruc: str, dv: str) -> "RespuestaConsultaRUC":
        """
        Consulta un RUC en SIFEN.

        Args:
            ruc: RUC sin dígito verificador.
            dv: Dígito verificador.

        Returns:
            Respuesta de SIFEN.
        """
        from sifen.services import consultar_ruc

        return consultar_ruc(self.config, ruc, dv)

    def validar_documento(self, documento) -> Tuple[bool, Optional[str]]:
        """
        Valida un documento sin enviarlo.

        Args:
            documento: DocumentoElectronico a validar.

        Returns:
            Tupla (es_valido, mensaje_error).
        """
        return documento.validate()

    def generar_xml(self, documento) -> str:
        """
        Genera el XML de un documento sin firmarlo ni enviarlo.

        Args:
            documento: DocumentoElectronico.

        Returns:
            XML como string.
        """
        from sifen.xml import generate_xml

        # Generar CDC si no existe
        if not documento.CDC:
            documento.generate_cdc()

        return generate_xml(documento, self.config.ambiente)

    def firmar_xml(
        self, xml: str, reference_id: str, csc: Optional[str] = None
    ) -> str:
        """
        Firma un XML con el certificado configurado y actualiza el código QR.

        Args:
            xml: XML a firmar.
            reference_id: ID del elemento a referenciar en la firma.
            csc: Código Secreto del Contribuyente (CSC). Si no se proporciona, usa el del config.

        Returns:
            XML firmado con QR actualizado.
        """
        from sifen.crypto.signature import sign_xml_string

        return sign_xml_string(xml, self.config, reference_id, csc or self.config.csc)

    @classmethod
    def validar_ruc(cls, ruc: str, dv: Optional[str] = None) -> bool:
        """
        Valida un RUC.

        Args:
            ruc: RUC sin dígito verificador o con formato completo.
            dv: Dígito verificador (opcional).

        Returns:
            True si es válido.
        """
        from sifen.utils import validar_ruc

        return validar_ruc(ruc, dv)

    @classmethod
    def validar_cdc(cls, cdc: str) -> bool:
        """
        Valida un CDC.

        Args:
            cdc: Código de Control.

        Returns:
            True si es válido.
        """
        from sifen.utils import validar_cdc

        return validar_cdc(cdc)

    @classmethod
    def calcular_dv_ruc(cls, ruc: str) -> int:
        """
        Calcula el dígito verificador de un RUC.

        Args:
            ruc: RUC sin dígito verificador.

        Returns:
            Dígito verificador.
        """
        from sifen.utils import calcular_dv_ruc

        return calcular_dv_ruc(ruc)

    @classmethod
    def formatear_ruc(cls, ruc: str, dv: str) -> str:
        """
        Formatea un RUC.

        Args:
            ruc: RUC sin dígito verificador.
            dv: Dígito verificador.

        Returns:
            RUC formateado (ej: "80012345-6").
        """
        from sifen.utils import formatear_ruc

        return formatear_ruc(ruc, dv)

    def enviar_lote(self, documentos: list) -> "RespuestaRecepcionLote":
        """
        Envía un lote de documentos electrónicos a SIFEN.

        Este método realiza todo el flujo automáticamente para cada documento:
        1. Valida todos los documentos
        2. Genera CDC para cada uno
        3. Genera XML para cada uno
        4. Firma digitalmente cada XML
        5. Envía el lote completo a SIFEN

        Args:
            documentos: Lista de DocumentoElectronico (máximo 50).

        Returns:
            Respuesta de SIFEN con el estado del lote.

        Raises:
            SifenException: Si hay error en el proceso.
            ValueError: Si la lista está vacía o tiene más de 50 documentos.
        """
        from sifen.xml import generate_xml
        from sifen.crypto import sign_xml_element
        from sifen.services import recibir_lote
        from sifen.exceptions import ValidationException
        from lxml import etree

        # Validar cantidad
        if not documentos:
            raise ValueError("La lista de documentos no puede estar vacía")

        if len(documentos) > 50:
            raise ValueError("El lote no puede contener más de 50 documentos")

        # Validar todos los documentos
        for i, documento in enumerate(documentos):
            is_valid, error = documento.validate()
            if not is_valid:
                raise ValidationException(f"Documento {i+1} inválido: {error}")

        # Generar XMLs firmados
        xmls_firmados = []
        for documento in documentos:
            # Generar CDC si no existe
            if not documento.CDC:
                documento.generate_cdc()

            # Generar XML
            xml_string = generate_xml(documento, self.config.ambiente)

            # Firmar
            root = etree.fromstring(xml_string.encode("utf-8"))
            signed_root = sign_xml_element(root, self.config, documento.Id)
            xml_firmado = etree.tostring(signed_root, encoding="unicode")

            xmls_firmados.append(xml_firmado)

        # Enviar lote a SIFEN
        return recibir_lote(self.config, xmls_firmados)

    def consultar_lote(self, numero_lote: str) -> "RespuestaConsultaLote":
        """
        Consulta el estado de un lote de documentos.

        Args:
            numero_lote: Número de lote asignado por SIFEN.

        Returns:
            Respuesta de SIFEN con el estado del lote.
        """
        from sifen.services import consultar_lote

        return consultar_lote(self.config, numero_lote)

    def cancelar_documento(self, cdc: str, motivo: str) -> "RespuestaRecepcionEvento":
        """
        Cancela un documento electrónico.

        Args:
            cdc: CDC del documento a cancelar.
            motivo: Motivo de la cancelación.

        Returns:
            Respuesta de SIFEN.
        """
        from sifen.models.eventos import GestionEvento, EventoCancelacion
        from sifen.xml.generator_evento import generate_evento_xml
        from sifen.crypto import sign_xml_element
        from sifen.services import recibir_evento, TIPO_EVENTO_CANCELACION
        from lxml import etree
        from datetime import datetime

        # Crear evento de cancelación
        evento_canc = EventoCancelacion(mOtEve=motivo)

        # Crear gestión de evento
        evento = GestionEvento(
            Id=f"EVE{datetime.now().strftime('%Y%m%d%H%M%S')}",
            dFecFirma=datetime.now(),
            iTipEve=TIPO_EVENTO_CANCELACION,
            dDesTipEve="Cancelación",
            Id_CDC=cdc,
            mOtEve=motivo,
            gGroupGesEve=evento_canc,
        )

        # Validar
        is_valid, error = evento.validate()
        if not is_valid:
            from sifen.exceptions import ValidationException

            raise ValidationException(f"Evento inválido: {error}")

        # Generar XML
        xml_string = generate_evento_xml(evento)

        # Firmar
        root = etree.fromstring(xml_string.encode("utf-8"))
        signed_root = sign_xml_element(root, self.config, evento.Id)
        xml_firmado = etree.tostring(signed_root, encoding="unicode")

        # Enviar a SIFEN
        return recibir_evento(self.config, xml_firmado)

    def enviar_conformidad(
        self, cdc: str, motivo: str = None
    ) -> "RespuestaRecepcionEvento":
        """
        Envía conformidad de recepción de un documento.

        Args:
            cdc: CDC del documento.
            motivo: Motivo opcional.

        Returns:
            Respuesta de SIFEN.
        """
        from sifen.models.eventos import GestionEvento, EventoConformidad
        from sifen.xml.generator_evento import generate_evento_xml
        from sifen.crypto import sign_xml_element
        from sifen.services import recibir_evento, TIPO_EVENTO_CONFORMIDAD
        from lxml import etree
        from datetime import datetime

        evento_conf = EventoConformidad(mOtEve=motivo)

        evento = GestionEvento(
            Id=f"EVE{datetime.now().strftime('%Y%m%d%H%M%S')}",
            dFecFirma=datetime.now(),
            iTipEve=TIPO_EVENTO_CONFORMIDAD,
            dDesTipEve="Conformidad",
            Id_CDC=cdc,
            mOtEve=motivo,
            gGroupGesEve=evento_conf,
        )

        # Generar, firmar y enviar
        xml_string = generate_evento_xml(evento)
        root = etree.fromstring(xml_string.encode("utf-8"))
        signed_root = sign_xml_element(root, self.config, evento.Id)
        xml_firmado = etree.tostring(signed_root, encoding="unicode")

        return recibir_evento(self.config, xml_firmado)

    def enviar_disconformidad(
        self, cdc: str, motivo: str
    ) -> "RespuestaRecepcionEvento":
        """
        Envía disconformidad de un documento.

        Args:
            cdc: CDC del documento.
            motivo: Motivo de la disconformidad.

        Returns:
            Respuesta de SIFEN.
        """
        from sifen.models.eventos import GestionEvento, EventoDisconformidad
        from sifen.xml.generator_evento import generate_evento_xml
        from sifen.crypto import sign_xml_element
        from sifen.services import recibir_evento, TIPO_EVENTO_DISCONFORMIDAD
        from lxml import etree
        from datetime import datetime

        evento_disconf = EventoDisconformidad(mOtEve=motivo)

        evento = GestionEvento(
            Id=f"EVE{datetime.now().strftime('%Y%m%d%H%M%S')}",
            dFecFirma=datetime.now(),
            iTipEve=TIPO_EVENTO_DISCONFORMIDAD,
            dDesTipEve="Disconformidad",
            Id_CDC=cdc,
            mOtEve=motivo,
            gGroupGesEve=evento_disconf,
        )

        # Generar, firmar y enviar
        xml_string = generate_evento_xml(evento)
        root = etree.fromstring(xml_string.encode("utf-8"))
        signed_root = sign_xml_element(root, self.config, evento.Id)
        xml_firmado = etree.tostring(signed_root, encoding="unicode")

        return recibir_evento(self.config, xml_firmado)

    def validar_firma_xml(self, xml: str) -> "SignatureValidationResult":
        """
        Valida la firma digital de un XML.

        Útil para verificar XMLs recibidos de SIFEN o terceros.

        Args:
            xml: String XML con firma digital.

        Returns:
            Resultado de la validación con detalles del certificado.

        Example:
            >>> resultado = client.validar_firma_xml(xml_recibido)
            >>> if resultado.is_valid:
            ...     print(f"✓ Firma válida - Emisor: {resultado.subject}")
            ... else:
            ...     print(f"✗ Firma inválida: {resultado.error}")
        """
        from sifen.crypto import validate_xml_signature

        return validate_xml_signature(xml)

    def validar_firma_archivo(self, ruta_archivo: str) -> "SignatureValidationResult":
        """
        Valida la firma digital de un archivo XML.

        Args:
            ruta_archivo: Ruta al archivo XML firmado.

        Returns:
            Resultado de la validación.

        Example:
            >>> resultado = client.validar_firma_archivo("/path/to/documento.xml")
            >>> print(f"Válido: {resultado.is_valid}")
        """
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            xml_content = f.read()
        return self.validar_firma_xml(xml_content)

    def generar_url_qr(self, cdc: str) -> str:
        """
        Genera la URL de consulta QR para un CDC.

        Esta URL puede ser convertida a código QR para que los clientes
        puedan consultar el documento electrónico desde sus dispositivos.

        Args:
            cdc: Código de Control del documento (44 caracteres).

        Returns:
            URL completa de consulta QR.

        Example:
            >>> url = client.generar_url_qr("01001001000000112024050412300080012345601")
            >>> print(url)
            https://ekuatia.set.gov.py/consultas/qr?nVersion=150&Id=01001001...

            >>> # Generar QR con librería externa
            >>> import qrcode
            >>> qr = qrcode.make(url)
            >>> qr.save("documento_qr.png")
        """
        return f"{self.config.url_consulta_qr}{cdc}"

    @classmethod
    def validar_firma_xml_estatico(cls, xml: str) -> "SignatureValidationResult":
        """
        Valida la firma digital de un XML sin necesidad de instanciar el cliente.

        Método estático útil para validaciones rápidas sin configuración.

        Args:
            xml: String XML con firma digital.

        Returns:
            Resultado de la validación.

        Example:
            >>> from sifen import SifenClient
            >>> resultado = SifenClient.validar_firma_xml_estatico(xml)
            >>> print(f"Firma válida: {resultado.is_valid}")
        """
        from sifen.crypto import validate_xml_signature

        return validate_xml_signature(xml)
