"""
Generador de XML para Documentos Electrónicos SIFEN.

Convierte objetos Python a XML según el formato requerido por SIFEN.
"""

from typing import Optional
from lxml import etree
from decimal import Decimal
from datetime import datetime, date

from sifen.models.documento import DocumentoElectronico
from sifen.constants import NAMESPACE_SIFEN

NS = NAMESPACE_SIFEN
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
NSMAP = {
    None: NS,
    "xsi": XSI_NS,
}


class XMLGenerator:
    """
    Generador de XML para Documentos Electrónicos.

    Convierte objetos DocumentoElectronico a XML según el formato SIFEN.
    """

    def __init__(self, documento: DocumentoElectronico, ambiente=None):
        """
        Inicializa el generador.

        Args:
            documento: Documento electrónico a convertir.
            ambiente: TipoAmbiente (DEV o PROD) para la URL del QR.
        """
        self.documento = documento
        self.ambiente = ambiente

    def generate(self) -> etree.Element:
        """
        Genera el XML completo del documento electrónico según formato SIFEN v150.

        Estructura XML generada:
        <rDE xmlns="http://ekuatia.set.gov.py/sifen/xsd">
            <DE Id="{CDC}">
                <dVerFor>150</dVerFor>                    ← Versión del formato

                <gTimb>                                   ← A. Identificación del DE
                    <iTiDE>1</iTiDE>                      ← Tipo de documento
                    <dNumTim>12345678</dNumTim>           ← Número de timbrado
                    <dEst>001</dEst>                      ← Establecimiento
                    <dPunExp>001</dPunExp>                ← Punto de expedición
                    <dNumDoc>0000001</dNumDoc>            ← Número de documento
                    ...
                </gTimb>

                <gDatGralOpe>                             ← B. Datos generales
                    <dFeEmiDE>2024-05-04</dFeEmiDE>       ← Fecha de emisión
                    <gOpeCom>...</gOpeCom>                ← Operación comercial
                    <gEmis>...</gEmis>                    ← Emisor
                    <gDatRec>...</gDatRec>                ← Receptor
                </gDatGralOpe>

                <gDtipDE>                                 ← E. Datos por tipo de DE
                    <gCamItem>...</gCamItem>              ← Ítems (repetible)
                    <gCamItem>...</gCamItem>
                </gDtipDE>

                <gTotSub>                                 ← F. Totales y subtotales
                    <dSubExe>0</dSubExe>                  ← Subtotal exento
                    <dSubExo>0</dSubExo>                  ← Subtotal exonerado
                    <dSub5>0</dSub5>                      ← Subtotal IVA 5%
                    <dSub10>0</dSub10>                    ← Subtotal IVA 10%
                    <dTotOpe>1000000</dTotOpe>            ← Total operación
                    ...
                </gTotSub>

                <gCamCond>                                ← E600. Condición de operación
                    <iCondOpe>1</iCondOpe>                ← Tipo: contado/crédito
                    <gPaConEIni>...</gPaConEIni>          ← Pagos (si contado)
                    <gPagCred>...</gPagCred>              ← Cuotas (si crédito)
                </gCamCond>
            </DE>
        </rDE>

        Returns:
            Elemento raíz del XML generado.
        """
        # ========================================
        # RAÍZ: rDE (Representación Electrónica)
        # ========================================
        root = etree.Element(f"{{{NS}}}rDE", nsmap=NSMAP)

        root.set(
            f"{{{XSI_NS}}}schemaLocation",
            "https://ekuatia.set.gov.py/sifen/xsd siRecepDE_v150.xsd",
        )

        # ========================================
        # dVerFor: Versión del formato (150) - ANTES del DE
        # ========================================
        self._add_element(root, "dVerFor", self.documento.dVerFor)

        # ========================================
        # DE: Documento Electrónico
        # ========================================
        de_elem = etree.SubElement(root, f"{{{NS}}}DE")
        # El Id debe ser el CDC completo de 44 dígitos
        de_elem.set(
            "Id",
            (
                self.documento.CDC
                if hasattr(self.documento, "CDC") and self.documento.CDC
                else self.documento.Id
            ),
        )

        # ========================================
        # dDVId: Dígito verificador del CDC (campo obligatorio)
        # ========================================
        dv_cdc = (
            self.documento._calculate_dv(self.documento.CDC[:-1])
            if hasattr(self.documento, "CDC") and self.documento.CDC
            else 0
        )
        self._add_element(de_elem, "dDVId", dv_cdc)

        # ========================================
        # dFecFirma: Fecha y hora de firma (campo obligatorio)
        # ========================================
        from datetime import datetime

        fecha_firma = datetime.now()
        self._add_element(de_elem, "dFecFirma", self._format_datetime(fecha_firma))

        # ========================================
        # dSisFact: Sistema de facturación (campo obligatorio)
        # 1 = Sistema de facturación del contribuyente
        # 2 = SIFEN solución gratuita
        # ========================================
        self._add_element(de_elem, "dSisFact", 1)

        # ========================================
        # gOpeDE: Grupo de operación del DE (campo obligatorio)
        # ========================================
        self._generate_operacion_de(de_elem)

        # ========================================
        # A. IDENTIFICACIÓN DEL DE (gTimb)
        # Campos del timbrado y numeración
        # ========================================
        self._generate_identificacion(de_elem)

        # ========================================
        # B. DATOS GENERALES DE LA OPERACIÓN (gDatGralOpe)
        # Fecha, emisor, receptor, operación comercial
        # ========================================
        self._generate_datos_generales(de_elem)

        # ========================================
        # E. DATOS POR TIPO DE DE (gDtipDE)
        # Ítems de la factura/documento
        # ========================================
        dtip_elem = etree.SubElement(de_elem, f"{{{NS}}}gDtipDE")

        # E605. CAMPOS ESPECÍFICOS POR TIPO DE DE
        # Para Factura Electrónica (iTiDE=1), agregar gCamFE
        if self.documento.gTimb.iTiDE == 1:
            self._generate_campos_fe(dtip_elem)

        # E600. CONDICIÓN DE LA OPERACIÓN (gCamCond) - Debe ir ANTES de los ítems
        # Contado o crédito, formas de pago
        self._generate_condicion(dtip_elem)

        # E700-E799: Ítems (gCamItem) - Repetible
        for item in self.documento.gCamItem:
            self._generate_item(dtip_elem, item)

        # ========================================
        # F. TOTALES Y SUBTOTALES (gTotSub)
        # Cálculo de totales por tasa de IVA
        # ========================================
        self._generate_totales(de_elem)

        # ========================================
        # G. CAMPOS FUERA DEL DE - gCamFuFD
        # Código QR y otros campos de firma fiscal digital
        # NOTA: gCamFuFD debe ir DESPUÉS de Signature según XSD
        # La firma se insertará antes de este elemento al firmar
        # ========================================
        self._generate_campos_fuera_de(root)

        return root

    def _generate_operacion_de(self, parent: etree.Element):
        """
        Genera el grupo gOpeDE - Operación del DE (campo obligatorio según XSD).

        Estructura:
        <gOpeDE>
            <iTipEmi>1</iTipEmi>                  ← Tipo de emisión
            <dDesTipEmi>Normal</dDesTipEmi>       ← Descripción
            <dCodSeg>123456789</dCodSeg>          ← Código de seguridad
            <dInfoEmi>...</dInfoEmi>              ← Info emisor (opcional)
            <dInfoFisc>...</dInfoFisc>            ← Info fisco (opcional)
        </gOpeDE>
        """
        gDatGralOpe = self.documento.gDatGralOpe

        ope_de_elem = etree.SubElement(parent, f"{{{NS}}}gOpeDE")

        self._add_element(ope_de_elem, "iTipEmi", gDatGralOpe.iTipEmi)
        if gDatGralOpe.dDesTipEmi:
            self._add_element(ope_de_elem, "dDesTipEmi", gDatGralOpe.dDesTipEmi)
        self._add_element(ope_de_elem, "dCodSeg", gDatGralOpe.dCodSeg)
        if gDatGralOpe.dInfoEmi:
            self._add_element(ope_de_elem, "dInfoEmi", gDatGralOpe.dInfoEmi)
        if gDatGralOpe.dInfoFisc:
            self._add_element(ope_de_elem, "dInfoFisc", gDatGralOpe.dInfoFisc)

    def _generate_identificacion(self, parent: etree.Element):
        """
        Genera el grupo A - Identificación del DE (gTimb).

        Estructura:
        <gTimb>
            <iTiDE>1</iTiDE>                          ← Tipo de documento (1=Factura)
            <dDesTiDE>Factura electrónica</dDesTiDE>  ← Descripción tipo
            <dNumTim>12345678</dNumTim>               ← Número de timbrado
            <dEst>001</dEst>                          ← Establecimiento
            <dPunExp>001</dPunExp>                    ← Punto de expedición
            <dNumDoc>0000001</dNumDoc>                ← Número de documento
            <dSerieNum>A001</dSerieNum>               ← Serie (opcional)
            <dFeIniT>2024-01-01T00:00:00</dFeIniT>    ← Fecha inicio timbrado
        </gTimb>
        """
        gTimb = self.documento.gTimb

        timb_elem = etree.SubElement(parent, f"{{{NS}}}gTimb")

        self._add_element(timb_elem, "iTiDE", gTimb.iTiDE)
        if gTimb.dDesTiDE:
            self._add_element(timb_elem, "dDesTiDE", gTimb.dDesTiDE)
        self._add_element(timb_elem, "dNumTim", gTimb.dNumTim)
        self._add_element(timb_elem, "dEst", gTimb.dEst)
        self._add_element(timb_elem, "dPunExp", gTimb.dPunExp)
        self._add_element(timb_elem, "dNumDoc", gTimb.dNumDoc)
        if gTimb.dSerieNum:
            self._add_element(timb_elem, "dSerieNum", gTimb.dSerieNum)
        # dFeIniT debe ser solo fecha YYYY-MM-DD según XSD
        self._add_element(timb_elem, "dFeIniT", self._format_date(gTimb.dFeIniT))

    def _generate_datos_generales(self, parent: etree.Element):
        """
        Genera el grupo B - Datos generales de la operación (gDatGralOpe).

        Estructura:
        <gDatGralOpe>
            <dFeEmiDE>2024-05-04</dFeEmiDE>           ← Fecha de emisión

            <gOpeCom>                                 ← Operación comercial
                <iTipTra>1</iTipTra>                  ← Tipo de transacción
                <iTImp>1</iTImp>                      ← Tipo de impuesto
                <cMoneOpe>PYG</cMoneOpe>              ← Moneda
                ...
            </gOpeCom>

            <gEmis>                                   ← Datos del emisor
                <dRucEm>80012345-6</dRucEm>           ← RUC emisor
                <dNomEmi>Empresa SA</dNomEmi>         ← Nombre emisor
                <dDirEmi>Av. Principal 123</dDirEmi>  ← Dirección
                ...
            </gEmis>

            <gDatRec>                                 ← Datos del receptor
                <iNatRec>1</iNatRec>                  ← Naturaleza receptor
                <iTiOpe>1</iTiOpe>                    ← Tipo de operación
                <dNomRec>Cliente SRL</dNomRec>        ← Nombre receptor
                ...
            </gDatRec>
        </gDatGralOpe>
        """
        gDatGralOpe = self.documento.gDatGralOpe

        dat_elem = etree.SubElement(parent, f"{{{NS}}}gDatGralOpe")

        # dFeEmiDE debe ser datetime YYYY-MM-DDTHH:MM:SS
        self._add_element(
            dat_elem, "dFeEmiDE", self._format_datetime(gDatGralOpe.dFeEmiDE)
        )

        # gOpeCom - Operación Comercial (obligatorio)
        self._generate_operacion_comercial(dat_elem)

        # gEmis - Emisor
        self._generate_emisor(dat_elem)

        # gDatRec - Receptor
        self._generate_receptor(dat_elem)

    def _generate_operacion_comercial(self, parent: etree.Element):
        """
        Genera el grupo gOpeCom - Operación Comercial.

        Estructura:
        <gOpeCom>
            <iTipTra>1</iTipTra>           ← Tipo de transacción
            <dDesTipTra>...</dDesTipTra>   ← Descripción (opcional)
            <iTImp>1</iTImp>               ← Tipo de impuesto
            <dDesTImp>IVA</dDesTImp>       ← Descripción (opcional)
            <cMoneOpe>PYG</cMoneOpe>       ← Moneda de la operación
            <dDesMoneOpe>Guarani</dDesMoneOpe>  ← Descripción (opcional)
        </gOpeCom>
        """
        gDatGralOpe = self.documento.gDatGralOpe

        ope_elem = etree.SubElement(parent, f"{{{NS}}}gOpeCom")

        # iTipTra - Tipo de transacción (obligatorio)
        self._add_element(ope_elem, "iTipTra", gDatGralOpe.iTipTra)
        if gDatGralOpe.dDesTipTra:
            self._add_element(ope_elem, "dDesTipTra", gDatGralOpe.dDesTipTra)

        # iTImp - Tipo de impuesto (obligatorio)
        self._add_element(ope_elem, "iTImp", gDatGralOpe.iTImp)
        if gDatGralOpe.dDesTImp:
            self._add_element(ope_elem, "dDesTImp", gDatGralOpe.dDesTImp)

        # cMoneOpe - Moneda de la operación (obligatorio)
        self._add_element(ope_elem, "cMoneOpe", gDatGralOpe.cMoneOpe)
        if gDatGralOpe.dDesMoneOpe:
            self._add_element(ope_elem, "dDesMoneOpe", gDatGralOpe.dDesMoneOpe)

    def _generate_emisor(self, parent: etree.Element):
        """Genera el grupo D - Emisor (gEmis)."""
        gEmis = self.documento.gEmis

        emis_elem = etree.SubElement(parent, f"{{{NS}}}gEmis")

        # El RUC debe ir sin guión ni DV según especificación SIFEN
        # Extraer solo la parte antes del guión
        ruc_sin_dv = gEmis.dRucEm.split("-")[0] if "-" in gEmis.dRucEm else gEmis.dRucEm
        self._add_element(emis_elem, "dRucEm", ruc_sin_dv)
        self._add_element(emis_elem, "dDVEmi", gEmis.dDVEmi)
        self._add_element(emis_elem, "iTipCont", gEmis.iTipCont)
        if gEmis.dDesTipCont:
            self._add_element(emis_elem, "dDesTipCont", gEmis.dDesTipCont)
        if gEmis.cTipReg:
            self._add_element(emis_elem, "cTipReg", gEmis.cTipReg)
        if gEmis.dDesTipReg:
            self._add_element(emis_elem, "dDesTipReg", gEmis.dDesTipReg)
        self._add_element(emis_elem, "dNomEmi", gEmis.dNomEmi)
        if gEmis.dNomFanEmi:
            self._add_element(emis_elem, "dNomFanEmi", gEmis.dNomFanEmi)
        self._add_element(emis_elem, "dDirEmi", gEmis.dDirEmi)
        # dNumCas es obligatorio según XSD
        self._add_element(emis_elem, "dNumCas", gEmis.dNumCas if gEmis.dNumCas else 0)
        if gEmis.dCompDir1:
            self._add_element(emis_elem, "dCompDir1", gEmis.dCompDir1)
        if gEmis.dCompDir2:
            self._add_element(emis_elem, "dCompDir2", gEmis.dCompDir2)
        self._add_element(emis_elem, "cDepEmi", gEmis.cDepEmi)
        # dDesDepEmi es obligatorio según XSD
        self._add_element(
            emis_elem, "dDesDepEmi", gEmis.dDesDepEmi if gEmis.dDesDepEmi else "CAPITAL"
        )
        if gEmis.cDisEmi:
            self._add_element(emis_elem, "cDisEmi", gEmis.cDisEmi)
        if gEmis.dDesDisEmi:
            self._add_element(emis_elem, "dDesDisEmi", gEmis.dDesDisEmi)
        self._add_element(emis_elem, "cCiuEmi", gEmis.cCiuEmi)
        # dDesCiuEmi es obligatorio según XSD
        self._add_element(
            emis_elem,
            "dDesCiuEmi",
            gEmis.dDesCiuEmi if gEmis.dDesCiuEmi else "ASUNCION",
        )
        self._add_element(emis_elem, "dTelEmi", gEmis.dTelEmi)
        self._add_element(emis_elem, "dEmailE", gEmis.dEmailE)
        if gEmis.dDenSuc:
            self._add_element(emis_elem, "dDenSuc", gEmis.dDenSuc)

        # Actividades económicas
        for act_eco in gEmis.gActEco:
            act_elem = etree.SubElement(emis_elem, f"{{{NS}}}gActEco")
            self._add_element(act_elem, "cActEco", act_eco.cActEco)
            self._add_element(act_elem, "dDesActEco", act_eco.dDesActEco)

        # Responsable del DE (opcional)
        if gEmis.gRespDE:
            resp_elem = etree.SubElement(emis_elem, f"{{{NS}}}gRespDE")
            self._add_element(resp_elem, "iTipIDRespDE", gEmis.gRespDE.iTipIDRespDE)
            if gEmis.gRespDE.dDTipIDRespDE:
                self._add_element(
                    resp_elem, "dDTipIDRespDE", gEmis.gRespDE.dDTipIDRespDE
                )
            self._add_element(resp_elem, "dNumIDRespDE", gEmis.gRespDE.dNumIDRespDE)
            self._add_element(resp_elem, "dNomRespDE", gEmis.gRespDE.dNomRespDE)
            if gEmis.gRespDE.dCarRespDE:
                self._add_element(resp_elem, "dCarRespDE", gEmis.gRespDE.dCarRespDE)

    def _generate_receptor(self, parent: etree.Element):
        """Genera el grupo E - Receptor (gDatRec)."""
        gDatRec = self.documento.gDatRec

        rec_elem = etree.SubElement(parent, f"{{{NS}}}gDatRec")

        self._add_element(rec_elem, "iNatRec", gDatRec.iNatRec)
        if gDatRec.dDesNatRec:
            self._add_element(rec_elem, "dDesNatRec", gDatRec.dDesNatRec)
        self._add_element(rec_elem, "iTiOpe", gDatRec.iTiOpe)
        if gDatRec.dDesTiOpe:
            self._add_element(rec_elem, "dDesTiOpe", gDatRec.dDesTiOpe)
        # cPaisRec es obligatorio según validador
        self._add_element(
            rec_elem, "cPaisRec", gDatRec.cPaisRec if gDatRec.cPaisRec else "PRY"
        )
        # dDesPaisRe es obligatorio según validador
        self._add_element(
            rec_elem,
            "dDesPaisRe",
            gDatRec.dDesPaisRe if gDatRec.dDesPaisRe else "Paraguay",
        )
        if gDatRec.iTiContRec:
            self._add_element(rec_elem, "iTiContRec", gDatRec.iTiContRec)
        if gDatRec.dDesTiContRec:
            self._add_element(rec_elem, "dDesTiContRec", gDatRec.dDesTiContRec)
        if gDatRec.dRucRec:
            self._add_element(rec_elem, "dRucRec", gDatRec.dRucRec)
        if gDatRec.dDVRec:
            self._add_element(rec_elem, "dDVRec", gDatRec.dDVRec)
        if gDatRec.dNumIDRec:
            self._add_element(rec_elem, "dNumIDRec", gDatRec.dNumIDRec)
        self._add_element(rec_elem, "dNomRec", gDatRec.dNomRec)
        if gDatRec.dNomFanRec:
            self._add_element(rec_elem, "dNomFanRec", gDatRec.dNomFanRec)
        if gDatRec.dDirRec:
            self._add_element(rec_elem, "dDirRec", gDatRec.dDirRec)
        if gDatRec.dNumCasRec:
            self._add_element(rec_elem, "dNumCasRec", gDatRec.dNumCasRec)
        if gDatRec.cDepRec:
            self._add_element(rec_elem, "cDepRec", gDatRec.cDepRec)
        if gDatRec.dDesDepRec:
            self._add_element(rec_elem, "dDesDepRec", gDatRec.dDesDepRec)
        if gDatRec.cDisRec:
            self._add_element(rec_elem, "cDisRec", gDatRec.cDisRec)
        if gDatRec.dDesDisRec:
            self._add_element(rec_elem, "dDesDisRec", gDatRec.dDesDisRec)
        if gDatRec.cCiuRec:
            self._add_element(rec_elem, "cCiuRec", gDatRec.cCiuRec)
        if gDatRec.dDesCiuRec:
            self._add_element(rec_elem, "dDesCiuRec", gDatRec.dDesCiuRec)
        if gDatRec.dTelRec:
            self._add_element(rec_elem, "dTelRec", gDatRec.dTelRec)
        if gDatRec.dEmailRec:
            self._add_element(rec_elem, "dEmailRec", gDatRec.dEmailRec)
        if gDatRec.dCodCliente:
            self._add_element(rec_elem, "dCodCliente", gDatRec.dCodCliente)

    def _add_element(self, parent: etree.Element, tag: str, value: any):
        if value is None:
            return
        elem = etree.SubElement(parent, tag)
        elem.text = str(value)

    def _format_datetime(self, dt: datetime) -> str:
        """
        Formatea datetime para XML.

        Args:
            dt: Datetime a formatear.

        Returns:
            String en formato ISO 8601.
        """
        return dt.strftime("%Y-%m-%dT%H:%M:%S")

    def _format_date(self, d: date) -> str:
        """
        Formatea date para XML.

        Args:
            d: Date a formatear.

        Returns:
            String en formato YYYY-MM-DD.
        """
        return d.strftime("%Y-%m-%d")

    def _format_decimal(self, value: Decimal, decimals: int = 2) -> str:
        """
        Formatea Decimal para XML.

        Args:
            value: Valor decimal.
            decimals: Número de decimales.

        Returns:
            String formateado.
        """
        return f"{value:.{decimals}f}"

    def _format_amount(self, value: Decimal) -> str:
        """Formatea monto monetario con 8 decimales (tMontoBase)."""
        return self._format_decimal(value, 8)

    def _format_pago(self, value: Decimal) -> str:
        """Formatea monto de pago: entero para PYG (tMontoBase4, xmlok.xml usa integer)."""
        from decimal import ROUND_HALF_UP

        moneda = getattr(self.documento.gTotSub, "cMoneOpe", "PYG")
        if moneda == "PYG":
            return str(int(value.to_integral_value(rounding=ROUND_HALF_UP)))
        return self._format_decimal(value, 4)

    def _format_compact(self, value: Decimal) -> str:
        """Formatea sin ceros decimales innecesarios: 100.00 -> 100, 50.50 -> 50.5"""
        if value == value.to_integral_value():
            return str(int(value.to_integral_value()))
        return str(value.normalize())

    def _generate_item(self, parent: etree.Element, item):
        """Genera un ítem (gCamItem)."""
        item_elem = etree.SubElement(parent, f"{{{NS}}}gCamItem")

        self._add_element(item_elem, "dCodInt", item.dCodInt)
        if item.dParAranc:
            self._add_element(item_elem, "dParAranc", item.dParAranc)
        if item.dNCM:
            self._add_element(item_elem, "dNCM", item.dNCM)
        self._add_element(item_elem, "dDesProSer", item.dDesProSer)
        self._add_element(item_elem, "cUniMed", item.cUniMed)
        # dDesUniMed es obligatorio según validador
        self._add_element(
            item_elem, "dDesUniMed", item.dDesUniMed if item.dDesUniMed else "UNI"
        )
        self._add_element(
            item_elem, "dCantProSer", self._format_decimal(item.dCantProSer, 4)
        )

        # gValorItem
        self._generate_valor_item(item_elem, item.gValorItem)

    def _generate_valor_item(self, parent: etree.Element, valor_item):
        """Genera valores del ítem (gValorItem)."""
        valor_elem = etree.SubElement(parent, f"{{{NS}}}gValorItem")

        # Precio unitario
        self._add_element(
            valor_elem, "dPUniProSer", self._format_amount(valor_item.dPUniProSer)
        )

        # Tipo de cambio (opcional, solo para moneda extranjera)
        if hasattr(valor_item, "dTiCamIt") and valor_item.dTiCamIt:
            self._add_element(
                valor_elem, "dTiCamIt", self._format_decimal(valor_item.dTiCamIt, 4)
            )

        # Total bruto (antes de descuentos)
        total_bruto = (
            valor_item.dTotOpeItem
            if not hasattr(valor_item, "dTotBruOpeItem")
            else valor_item.dTotBruOpeItem
        )
        self._add_element(
            valor_elem, "dTotBruOpeItem", self._format_amount(total_bruto)
        )

        # gValorRestaItem - Valores después de descuentos
        resta_elem = etree.SubElement(valor_elem, f"{{{NS}}}gValorRestaItem")

        desc_item = (
            valor_item.dDescItem if valor_item.dDescItem is not None else Decimal("0")
        )
        self._add_element(resta_elem, "dDescItem", self._format_amount(desc_item))

        porc_des_it = (
            valor_item.dPorcDesIt if valor_item.dPorcDesIt is not None else Decimal("0")
        )
        if porc_des_it > 0:
            self._add_element(
                resta_elem, "dPorcDesIt", self._format_decimal(porc_des_it, 8)
            )

        desc_glo_item = (
            valor_item.dDescGloItem
            if valor_item.dDescGloItem is not None
            else Decimal("0")
        )
        if desc_glo_item > 0:
            self._add_element(
                resta_elem, "dDescGloItem", self._format_amount(desc_glo_item)
            )

        # Total operación del ítem
        self._add_element(
            resta_elem, "dTotOpeItem", self._format_amount(valor_item.dTotOpeItem)
        )

        # gCamIVA - Fuera de gValorItem, directamente en gCamItem
        if valor_item.gCamIVA:
            self._generate_iva_item(parent, valor_item.gCamIVA)

    def _generate_iva_item(self, parent: etree.Element, iva_item):
        """Genera IVA del ítem (gCamIVA)."""
        iva_elem = etree.SubElement(parent, f"{{{NS}}}gCamIVA")

        self._add_element(iva_elem, "iAfecIVA", iva_item.iAfecIVA)
        if iva_item.dDesAfecIVA:
            self._add_element(iva_elem, "dDesAfecIVA", iva_item.dDesAfecIVA)
        self._add_element(iva_elem, "dPropIVA", self._format_compact(iva_item.dPropIVA))
        self._add_element(iva_elem, "dTasaIVA", int(iva_item.dTasaIVA))
        self._add_element(
            iva_elem, "dBasGravIVA", self._format_amount(iva_item.dBasGravIVA)
        )
        self._add_element(
            iva_elem, "dLiqIVAItem", self._format_amount(iva_item.dLiqIVAItem)
        )
        base_exenta = getattr(iva_item, "dBasExe", Decimal("0"))
        # dBasExe: 0 como entero cuando es cero (igual que xmlok.xml)
        self._add_element(iva_elem, "dBasExe", self._format_compact(base_exenta))

    def _generate_totales(self, parent: etree.Element):
        """Genera totales (gTotSub)."""
        totales = self.documento.gTotSub

        tot_elem = etree.SubElement(parent, f"{{{NS}}}gTotSub")

        # Subtotales por tasa (en orden según XSD)
        if totales.dSubExe is not None:
            self._add_element(tot_elem, "dSubExe", self._format_amount(totales.dSubExe))
        if totales.dSubExo is not None and totales.dSubExo > 0:
            self._add_element(tot_elem, "dSubExo", self._format_amount(totales.dSubExo))
        if totales.dSub5 is not None:
            self._add_element(tot_elem, "dSub5", self._format_amount(totales.dSub5))
        if totales.dSub10:
            self._add_element(tot_elem, "dSub10", self._format_amount(totales.dSub10))

        self._add_element(tot_elem, "dTotOpe", self._format_amount(totales.dTotOpe))

        if totales.dTotDesc is not None:
            self._add_element(
                tot_elem, "dTotDesc", self._format_amount(totales.dTotDesc)
            )
        if totales.dTotDescGlotem is not None:
            self._add_element(
                tot_elem, "dTotDescGlotem", self._format_amount(totales.dTotDescGlotem)
            )
        if totales.dTotAntItem is not None:
            self._add_element(
                tot_elem, "dTotAntItem", self._format_compact(totales.dTotAntItem)
            )
        if totales.dTotAnt is not None:
            self._add_element(
                tot_elem, "dTotAnt", self._format_compact(totales.dTotAnt)
            )

        if totales.dPorcDescTotal is not None:
            self._add_element(
                tot_elem,
                "dPorcDescTotal",
                self._format_decimal(totales.dPorcDescTotal, 8),
            )

        if totales.dDescTotal is not None:
            self._add_element(
                tot_elem, "dDescTotal", self._format_amount(totales.dDescTotal)
            )
        if totales.dAnticipo is not None:
            self._add_element(
                tot_elem, "dAnticipo", self._format_compact(totales.dAnticipo)
            )
        if totales.dRedon is not None:
            self._add_element(
                tot_elem, "dRedon", self._format_decimal(totales.dRedon, 4)
            )

        self._add_element(
            tot_elem, "dTotGralOpe", self._format_amount(totales.dTotGralOpe)
        )

        if totales.dIVA5 is not None:
            self._add_element(tot_elem, "dIVA5", self._format_amount(totales.dIVA5))
        if totales.dIVA10:
            self._add_element(tot_elem, "dIVA10", self._format_amount(totales.dIVA10))

        self._add_element(tot_elem, "dTotIVA", self._format_amount(totales.dTotIVA))

        if totales.dBaseGrav5 is not None:
            self._add_element(
                tot_elem, "dBaseGrav5", self._format_amount(totales.dBaseGrav5)
            )
        if totales.dBaseGrav10:
            self._add_element(
                tot_elem, "dBaseGrav10", self._format_amount(totales.dBaseGrav10)
            )
        if totales.dTBasGraIVA:
            self._add_element(
                tot_elem, "dTBasGraIVA", self._format_amount(totales.dTBasGraIVA)
            )

        # dTotalGs: Total en Guaraníes (solo cuando la moneda NO es PYG)
        # Cuando la moneda es extranjera, aquí va la conversión a guaraníes
        if (
            totales.cMoneOpe != "PYG"
            and hasattr(totales, "dTotalGs")
            and totales.dTotalGs
        ):
            self._add_element(
                tot_elem, "dTotalGs", self._format_decimal(totales.dTotalGs, 2)
            )

    def _generate_campos_fe(self, parent: etree.Element):
        """
        Genera el grupo gCamFE - Campos específicos de Factura Electrónica.

        Estructura:
        <gCamFE>
            <iIndPres>1</iIndPres>           ← Indicador de presencia
            <dDesIndPres>...</dDesIndPres>   ← Descripción (opcional)
        </gCamFE>
        """
        fe_elem = etree.SubElement(parent, f"{{{NS}}}gCamFE")

        # iIndPres - Indicador de presencia (1=Presencial, 2=Electrónico, etc.)
        # Por defecto 1 (Operación presencial)
        ind_pres = getattr(self.documento, "iIndPres", 1)
        self._add_element(fe_elem, "iIndPres", ind_pres)

        # dDesIndPres - Descripción del indicador de presencia (obligatorio)
        desc_ind_pres = getattr(self.documento, "dDesIndPres", "Operación presencial")
        self._add_element(fe_elem, "dDesIndPres", desc_ind_pres)

    def _generate_condicion(self, parent: etree.Element):
        """Genera condición de operación (gCamCond)."""
        condicion = self.documento.gPaConEIni

        cond_elem = etree.SubElement(parent, f"{{{NS}}}gCamCond")

        self._add_element(cond_elem, "iCondOpe", condicion.iCondOpe)
        if condicion.dDesCondOpe:
            self._add_element(cond_elem, "dDCondOpe", condicion.dDesCondOpe)

        # Pagos
        if condicion.gPaConEIni:
            for pago in condicion.gPaConEIni:
                pago_elem = etree.SubElement(cond_elem, f"{{{NS}}}gPaConEIni")
                self._add_element(pago_elem, "iTiPago", pago.iTiPago)
                if pago.dDesTiPag:
                    self._add_element(pago_elem, "dDesTiPag", pago.dDesTiPag)
                # dMonTiPag es obligatorio
                monto_pago = pago.dMonTiPag if pago.dMonTiPag else Decimal("0")
                self._add_element(pago_elem, "dMonTiPag", self._format_pago(monto_pago))
                # cMoneTiPag: Moneda del pago (obligatorio, PYG por defecto)
                moneda_pago = getattr(pago, "cMoneTiPag", None) or "PYG"
                self._add_element(pago_elem, "cMoneTiPag", moneda_pago)
                # dDMoneTiPag: Descripción de la moneda (opcional)
                desc_moneda = getattr(pago, "dDMoneTiPag", None) or "guarani"
                self._add_element(pago_elem, "dDMoneTiPag", desc_moneda)

        # Cuotas
        if condicion.gCuotas:
            for cuota in condicion.gCuotas:
                cuota_elem = etree.SubElement(cond_elem, f"{{{NS}}}gCuotas")
                self._add_element(cuota_elem, "cMoneCuo", cuota.cMoneCuo)
                if cuota.dDMoneCuo:
                    self._add_element(cuota_elem, "dDMoneCuo", cuota.dDMoneCuo)
                self._add_element(
                    cuota_elem, "dMonCuota", self._format_pago(cuota.dMonCuota)
                )
                if cuota.dVencCuo:
                    self._add_element(cuota_elem, "dVencCuo", cuota.dVencCuo)

    def _generate_campos_fuera_de(self, parent: etree.Element):
        """
        Genera el grupo gCamFuFD - Campos fuera del DE (firma fiscal digital).

        Este grupo contiene el código QR y otros campos relacionados con la firma.
        """
        fufd_elem = etree.SubElement(parent, f"{{{NS}}}gCamFuFD")

        # dCarQR: Código QR (obligatorio)
        # Generar URL con todos los parámetros requeridos
        qr_url = self._generate_qr_url()
        self._add_element(fufd_elem, "dCarQR", qr_url)

    def _generate_qr_url(self) -> str:
        """
        Genera la URL del código QR con todos los parámetros requeridos.

        Returns:
            URL completa del QR
        """
        import hashlib
        from urllib.parse import quote

        # Parámetros base
        params = []
        params.append(f"nVersion=150")
        params.append(f"Id={self.documento.CDC}")

        # dFeEmiDE en hexadecimal
        fecha_emision_str = self.documento.gDatGralOpe.dFeEmiDE.strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        fecha_hex = fecha_emision_str.encode("utf-8").hex()
        params.append(f"dFeEmiDE={fecha_hex}")

        # dRucRec si el receptor es contribuyente, dNumIDRec si no lo es
        if (
            hasattr(self.documento.gDatRec, "dRucRec")
            and self.documento.gDatRec.dRucRec
        ):
            params.append(f"dRucRec={self.documento.gDatRec.dRucRec}")
        elif (
            hasattr(self.documento.gDatRec, "dNumIDRec")
            and self.documento.gDatRec.dNumIDRec
        ):
            params.append(f"dNumIDRec={self.documento.gDatRec.dNumIDRec}")

        # dTotGralOpe y dTotIVA: 8 decimales (formato requerido por SIFEN para validar cHashQR)
        params.append(
            f"dTotGralOpe={self._format_decimal(self.documento.gTotSub.dTotGralOpe, 8)}"
        )
        params.append(
            f"dTotIVA={self._format_decimal(self.documento.gTotSub.dTotIVA, 8)}"
        )

        # cItems (cantidad de ítems)
        num_items = len(self.documento.gCamItem)
        params.append(f"cItems={num_items}")

        # NOTA: DigestValue, IdCSC y cHashQR se deben agregar después de firmar
        # Por ahora generamos el QR sin estos parámetros para evitar errores de validación

        # Construir URL (ambiente-aware)
        from sifen.config import TipoAmbiente

        if self.ambiente is not None and self.ambiente == TipoAmbiente.PROD:
            base_url = "https://ekuatia.set.gov.py/consultas/qr"
        else:
            base_url = "https://ekuatia.set.gov.py/consultas-test/qr"
        qr_url = f"{base_url}?{'&'.join(params)}"

        return qr_url


def generate_xml(documento: DocumentoElectronico, ambiente=None) -> str:
    """
    Genera XML a partir de un DocumentoElectronico.

    Args:
        documento: Documento a convertir.
        ambiente: TipoAmbiente para la URL del QR.

    Returns:
        XML como string.
    """
    generator = XMLGenerator(documento, ambiente=ambiente)
    root = generator.generate()

    # Generar XML con declaración
    xml_bytes = etree.tostring(
        root, encoding="UTF-8", pretty_print=True, xml_declaration=True
    )
    return xml_bytes.decode("UTF-8")


def generate_xml_element(documento: DocumentoElectronico) -> etree.Element:
    """
    Genera elemento XML a partir de un DocumentoElectronico.

    Args:
        documento: Documento a convertir.

    Returns:
        Elemento XML.
    """
    generator = XMLGenerator(documento)
    return generator.generate()
