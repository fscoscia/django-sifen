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

        # E4. CAMPOS DE AUTOFACTURA ELECTRÓNICA (gCamAE)
        # Para AFE (iTiDE=4)
        if (
            self.documento.gTimb.iTiDE == 4
            and hasattr(self.documento, "gCamAE")
            and self.documento.gCamAE
        ):
            self._generate_campos_autofactura(dtip_elem)

        # E5. CAMPOS DE NOTA DE CRÉDITO/DÉBITO (gCamNCDE)
        # Para NCE (iTiDE=5) o NDE (iTiDE=6)
        if self.documento.gTimb.iTiDE in [5, 6] and self.documento.gCamNCDE:
            self._generate_campos_ncde(dtip_elem)

        # E6. CAMPOS DE NOTA DE REMISIÓN ELECTRÓNICA (gCamNRE)
        # Para NRE (iTiDE=7)
        if self.documento.gTimb.iTiDE == 7 and self.documento.gCamNRE:
            self._generate_campos_nre(dtip_elem)

        # E600. CONDICIÓN DE LA OPERACIÓN (gCamCond)
        # Contado o crédito, formas de pago (no requerido para NCE/NDE)
        if self.documento.gPaConEIni:
            self._generate_condicion(dtip_elem)

        # E700-E799: Ítems (gCamItem) - Repetible
        for item in self.documento.gCamItem:
            self._generate_item(dtip_elem, item)

        # E10. CAMPOS QUE DESCRIBEN EL TRANSPORTE (gTransp)
        # Obligatorio para NRE (iTiDE=7) - Debe ir después de los ítems
        if self.documento.gTimb.iTiDE == 7 and self.documento.gTransp:
            self._generate_transporte(dtip_elem)

        # ========================================
        # F. TOTALES Y SUBTOTALES (gTotSub)
        # Cálculo de totales por tasa de IVA
        # NO incluir para iTiDE=7 (Nota de Remisión)
        # ========================================
        if self.documento.gTimb.iTiDE != 7:
            self._generate_totales(de_elem)

        # ========================================
        # H. CAMPOS QUE IDENTIFICAN AL DOCUMENTO ASOCIADO (gCamDEAsoc)
        # Obligatorio si iTiDE = 4, 5, 6 (Autofactura, NCE, NDE)
        # Debe ir FUERA de gDtipDE, después de gTotSub según XSD
        # ========================================
        if self.documento.gTimb.iTiDE in [4, 5, 6] and self.documento.gCamDEAsoc:
            self._generate_documento_asociado(de_elem)

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

        # gOpeCom - Operación Comercial (NO incluir para iTiDE=7 - Nota de Remisión)
        if self.documento.gTimb.iTiDE != 7:
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
        # D208 / D209: Tipo de documento de identidad del receptor
        # Obligatorio si iNatRec = 2 y iTiOpe != 4 (según manual)
        i_nat_rec = getattr(gDatRec, "iNatRec", None)
        i_ti_ope = getattr(gDatRec, "iTiOpe", None)
        
        if i_nat_rec == 2 and i_ti_ope != 4:
            i_tip_id = getattr(gDatRec, "iTipIDRec", None)
            d_dtip_id = getattr(gDatRec, "dDTipIDRec", None)
        
            if i_tip_id is not None:
                self._add_element(rec_elem, "iTipIDRec", i_tip_id)
            if d_dtip_id:
                self._add_element(rec_elem, "dDTipIDRec", d_dtip_id)
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

        # gValorItem (no incluir para nota de remisión iTiDE=7)
        if item.gValorItem is not None:
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

    def _generate_campos_autofactura(self, parent: etree.Element):
        """
        Genera el grupo gCamAE - Campos de Autofactura Electrónica.

        Estructura:
        <gCamAE>
            <iNatVen>1</iNatVen>              ← Naturaleza del vendedor
            <dDesNatVen>...</dDesNatVen>      ← Descripción
            <iTipIDVen>1</iTipIDVen>          ← Tipo de documento
            <dDTipIDVen>...</dDTipIDVen>      ← Descripción tipo doc
            <dNumIDVen>...</dNumIDVen>        ← Número de documento
            <dNomVen>...</dNomVen>            ← Nombre del vendedor
            <dDirVen>...</dDirVen>            ← Dirección del vendedor
            ... (campos opcionales de ubicación)
            <dDirProv>...</dDirProv>          ← Lugar de la transacción
            ... (campos opcionales de ubicación de transacción)
        </gCamAE>
        """
        ae_elem = etree.SubElement(parent, f"{{{NS}}}gCamAE")

        ae = self.documento.gCamAE

        # E301 - Naturaleza del vendedor
        self._add_element(ae_elem, "iNatVen", ae.iNatVen)

        # E302 - Descripción de la naturaleza del vendedor
        self._add_element(ae_elem, "dDesNatVen", ae.dDesNatVen)

        # E304 - Tipo de documento de identidad del vendedor
        self._add_element(ae_elem, "iTipIDVen", ae.iTipIDVen)

        # E305 - Descripción del tipo de documento
        self._add_element(ae_elem, "dDTipIDVen", ae.dDTipIDVen)

        # E306 - Número de documento de identidad
        self._add_element(ae_elem, "dNumIDVen", ae.dNumIDVen)

        # E307 - Nombre y apellido del vendedor
        self._add_element(ae_elem, "dNomVen", ae.dNomVen)

        # E308 - Dirección del vendedor
        self._add_element(ae_elem, "dDirVen", ae.dDirVen)

        # E309 - Número de casa del vendedor (opcional)
        if ae.dNumCasVen is not None:
            self._add_element(ae_elem, "dNumCasVen", ae.dNumCasVen)

        # E310 - Código del departamento del vendedor (opcional)
        if ae.cDepVen is not None:
            self._add_element(ae_elem, "cDepVen", ae.cDepVen)

        # E311 - Descripción del departamento del vendedor (opcional)
        if ae.dDesDepVen is not None:
            self._add_element(ae_elem, "dDesDepVen", ae.dDesDepVen)

        # E312 - Código del distrito del vendedor (opcional)
        if ae.cDisVen is not None:
            self._add_element(ae_elem, "cDisVen", ae.cDisVen)

        # E313 - Descripción del distrito del vendedor (opcional)
        if ae.dDesDisVen is not None:
            self._add_element(ae_elem, "dDesDisVen", ae.dDesDisVen)

        # E314 - Código de la ciudad del vendedor (opcional)
        if ae.cCiuVen is not None:
            self._add_element(ae_elem, "cCiuVen", ae.cCiuVen)

        # E315 - Descripción de la ciudad del vendedor (opcional)
        if ae.dDesCiuVen is not None:
            self._add_element(ae_elem, "dDesCiuVen", ae.dDesCiuVen)

        # E316 - Lugar de la transacción (dirección donde se provee el servicio/producto)
        self._add_element(ae_elem, "dDirProv", ae.dDirProv)

        # E317 - Código del departamento donde se realiza la transacción (opcional)
        if ae.cDepProv is not None:
            self._add_element(ae_elem, "cDepProv", ae.cDepProv)

        # E318 - Descripción del departamento de transacción (opcional)
        if ae.dDesDepProv is not None:
            self._add_element(ae_elem, "dDesDepProv", ae.dDesDepProv)

        # E319 - Código del distrito de transacción (opcional)
        if ae.cDisProv is not None:
            self._add_element(ae_elem, "cDisProv", ae.cDisProv)

        # E320 - Descripción del distrito de transacción (opcional)
        if ae.dDesDisProv is not None:
            self._add_element(ae_elem, "dDesDisProv", ae.dDesDisProv)

        # E321 - Código de la ciudad de transacción (opcional)
        if ae.cCiuProv is not None:
            self._add_element(ae_elem, "cCiuProv", ae.cCiuProv)

        # E322 - Descripción de la ciudad de transacción (opcional)
        if ae.dDesCiuProv is not None:
            self._add_element(ae_elem, "dDesCiuProv", ae.dDesCiuProv)

    def _generate_campos_ncde(self, parent: etree.Element):
        """
        Genera el grupo gCamNCDE - Campos de Nota de Crédito/Débito Electrónica.

        Estructura:
        <gCamNCDE>
            <iMotEmi>1</iMotEmi>              ← Motivo de emisión
            <dDesMotEmi>...</dDesMotEmi>      ← Descripción del motivo
        </gCamNCDE>
        """
        ncde_elem = etree.SubElement(parent, f"{{{NS}}}gCamNCDE")

        ncde = self.documento.gCamNCDE

        # E401 - Motivo de emisión
        self._add_element(ncde_elem, "iMotEmi", ncde.iMotEmi)

        # E402 - Descripción del motivo
        self._add_element(ncde_elem, "dDesMotEmi", ncde.dDesMotEmi)

    def _generate_campos_nre(self, parent: etree.Element):
        """
        Genera el grupo gCamNRE - Campos de Nota de Remisión Electrónica.

        Estructura:
        <gCamNRE>
            <iMotEmiNR>1</iMotEmiNR>              ← Motivo de emisión
            <dDesMotEmiNR>...</dDesMotEmiNR>      ← Descripción del motivo
            <iRespEmiNR>1</iRespEmiNR>            ← Responsable de la emisión
            <dDesRespEmiNR>...</dDesRespEmiNR>    ← Descripción del responsable
            <dKmR>150</dKmR>                      ← Kilómetros estimados (opcional)
            <dFecEm>2026-06-15</dFecEm>           ← Fecha futura de emisión (opcional)
        </gCamNRE>
        """
        nre_elem = etree.SubElement(parent, f"{{{NS}}}gCamNRE")

        nre = self.documento.gCamNRE

        # E501 - Motivo de emisión
        self._add_element(nre_elem, "iMotEmiNR", nre.iMotEmiNR)

        # E502 - Descripción del motivo de emisión
        self._add_element(nre_elem, "dDesMotEmiNR", nre.dDesMotEmiNR)

        # E503 - Responsable de la emisión
        self._add_element(nre_elem, "iRespEmiNR", nre.iRespEmiNR)

        # E504 - Descripción del responsable
        self._add_element(nre_elem, "dDesRespEmiNR", nre.dDesRespEmiNR)

        # E505 - Kilómetros estimados de recorrido (opcional)
        if nre.dKmR is not None:
            self._add_element(nre_elem, "dKmR", nre.dKmR)

        # E506 - Fecha futura de emisión de la factura (opcional)
        if nre.dFecEm is not None:
            # Formato: AAAA-MM-DD
            self._add_element(nre_elem, "dFecEm", nre.dFecEm.strftime("%Y-%m-%d"))

    def _generate_transporte(self, parent: etree.Element):
        """
        Genera el grupo gTransp - Campos que describen el transporte de las mercaderías.

        Estructura:
        <gTransp>
            <iTipTrans>1</iTipTrans>              ← Tipo de transporte
            <dDesTipTrans>...</dDesTipTrans>      ← Descripción del tipo
            <iModTrans>1</iModTrans>              ← Modalidad del transporte
            <dDesModTrans>...</dDesModTrans>      ← Descripción de la modalidad
            <iRespFlete>1</iRespFlete>            ← Responsable del costo del flete
        </gTransp>
        """
        transp_elem = etree.SubElement(parent, f"{{{NS}}}gTransp")

        transp = self.documento.gTransp

        # E901 - Tipo de transporte
        self._add_element(transp_elem, "iTipTrans", transp.iTipTrans)

        # E902 - Descripción del tipo de transporte
        self._add_element(transp_elem, "dDesTipTrans", transp.dDesTipTrans)

        # E903 - Modalidad del transporte
        self._add_element(transp_elem, "iModTrans", transp.iModTrans)

        # E904 - Descripción de la modalidad del transporte
        self._add_element(transp_elem, "dDesModTrans", transp.dDesModTrans)

        # E905 - Responsable del costo del flete
        self._add_element(transp_elem, "iRespFlete", transp.iRespFlete)

        # E906 - Condición de la negociación (opcional)
        if transp.cCondNeg is not None:
            self._add_element(transp_elem, "cCondNeg", transp.cCondNeg)

        # E907 - Número de manifiesto (opcional)
        if transp.dNuManif is not None:
            self._add_element(transp_elem, "dNuManif", transp.dNuManif)

        # E908 - Número de despacho de importación (opcional)
        if transp.dNuDespImp is not None:
            self._add_element(transp_elem, "dNuDespImp", transp.dNuDespImp)

        # E909 - Fecha estimada de inicio de traslado (opcional)
        if transp.dIniTras is not None:
            self._add_element(
                transp_elem, "dIniTras", transp.dIniTras.strftime("%Y-%m-%d")
            )

        # E910 - Fecha estimada de fin de traslado (opcional)
        if transp.dFinTras is not None:
            self._add_element(
                transp_elem, "dFinTras", transp.dFinTras.strftime("%Y-%m-%d")
            )

        # E911 - Código del país de destino (opcional)
        if transp.cPaisDest is not None:
            self._add_element(transp_elem, "cPaisDest", transp.cPaisDest)

        # E912 - Descripción del país de destino (opcional)
        if transp.dDesPaisDest is not None:
            self._add_element(transp_elem, "dDesPaisDest", transp.dDesPaisDest)

        # E10.1 - Local de salida (gCamSal) - Obligatorio para iTiDE=7
        if transp.gCamSal is not None:
            self._generate_local_salida(transp_elem, transp.gCamSal)

        # E10.2 - Locales de entrega (gCamEnt) - Obligatorio para iTiDE=7, repetible
        for local_ent in transp.gCamEnt:
            self._generate_local_entrega(transp_elem, local_ent)

        # E10.3 - Vehículos de traslado (gVehTras) - Obligatorio para iTiDE=7, repetible hasta 4
        for vehiculo in transp.gVehTras:
            self._generate_vehiculo_traslado(transp_elem, vehiculo)

        # E10.4 - Transportista (gCamTrans) - Obligatorio para iTiDE=7
        if transp.gCamTrans is not None:
            self._generate_transportista(transp_elem, transp.gCamTrans)

    def _generate_local_salida(self, parent: etree.Element, local_sal):
        """Genera el grupo gCamSal - Local de salida."""
        sal_elem = etree.SubElement(parent, f"{{{NS}}}gCamSal")

        self._add_element(sal_elem, "dDirLocSal", local_sal.dDirLocSal)
        self._add_element(sal_elem, "dNumCasSal", local_sal.dNumCasSal)

        if local_sal.dComp1Sal is not None:
            self._add_element(sal_elem, "dComp1Sal", local_sal.dComp1Sal)
        if local_sal.dComp2Sal is not None:
            self._add_element(sal_elem, "dComp2Sal", local_sal.dComp2Sal)

        self._add_element(sal_elem, "cDepSal", local_sal.cDepSal)
        self._add_element(sal_elem, "dDesDepSal", local_sal.dDesDepSal)

        if local_sal.cDisSal is not None:
            self._add_element(sal_elem, "cDisSal", local_sal.cDisSal)
        if local_sal.dDesDisSal is not None:
            self._add_element(sal_elem, "dDesDisSal", local_sal.dDesDisSal)

        self._add_element(sal_elem, "cCiuSal", local_sal.cCiuSal)
        self._add_element(sal_elem, "dDesCiuSal", local_sal.dDesCiuSal)

        if local_sal.dTelSal is not None:
            self._add_element(sal_elem, "dTelSal", local_sal.dTelSal)

    def _generate_local_entrega(self, parent: etree.Element, local_ent):
        """Genera el grupo gCamEnt - Local de entrega."""
        ent_elem = etree.SubElement(parent, f"{{{NS}}}gCamEnt")

        self._add_element(ent_elem, "dDirLocEnt", local_ent.dDirLocEnt)
        self._add_element(ent_elem, "dNumCasEnt", local_ent.dNumCasEnt)

        if local_ent.dComp1Ent is not None:
            self._add_element(ent_elem, "dComp1Ent", local_ent.dComp1Ent)
        if local_ent.dComp2Ent is not None:
            self._add_element(ent_elem, "dComp2Ent", local_ent.dComp2Ent)

        self._add_element(ent_elem, "cDepEnt", local_ent.cDepEnt)
        self._add_element(ent_elem, "dDesDepEnt", local_ent.dDesDepEnt)

        if local_ent.cDisEnt is not None:
            self._add_element(ent_elem, "cDisEnt", local_ent.cDisEnt)
        if local_ent.dDesDisEnt is not None:
            self._add_element(ent_elem, "dDesDisEnt", local_ent.dDesDisEnt)

        self._add_element(ent_elem, "cCiuEnt", local_ent.cCiuEnt)
        self._add_element(ent_elem, "dDesCiuEnt", local_ent.dDesCiuEnt)

        if local_ent.dTelEnt is not None:
            self._add_element(ent_elem, "dTelEnt", local_ent.dTelEnt)

    def _generate_vehiculo_traslado(self, parent: etree.Element, vehiculo):
        """Genera el grupo gVehTras - Vehículo de traslado."""
        veh_elem = etree.SubElement(parent, f"{{{NS}}}gVehTras")

        # E961 - Tipo de vehículo
        self._add_element(veh_elem, "dTiVehTras", vehiculo.dTiVehTras)

        # E962 - Marca
        self._add_element(veh_elem, "dMarVeh", vehiculo.dMarVeh)

        # E967 - Tipo de identificación del vehículo (opcional)
        if vehiculo.dTipIdenVeh is not None:
            self._add_element(veh_elem, "dTipIdenVeh", vehiculo.dTipIdenVeh)

        # E963 - Número de identificación del vehículo (opcional)
        if vehiculo.dNroIDVeh is not None:
            self._add_element(veh_elem, "dNroIDVeh", vehiculo.dNroIDVeh)

        # E964 - Datos adicionales del vehículo (opcional)
        if vehiculo.dAdicVeh is not None:
            self._add_element(veh_elem, "dAdicVeh", vehiculo.dAdicVeh)

        # E965 - Número de matrícula del vehículo (opcional)
        if vehiculo.dNroMatVeh is not None:
            self._add_element(veh_elem, "dNroMatVeh", vehiculo.dNroMatVeh)

        # E966 - Número de vuelo (opcional)
        if vehiculo.dNroVuelo is not None:
            self._add_element(veh_elem, "dNroVuelo", vehiculo.dNroVuelo)

    def _generate_transportista(self, parent: etree.Element, transportista):
        """Genera el grupo gCamTrans - Transportista."""
        trans_elem = etree.SubElement(parent, f"{{{NS}}}gCamTrans")

        # E981 - Naturaleza del transportista
        self._add_element(trans_elem, "iNatTrans", transportista.iNatTrans)

        # E982 - Nombre o razón social
        self._add_element(trans_elem, "dNomTrans", transportista.dNomTrans)

        # E983 - RUC del transportista (opcional)
        if transportista.dRucTrans is not None:
            self._add_element(trans_elem, "dRucTrans", transportista.dRucTrans)

        # E984 - Dígito verificador (opcional)
        if transportista.dDVTrans is not None:
            self._add_element(trans_elem, "dDVTrans", transportista.dDVTrans)

        # E985 - Tipo de documento de identidad (opcional)
        if transportista.iTipIDTrans is not None:
            self._add_element(trans_elem, "iTipIDTrans", transportista.iTipIDTrans)

        # E986 - Descripción del tipo de documento (opcional)
        if transportista.dDTipIDTrans is not None:
            self._add_element(trans_elem, "dDTipIDTrans", transportista.dDTipIDTrans)

        # E987 - Número de documento (opcional)
        if transportista.dNumIDTrans is not None:
            self._add_element(trans_elem, "dNumIDTrans", transportista.dNumIDTrans)

        # E988 - Nacionalidad (opcional)
        if transportista.cNacTrans is not None:
            self._add_element(trans_elem, "cNacTrans", transportista.cNacTrans)

        # E989 - Descripción de la nacionalidad (opcional)
        if transportista.dDesNacTrans is not None:
            self._add_element(trans_elem, "dDesNacTrans", transportista.dDesNacTrans)

        # E990 - Número de documento del chofer
        self._add_element(trans_elem, "dNumIDChof", transportista.dNumIDChof)

        # E991 - Nombre del chofer
        self._add_element(trans_elem, "dNomChof", transportista.dNomChof)

        # E992 - Domicilio fiscal (opcional)
        if transportista.dDomFisc is not None:
            self._add_element(trans_elem, "dDomFisc", transportista.dDomFisc)

        # E993 - Dirección del chofer (opcional)
        if transportista.dDirChof is not None:
            self._add_element(trans_elem, "dDirChof", transportista.dDirChof)

        # E994 - Nombre del agente (opcional)
        if transportista.dNombAg is not None:
            self._add_element(trans_elem, "dNombAg", transportista.dNombAg)

        # E995 - RUC del agente (opcional)
        if transportista.dRucAg is not None:
            self._add_element(trans_elem, "dRucAg", transportista.dRucAg)

        # E996 - DV del agente (opcional)
        if transportista.dDVAg is not None:
            self._add_element(trans_elem, "dDVAg", transportista.dDVAg)

        # E997 - Dirección del agente (opcional)
        if transportista.dDirAge is not None:
            self._add_element(trans_elem, "dDirAge", transportista.dDirAge)

    def _generate_documento_asociado(self, parent: etree.Element):
        """
        Genera el grupo gCamDEAsoc - Campos que identifican al documento asociado.

        Estructura:
        <gCamDEAsoc>
            <iTipDocAso>1</iTipDocAso>        ← Tipo de documento asociado
            <dDesTipDocAso>...</dDesTipDocAso> ← Descripción
            <dCdCDERef>...</dCdCDERef>        ← CDC (si electrónico)
            <!-- O campos de documento impreso -->
        </gCamDEAsoc>
        """
        asoc_elem = etree.SubElement(parent, f"{{{NS}}}gCamDEAsoc")

        doc_asoc = self.documento.gCamDEAsoc

        # H002 - Tipo de documento asociado
        self._add_element(asoc_elem, "iTipDocAso", doc_asoc.iTipDocAso)

        # H003 - Descripción del tipo
        self._add_element(asoc_elem, "dDesTipDocAso", doc_asoc.dDesTipDocAso)

        # Campos según tipo de documento
        if doc_asoc.iTipDocAso == 1:  # Electrónico
            # H004 - CDC del DTE referenciado
            if doc_asoc.dCdCDERef:
                self._add_element(asoc_elem, "dCdCDERef", doc_asoc.dCdCDERef)

        elif doc_asoc.iTipDocAso == 2:  # Impreso
            # H005 - Número de timbrado
            if doc_asoc.dNTimDI:
                self._add_element(asoc_elem, "dNTimDI", doc_asoc.dNTimDI)

            # H006 - Establecimiento
            if doc_asoc.dEstDocAso:
                self._add_element(asoc_elem, "dEstDocAso", doc_asoc.dEstDocAso)

            # H007 - Punto de expedición
            if doc_asoc.dPExpDocAso:
                self._add_element(asoc_elem, "dPExpDocAso", doc_asoc.dPExpDocAso)

            # H008 - Número del documento
            if doc_asoc.dNumDocAso:
                self._add_element(asoc_elem, "dNumDocAso", doc_asoc.dNumDocAso)

            # H009 - Tipo de documento impreso
            if doc_asoc.iTipoDocAso:
                self._add_element(asoc_elem, "iTipoDocAso", doc_asoc.iTipoDocAso)

            # H010 - Descripción del tipo de documento impreso
            if doc_asoc.dDTipoDocAso:
                self._add_element(asoc_elem, "dDTipoDocAso", doc_asoc.dDTipoDocAso)

            # H011 - Fecha de emisión
            if doc_asoc.dFecEmiDI:
                fecha_str = doc_asoc.dFecEmiDI.strftime("%Y-%m-%d")
                self._add_element(asoc_elem, "dFecEmiDI", fecha_str)

        elif doc_asoc.iTipDocAso == 3:  # Constancia Electrónica
            # H014 - Tipo de constancia
            if doc_asoc.iTipCons:
                self._add_element(asoc_elem, "iTipCons", doc_asoc.iTipCons)

            # H015 - Descripción del tipo de constancia
            if doc_asoc.dDesTipCons:
                self._add_element(asoc_elem, "dDesTipCons", doc_asoc.dDesTipCons)

            # H016 - Número de constancia
            if doc_asoc.dNumCons:
                self._add_element(asoc_elem, "dNumCons", doc_asoc.dNumCons)

            # H017 - Número de control
            if doc_asoc.dNumControl:
                self._add_element(asoc_elem, "dNumControl", doc_asoc.dNumControl)

        # H012 - Número de comprobante de retención (opcional para todos)
        if doc_asoc.dNumComRet:
            self._add_element(asoc_elem, "dNumComRet", doc_asoc.dNumComRet)

        # H013 - Número de resolución de crédito fiscal (opcional para todos)
        if doc_asoc.dNumResCF:
            self._add_element(asoc_elem, "dNumResCF", doc_asoc.dNumResCF)

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
