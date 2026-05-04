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


# Namespace para el XML
NS = NAMESPACE_SIFEN
NSMAP = {None: NS}  # Namespace por defecto


class XMLGenerator:
    """
    Generador de XML para Documentos Electrónicos.

    Convierte objetos DocumentoElectronico a XML según el formato SIFEN.
    """

    def __init__(self, documento: DocumentoElectronico):
        """
        Inicializa el generador.

        Args:
            documento: Documento electrónico a convertir.
        """
        self.documento = documento

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

        # ========================================
        # DE: Documento Electrónico
        # ========================================
        de_elem = etree.SubElement(root, f"{{{NS}}}DE")
        de_elem.set("Id", self.documento.Id)  # CDC como ID del documento

        # ========================================
        # dVerFor: Versión del formato (150)
        # ========================================
        self._add_element(de_elem, "dVerFor", self.documento.dVerFor)

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

        # E700-E799: Ítems (gCamItem) - Repetible
        for item in self.documento.gCamItem:
            self._generate_item(dtip_elem, item)

        # ========================================
        # F. TOTALES Y SUBTOTALES (gTotSub)
        # Cálculo de totales por tasa de IVA
        # ========================================
        self._generate_totales(de_elem)

        # ========================================
        # E600. CONDICIÓN DE LA OPERACIÓN (gCamCond)
        # Contado o crédito, formas de pago
        # ========================================
        self._generate_condicion(de_elem)

        return root

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
        self._add_element(timb_elem, "dFeIniT", self._format_datetime(gTimb.dFeIniT))

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

        self._add_element(dat_elem, "dFeEmiDE", self._format_date(gDatGralOpe.dFeEmiDE))

        # gOpeCom - Operación comercial
        ope_elem = etree.SubElement(dat_elem, f"{{{NS}}}gOpeCom")
        self._add_element(ope_elem, "iTipEmi", gDatGralOpe.iTipEmi)
        if gDatGralOpe.dDesTipEmi:
            self._add_element(ope_elem, "dDesTipEmi", gDatGralOpe.dDesTipEmi)
        self._add_element(ope_elem, "dCodSeg", gDatGralOpe.dCodSeg)
        if gDatGralOpe.dInfoEmi:
            self._add_element(ope_elem, "dInfoEmi", gDatGralOpe.dInfoEmi)
        if gDatGralOpe.dInfoFisc:
            self._add_element(ope_elem, "dInfoFisc", gDatGralOpe.dInfoFisc)

        # gEmis - Emisor
        self._generate_emisor(dat_elem)

        # gDatRec - Receptor
        self._generate_receptor(dat_elem)

    def _generate_emisor(self, parent: etree.Element):
        """Genera el grupo D - Emisor (gEmis)."""
        gEmis = self.documento.gEmis

        emis_elem = etree.SubElement(parent, f"{{{NS}}}gEmis")

        self._add_element(emis_elem, "dRucEm", gEmis.dRucEm)
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
        if gEmis.dNumCas:
            self._add_element(emis_elem, "dNumCas", gEmis.dNumCas)
        if gEmis.dCompDir1:
            self._add_element(emis_elem, "dCompDir1", gEmis.dCompDir1)
        if gEmis.dCompDir2:
            self._add_element(emis_elem, "dCompDir2", gEmis.dCompDir2)
        self._add_element(emis_elem, "cDepEmi", gEmis.cDepEmi)
        if gEmis.dDesDepEmi:
            self._add_element(emis_elem, "dDesDepEmi", gEmis.dDesDepEmi)
        self._add_element(emis_elem, "cDisEmi", gEmis.cDisEmi)
        if gEmis.dDesDisEmi:
            self._add_element(emis_elem, "dDesDisEmi", gEmis.dDesDisEmi)
        self._add_element(emis_elem, "cCiuEmi", gEmis.cCiuEmi)
        if gEmis.dDesCiuEmi:
            self._add_element(emis_elem, "dDesCiuEmi", gEmis.dDesCiuEmi)
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
        if gDatRec.cPaisRec:
            self._add_element(rec_elem, "cPaisRec", gDatRec.cPaisRec)
        if gDatRec.dDesPaisRe:
            self._add_element(rec_elem, "dDesPaisRe", gDatRec.dDesPaisRe)
        if gDatRec.iTiContRec:
            self._add_element(rec_elem, "iTiContRec", gDatRec.iTiContRec)
        if gDatRec.dDesTiContRec:
            self._add_element(rec_elem, "dDesTiContRec", gDatRec.dDesTiContRec)
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

    def _add_element(
        self, parent: etree.Element, tag: str, value: any, namespace: str = NS
    ):
        """
        Agrega un elemento hijo con valor.

        Args:
            parent: Elemento padre.
            tag: Nombre del tag.
            value: Valor del elemento.
            namespace: Namespace del elemento.
        """
        if value is None:
            return

        elem = etree.SubElement(parent, f"{{{namespace}}}{tag}")
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
        if item.dDesUniMed:
            self._add_element(item_elem, "dDesUniMed", item.dDesUniMed)
        self._add_element(
            item_elem, "dCantProSer", self._format_decimal(item.dCantProSer, 4)
        )

        # gValorItem
        self._generate_valor_item(item_elem, item.gValorItem)

    def _generate_valor_item(self, parent: etree.Element, valor_item):
        """Genera valores del ítem (gValorItem)."""
        valor_elem = etree.SubElement(parent, f"{{{NS}}}gValorItem")

        self._add_element(
            valor_elem, "dPUniProSer", self._format_decimal(valor_item.dPUniProSer, 4)
        )
        self._add_element(
            valor_elem, "dTotOpeItem", self._format_decimal(valor_item.dTotOpeItem, 2)
        )
        if valor_item.dTotOpeGs:
            self._add_element(
                valor_elem, "dTotOpeGs", self._format_decimal(valor_item.dTotOpeGs, 2)
            )

        # gCamIVA
        if valor_item.gCamIVA:
            self._generate_iva_item(valor_elem, valor_item.gCamIVA)

    def _generate_iva_item(self, parent: etree.Element, iva_item):
        """Genera IVA del ítem (gCamIVA)."""
        iva_elem = etree.SubElement(parent, f"{{{NS}}}gCamIVA")

        self._add_element(iva_elem, "iAfecIVA", iva_item.iAfecIVA)
        if iva_item.dDesAfecIVA:
            self._add_element(iva_elem, "dDesAfecIVA", iva_item.dDesAfecIVA)
        self._add_element(
            iva_elem, "dPropIVA", self._format_decimal(iva_item.dPropIVA, 2)
        )
        self._add_element(
            iva_elem, "dTasaIVA", self._format_decimal(iva_item.dTasaIVA, 2)
        )
        self._add_element(
            iva_elem, "dBasGravIVA", self._format_decimal(iva_item.dBasGravIVA, 2)
        )
        self._add_element(
            iva_elem, "dLiqIVAItem", self._format_decimal(iva_item.dLiqIVAItem, 2)
        )

    def _generate_totales(self, parent: etree.Element):
        """Genera totales (gTotSub)."""
        totales = self.documento.gTotSub

        tot_elem = etree.SubElement(parent, f"{{{NS}}}gTotSub")

        if totales.dSub10:
            self._add_element(
                tot_elem, "dSub10", self._format_decimal(totales.dSub10, 2)
            )
        self._add_element(tot_elem, "dTotOpe", self._format_decimal(totales.dTotOpe, 2))

        # Subtotales por tasa de IVA
        for sub_iva in totales.gCamIVA:
            sub_elem = etree.SubElement(tot_elem, f"{{{NS}}}gCamIVA")
            self._add_element(sub_elem, "iAfecIVA", sub_iva.iAfecIVA)
            if sub_iva.dDesAfecIVA:
                self._add_element(sub_elem, "dDesAfecIVA", sub_iva.dDesAfecIVA)
            self._add_element(
                sub_elem, "dBasGravIVA", self._format_decimal(sub_iva.dBasGravIVA, 2)
            )
            self._add_element(
                sub_elem, "dLiqIVA", self._format_decimal(sub_iva.dLiqIVA, 2)
            )

        self._add_element(tot_elem, "dTotIVA", self._format_decimal(totales.dTotIVA, 2))
        if totales.dLiqTotIVA10:
            self._add_element(
                tot_elem, "dLiqTotIVA10", self._format_decimal(totales.dLiqTotIVA10, 2)
            )
        self._add_element(
            tot_elem, "dTotGralOpe", self._format_decimal(totales.dTotGralOpe, 2)
        )
        self._add_element(tot_elem, "cMoneOpe", totales.cMoneOpe)
        if totales.dDesMoneOpe:
            self._add_element(tot_elem, "dDesMoneOpe", totales.dDesMoneOpe)

    def _generate_condicion(self, parent: etree.Element):
        """Genera condición de operación (gCamCond)."""
        condicion = self.documento.gPaConEIni

        cond_elem = etree.SubElement(parent, f"{{{NS}}}gCamCond")

        self._add_element(cond_elem, "iCondOpe", condicion.iCondOpe)
        if condicion.dDesCondOpe:
            self._add_element(cond_elem, "dDesCondOpe", condicion.dDesCondOpe)

        # Pagos
        if condicion.gPaConEIni:
            for pago in condicion.gPaConEIni:
                pago_elem = etree.SubElement(cond_elem, f"{{{NS}}}gPaConEIni")
                self._add_element(pago_elem, "iTiPago", pago.iTiPago)
                if pago.dDesTiPag:
                    self._add_element(pago_elem, "dDesTiPag", pago.dDesTiPag)
                if pago.dMonTiPag:
                    self._add_element(
                        pago_elem, "dMonTiPag", self._format_decimal(pago.dMonTiPag, 2)
                    )

        # Cuotas
        if condicion.gCuotas:
            for cuota in condicion.gCuotas:
                cuota_elem = etree.SubElement(cond_elem, f"{{{NS}}}gCuotas")
                self._add_element(cuota_elem, "cMoneCuo", cuota.cMoneCuo)
                if cuota.dDMoneCuo:
                    self._add_element(cuota_elem, "dDMoneCuo", cuota.dDMoneCuo)
                self._add_element(
                    cuota_elem, "dMonCuota", self._format_decimal(cuota.dMonCuota, 2)
                )
                if cuota.dVencCuo:
                    self._add_element(cuota_elem, "dVencCuo", cuota.dVencCuo)


def generate_xml(documento: DocumentoElectronico) -> str:
    """
    Genera XML a partir de un DocumentoElectronico.

    Args:
        documento: Documento a convertir.

    Returns:
        XML como string.
    """
    generator = XMLGenerator(documento)
    root = generator.generate()

    return etree.tostring(
        root, encoding="unicode", pretty_print=True, xml_declaration=True
    )


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
