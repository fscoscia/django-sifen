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

    def firmar_xml(self, xml: str, reference_id: str, csc: Optional[str] = None) -> str:
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

        # Generar XMLs firmados (como árboles XML, no strings)
        arboles_firmados = []
        for idx, documento in enumerate(documentos, 1):
            # Generar CDC si no existe
            if not documento.CDC:
                documento.generate_cdc()

            # Generar XML
            xml_string = generate_xml(documento, self.config.ambiente)

            # Firmar - parsear sin whitespace para que DigestValue coincida con la
            # re-serialización compacta que hace SIFEN al procesar el lote en forma asíncrona
            parser = etree.XMLParser(remove_blank_text=True)
            root = etree.fromstring(xml_string.encode("utf-8"), parser=parser)
            signed_root = sign_xml_element(root, self.config, documento.CDC)

            # Actualizar QR con DigestValue, IdCSC y cHashQR después de firmar
            from sifen.crypto.signature import update_qr_after_signature

            update_qr_after_signature(signed_root, self.config.csc)

            # Serializar el XML firmado — etree.tostring codifica & como &amp; correctamente
            xml_firmado = etree.tostring(signed_root, encoding="unicode")

            arboles_firmados.append(xml_firmado)
        # Enviar lote a SIFEN (ahora recibe árboles XML en lugar de strings)
        return recibir_lote(self.config, arboles_firmados)

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

        # Generar ID del evento numérico (1-10 caracteres según manual)
        # Usar timestamp de 10 dígitos (segundos desde epoch)
        evento_id = str(int(datetime.now().timestamp()))[:10]

        # Crear gestión de evento
        evento = GestionEvento(
            Id=evento_id,
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

        # Debug: mostrar XML generado
        print("\n" + "=" * 70)
        print("DEBUG: XML del Evento ANTES de firmar")
        print("=" * 70)
        print(xml_string)
        print("=" * 70 + "\n")

        # Firmar solo rEve (no todo rGesEve)
        # Parsear el XML generado
        root = etree.fromstring(xml_string.encode("utf-8"))  # root = rGesEve

        # Encontrar el elemento rEve dentro de rGesEve
        r_eve = root.find("rEve")
        if r_eve is None:
            r_eve = root.find(".//{http://ekuatia.set.gov.py/sifen/xsd}rEve")

        if r_eve is None:
            raise Exception("No se encontró el elemento rEve para firmar")

        # Firmar rEve (la firma se agregará como hermano de rEve dentro de rGesEve)
        signed_root = sign_xml_element(root, self.config, evento.Id)
        xml_firmado = etree.tostring(signed_root, encoding="unicode")

        # Debug: mostrar XML firmado
        print("\n" + "=" * 70)
        print("DEBUG: XML del Evento DESPUÉS de firmar")
        print("=" * 70)
        print(xml_firmado)
        print("=" * 70 + "\n")

        # Enviar a SIFEN
        return recibir_evento(self.config, xml_firmado)

    def enviar_conformidad(
        self, cdc: str, motivo: str = None
    ) -> "RespuestaRecepcionEvento":
        """
        Envía conformidad total de recepción de un documento.

        Args:
            cdc: CDC del documento.
            motivo: Motivo opcional.

        Returns:
            Respuesta de SIFEN.
        """
        from sifen.models.eventos import GestionEvento, EventoConformidadParcial
        from sifen.xml.generator_evento import generate_evento_xml
        from sifen.crypto import sign_xml_element
        from sifen.services import recibir_evento, TIPO_EVENTO_CONFORMIDAD
        from lxml import etree
        from datetime import datetime

        # Conformidad total (iTipConf=1)
        evento_conf = EventoConformidadParcial(Id=cdc, iTipConf=1)

        # Generar ID del evento numérico (1-10 caracteres según manual)
        # Usar timestamp de 10 dígitos (segundos desde epoch)
        evento_id = str(int(datetime.now().timestamp()))[:10]

        evento = GestionEvento(
            Id=evento_id,
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

        # Para eventos de receptor, usar el CDC del evento (no el Id de GestionEvento)
        # porque rEve no tiene atributo Id en eventos de receptor
        id_para_firma = evento_conf.Id  # CDC del documento
        signed_root = sign_xml_element(root, self.config, id_para_firma)
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
            Id="1",
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

    def enviar_desconocimiento(
        self, cdc: str, motivo: str
    ) -> "RespuestaRecepcionEvento":
        """
        Envía desconocimiento de un documento.

        Args:
            cdc: CDC del documento.
            motivo: Motivo del desconocimiento.

        Returns:
            Respuesta de SIFEN.
        """
        from sifen.models.eventos import GestionEvento, EventoDesconocimiento
        from sifen.xml.generator_evento import XMLEventoGenerator
        from sifen.crypto import sign_xml_element
        from sifen.services import recibir_evento, TIPO_EVENTO_DESCONOCIMIENTO
        from lxml import etree
        from datetime import datetime

        evento_desc = EventoDesconocimiento(mOtEve=motivo)

        evento = GestionEvento(
            Id="1",
            dFecFirma=datetime.now(),
            iTipEve=TIPO_EVENTO_DESCONOCIMIENTO,
            dDesTipEve="Desconocimiento",
            Id_CDC=cdc,
            mOtEve=motivo,
            gGroupGesEve=evento_desc,
        )

        # Generar, firmar y enviar
        generator = XMLEventoGenerator()
        xml_string = generator.generate(evento)
        root = etree.fromstring(xml_string.encode("utf-8"))
        signed_root = sign_xml_element(root, self.config, evento.Id)
        xml_firmado = etree.tostring(signed_root, encoding="unicode")

        return recibir_evento(self.config, xml_firmado)

    def nominar_documento(
        self,
        cdc: str,
        motivo: str,
        ruc: str,
        dv: int,
        nombre: str,
        naturaleza_receptor: int = 1,
        tipo_operacion: int = 1,
        codigo_pais: str = "PRY",
        descripcion_pais: str = "Paraguay",
        tipo_contribuyente: int = 1,
    ) -> "RespuestaRecepcionEvento":
        """
        Nomina un documento electrónico (asigna RUC/identidad a factura innominada).

        Args:
            cdc: CDC del documento a nominar.
            motivo: Motivo de la nominación.
            ruc: RUC del receptor (sin DV).
            dv: Dígito verificador del RUC.
            nombre: Nombre o razón social del receptor.
            naturaleza_receptor: Naturaleza del receptor (1=Contribuyente, 2=No contribuyente).
            tipo_operacion: Tipo de operación (1-10).
            codigo_pais: Código del país (3 caracteres).
            descripcion_pais: Descripción del país.
            tipo_contribuyente: Tipo de contribuyente (1 o 2).

        Returns:
            Respuesta de SIFEN.
        """
        from sifen.models.eventos import GestionEvento, EventoNominacion
        from sifen.xml.generator_evento import generate_evento_xml
        from sifen.crypto import sign_xml_element
        from sifen.services import recibir_evento, TIPO_EVENTO_NOMINACION
        from lxml import etree
        from datetime import datetime

        evento_nom = EventoNominacion(
            Id=cdc,
            mOtEve=motivo,
            iNatRec=naturaleza_receptor,
            iTiOpe=tipo_operacion,
            cPaisRec=codigo_pais,
            dDesPaisRe=descripcion_pais,
            iTiContRec=tipo_contribuyente,
            dRucRec=ruc,
            dDVRec=dv,
            dNomRec=nombre,
        )

        evento_id = str(int(datetime.now().timestamp()))[:10]

        evento = GestionEvento(
            Id=evento_id,
            dFecFirma=datetime.now(),
            iTipEve=TIPO_EVENTO_NOMINACION,
            dDesTipEve="Nominación",
            Id_CDC=cdc,
            mOtEve=motivo,
            gGroupGesEve=evento_nom,
        )

        is_valid, error = evento.validate()
        if not is_valid:
            from sifen.exceptions import ValidationException

            raise ValidationException(f"Evento inválido: {error}")

        xml_string = generate_evento_xml(evento)
        root = etree.fromstring(xml_string.encode("utf-8"))
        signed_root = sign_xml_element(root, self.config, evento.Id)
        xml_firmado = etree.tostring(signed_root, encoding="unicode")

        return recibir_evento(self.config, xml_firmado)

    def inutilizar_numeracion(
        self,
        motivo: str,
        timbrado: int,
        establecimiento: str,
        punto_expedicion: str,
        numero_inicial: str,
        numero_final: str,
        tipo_documento: int,
    ) -> "RespuestaRecepcionEvento":
        """
        Inutiliza un rango de numeración de documentos.

        Args:
            motivo: Motivo de la inutilización.
            timbrado: Número de timbrado.
            establecimiento: Establecimiento (3 dígitos).
            punto_expedicion: Punto de expedición (3 dígitos).
            numero_inicial: Número inicial del rango (7 dígitos).
            numero_final: Número final del rango (7 dígitos).
            tipo_documento: Tipo de documento electrónico (1-8).

        Returns:
            Respuesta de SIFEN.
        """
        from sifen.models.eventos import GestionEvento, EventoInutilizacion
        from sifen.xml.generator_evento import XMLEventoGenerator
        from sifen.crypto import sign_xml_element
        from sifen.services import recibir_evento, TIPO_EVENTO_INUTILIZACION
        from lxml import etree
        from datetime import datetime

        evento_inu = EventoInutilizacion(
            mOtEve=motivo,
            dNumTim=timbrado,
            dEst=establecimiento,
            dPunExp=punto_expedicion,
            dNumIn=numero_inicial,
            dNumFin=numero_final,
            iTiDE=tipo_documento,
        )

        # Generar CDC ficticio para inutilización
        cdc_ficticio = "0" * 44

        # Generar ID del evento numérico (1-10 caracteres según manual)
        # Usar timestamp de 10 dígitos (segundos desde epoch)
        evento_id = str(int(datetime.now().timestamp()))[:10]

        evento = GestionEvento(
            Id=evento_id,
            dFecFirma=datetime.now(),
            iTipEve=TIPO_EVENTO_INUTILIZACION,
            dDesTipEve="Inutilización",
            Id_CDC=cdc_ficticio,
            mOtEve=motivo,
            gGroupGesEve=evento_inu,
        )

        # Generar, firmar y enviar
        generator = XMLEventoGenerator()
        xml_string = generator.generate(evento)
        root = etree.fromstring(xml_string.encode("utf-8"))
        signed_root = sign_xml_element(root, self.config, evento.Id)
        xml_firmado = etree.tostring(signed_root, encoding="unicode")

        return recibir_evento(self.config, xml_firmado)

    def enviar_lote_eventos(self, eventos_xml: list) -> "RespuestaRecepcionLoteEventos":
        """
        Envía un lote de hasta 15 eventos a SIFEN.

        Args:
            eventos_xml: Lista de XMLs de eventos firmados (máximo 15).

        Returns:
            Respuesta de SIFEN con el estado de cada evento.
        """
        from sifen.services import recibir_lote_eventos

        return recibir_lote_eventos(self.config, eventos_xml)

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

    def generar_kude(
        self,
        documento: "DocumentoElectronico",
        output_path: Optional[str] = None,
        logo_path: Optional[str] = None,
    ) -> bytes:
        """
        Genera el KuDE (representación gráfica en PDF) del documento electrónico.

        El KuDE es la representación gráfica del documento electrónico según
        el Manual Técnico SIFEN v150, Capítulo 13. Puede ser impreso o enviado
        digitalmente al receptor.

        Args:
            documento: Documento electrónico con CDC generado.
            output_path: Ruta donde guardar el PDF (opcional).
            logo_path: Ruta del logo del emisor para incluir en el KuDE (opcional).

        Returns:
            Bytes del PDF generado.

        Raises:
            ImportError: Si ReportLab no está instalado.
            ValueError: Si el documento no tiene CDC generado.

        Example:
            >>> # Después de enviar un documento
            >>> respuesta = client.enviar_documento(documento)
            >>> if respuesta.aprobado:
            ...     # Generar KuDE
            ...     pdf_bytes = client.generar_kude(
            ...         documento,
            ...         output_path="/path/to/factura.pdf",
            ...         logo_path="/path/to/logo.png"
            ...     )
            ...     print(f"KuDE generado: {len(pdf_bytes)} bytes")
        """
        from sifen.kude_generator import generar_kude

        return generar_kude(
            documento=documento,
            output_path=output_path,
            logo_path=logo_path,
            ambiente=self.config.ambiente,
        )

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
