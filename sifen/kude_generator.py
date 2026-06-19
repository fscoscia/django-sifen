"""
Generador de KuDE (Representación Gráfica en PDF) para Documentos Electrónicos.

Basado en el Manual Técnico SIFEN v150, Capítulo 13.
"""

from typing import Optional, BinaryIO
from decimal import Decimal
from datetime import datetime
import io

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import mm, cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle,
        Paragraph,
        Spacer,
        Image as RLImage,
        PageBreak,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.pdfgen import canvas

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    # Definir clases dummy para evitar errores
    RLImage = None

try:
    import qrcode
    from PIL import Image as PILImage

    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    PILImage = None

from sifen.models.documento import DocumentoElectronico
from sifen.config import TipoAmbiente


class KuDEGenerator:
    """
    Generador de KuDE (Código Único de Documento Electrónico) en formato PDF.

    El KuDE es la representación gráfica del documento electrónico según
    especificaciones del Manual Técnico SIFEN v150, Capítulo 13.
    """

    def __init__(self, ambiente: TipoAmbiente = TipoAmbiente.DEV):
        """
        Inicializa el generador de KuDE.

        Args:
            ambiente: Ambiente SIFEN (DEV o PROD)
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "ReportLab no está instalado. " "Instalar con: pip install reportlab"
            )

        self.ambiente = ambiente
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Configura estilos personalizados para el PDF."""
        # Estilo para título principal
        self.styles.add(
            ParagraphStyle(
                name="KuDETitle",
                parent=self.styles["Heading1"],
                fontSize=14,
                textColor=colors.HexColor("#333333"),
                alignment=TA_CENTER,
                spaceAfter=6,
                fontName="Helvetica-Bold",
            )
        )

        # Estilo para subtítulos
        self.styles.add(
            ParagraphStyle(
                name="KuDESubtitle",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor("#666666"),
                alignment=TA_CENTER,
                spaceAfter=12,
            )
        )

        # Estilo para texto normal
        self.styles.add(
            ParagraphStyle(
                name="KuDENormal",
                parent=self.styles["Normal"],
                fontSize=9,
                textColor=colors.HexColor("#000000"),
            )
        )

        # Estilo para texto pequeño
        self.styles.add(
            ParagraphStyle(
                name="KuDESmall",
                parent=self.styles["Normal"],
                fontSize=7,
                textColor=colors.HexColor("#666666"),
            )
        )

        # Estilo para CDC
        self.styles.add(
            ParagraphStyle(
                name="KuDECDC",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor("#0066CC"),
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
            )
        )

    def generate(
        self,
        documento: DocumentoElectronico,
        output_path: Optional[str] = None,
        logo_path: Optional[str] = None,
    ) -> bytes:
        """
        Genera el KuDE en formato PDF.

        Args:
            documento: Documento electrónico a convertir
            output_path: Ruta donde guardar el PDF (opcional)
            logo_path: Ruta del logo del emisor (opcional)

        Returns:
            Bytes del PDF generado
        """
        # Validar que el documento tenga CDC
        if not documento.CDC:
            raise ValueError("El documento debe tener CDC generado")

        # Crear buffer para el PDF
        buffer = io.BytesIO()

        # Crear documento PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        # Construir contenido
        story = []

        # 1. Encabezado
        story.extend(self._build_header(documento, logo_path))
        story.append(Spacer(1, 0.5 * cm))

        # 2. Datos del emisor y timbrado
        story.extend(self._build_emisor_timbrado(documento))
        story.append(Spacer(1, 0.3 * cm))

        # 3. Datos generales y receptor
        story.extend(self._build_datos_generales(documento))
        story.append(Spacer(1, 0.3 * cm))

        # 4. Tabla de ítems
        story.extend(self._build_items_table(documento))
        story.append(Spacer(1, 0.3 * cm))

        # 5. Subtotales y totales
        story.extend(self._build_totales(documento))
        story.append(Spacer(1, 0.5 * cm))

        # 6. Información de consulta SIFEN y QR
        story.extend(self._build_footer(documento))

        # Generar PDF
        doc.build(story)

        # Obtener bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        # Guardar en archivo si se especificó
        if output_path:
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)

        return pdf_bytes

    def _build_header(
        self, documento: DocumentoElectronico, logo_path: Optional[str] = None
    ) -> list:
        """Construye el encabezado del KuDE estilo Equifax."""
        elements = []

        emisor = documento.gEmis
        timbrado = documento.gTimb

        # Determinar tipo de documento
        tipo_doc_map = {
            1: "Factura electrónica Nro:",
            4: "Autofactura electrónica Nro:",
            5: "Nota de crédito electrónica Nro:",
            6: "Nota de débito electrónica Nro:",
            7: "Nota de remisión electrónica Nro:",
        }
        tipo_doc_label = tipo_doc_map.get(
            documento.gTimb.iTiDE, "Documento electrónico Nro:"
        )

        # Crear contenido del encabezado
        # Columna izquierda: Logo + datos emisor
        left_content = []

        # Logo
        if logo_path:
            try:
                logo = RLImage(logo_path, width=3 * cm, height=3 * cm)
                left_content.append([logo])
            except:
                left_content.append([""])

        # Datos del emisor (debajo del logo)
        left_content.append(
            [Paragraph(f"<b>{emisor.dNomEmi}</b>", self.styles["KuDENormal"])]
        )
        left_content.append([Paragraph(f"{emisor.dDirEmi}", self.styles["KuDESmall"])])
        left_content.append(
            [Paragraph(f"Ciudad: {emisor.dDesCiuEmi or ''}", self.styles["KuDESmall"])]
        )
        left_content.append(
            [Paragraph(f"Teléfono: {emisor.dTelEmi}", self.styles["KuDESmall"])]
        )

        # Actividad económica
        if emisor.gActEco:
            act_eco = emisor.gActEco[0].dDesActEco if emisor.gActEco else ""
            left_content.append(
                [Paragraph(f"Actividad económica: {act_eco}", self.styles["KuDESmall"])]
            )

        left_table = Table(left_content, colWidths=[6 * cm])
        left_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )

        # Columna derecha: Timbrado y número de documento
        right_content = [
            [
                Paragraph(
                    f"<b>RUC:</b> {emisor.dRucEm}-{emisor.dDVEmi}",
                    self.styles["KuDENormal"],
                )
            ],
            [
                Paragraph(
                    f"<b>Timbrado Nº:</b> {timbrado.dNumTim}", self.styles["KuDENormal"]
                )
            ],
            [
                Paragraph(
                    f"<b>Fecha de inicio de vigencia:</b> {timbrado.dFeIniT}",
                    self.styles["KuDENormal"],
                )
            ],
            [Spacer(1, 0.3 * cm)],
            [Paragraph(f"<b>{tipo_doc_label}</b>", self.styles["KuDENormal"])],
            [
                Paragraph(
                    f"<b>{timbrado.dEst}-{timbrado.dPunExp}-{timbrado.dNumDoc}</b>",
                    self.styles["KuDETitle"],
                )
            ],
        ]

        right_table = Table(right_content, colWidths=[11 * cm])
        right_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )

        # Combinar ambas columnas en una tabla
        header_data = [[left_table, right_table]]
        header_table = Table(header_data, colWidths=[6 * cm, 11 * cm])
        header_table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 1.5, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )

        elements.append(header_table)

        return elements

    def _build_emisor_timbrado(self, documento: DocumentoElectronico) -> list:
        """Ya no se usa - el encabezado ahora incluye todo."""
        return []

    def _build_datos_generales(self, documento: DocumentoElectronico) -> list:
        """Construye la sección de datos generales y receptor estilo Equifax."""
        elements = []

        datos = documento.gDatGralOpe
        receptor = documento.gDatRec

        # Formatear fecha
        fecha_emision = datos.dFeEmiDE.strftime("%d/%m/%Y")

        # Condición de venta
        condicion = (
            "CONTADO"
            if documento.gPaConEIni and documento.gPaConEIni.iCondOpe == 1
            else "CREDITO"
        )

        # Plazo (si es crédito)
        plazo = ""
        if documento.gPaConEIni and documento.gPaConEIni.iCondOpe == 2:
            if documento.gPaConEIni.gCuotas:
                plazo = f"{len(documento.gPaConEIni.gCuotas)} cuotas"

        # RUC del receptor
        ruc_receptor = ""
        if receptor.dRucRec:
            ruc_receptor = (
                f"{receptor.dRucRec}-{receptor.dDVRec}"
                if receptor.dDVRec
                else receptor.dRucRec
            )
        elif receptor.dNumIDRec:
            ruc_receptor = receptor.dNumIDRec

        # Crear tabla con dos columnas
        data = [
            # Fila 1
            [f"Fecha de Emisión: {fecha_emision}", f"RUC: {ruc_receptor}"],
            # Fila 2
            [f"Condición de Venta: {condicion}", f"Cliente: {receptor.dNomRec}"],
            # Fila 3
            [
                f"Plazo: {plazo}" if plazo else "",
                f"Dirección: {receptor.dDirRec or ''}",
            ],
            # Fila 4
            [
                f"Moneda: {documento.gTotSub.cMoneOpe}",
                f"Teléfono: {receptor.dTelRec or ''}",
            ],
            # Fila 5
            [
                f"Tipo de Cambio: {documento.gTotSub.dTiCam or ''}",
                f"Correo electrónico: {receptor.dEmailRec or ''}",
            ],
            # Fila 6
            [
                "CDC asociado:",
                f"Tipo de Transacción: {receptor.dDesTiOpe or 'Prestación de servicios'}",
            ],
            # Fila 7
            ["Tipo Doc. asociado:", "Motivo Emisión:"],
            # Fila 8
            ["Nº Comp. asociado:", "Periodo de Facturacion:"],
            # Fila 9
            ["Cod. Afiliado: ", ""],
        ]

        table = Table(data, colWidths=[8.5 * cm, 8.5 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 1, colors.black),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("FONTSIZE", (0, 0), (-1, -1), 7),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )

        elements.append(table)

        return elements

    def _build_items_table(self, documento: DocumentoElectronico) -> list:
        """Construye la tabla de ítems."""
        elements = []

        # Encabezado de la tabla (sin "Valor de Venta")
        items_data = [
            [
                "Cod",
                "Descripción",
                "Unidad",
                "Cantidad",
                "Precio\nUnitario",
                "Descuento",
                "Exentas",
                "5%",
                "10%",
            ]
        ]

        # Agregar cada ítem
        for item in documento.gCamItem:
            if not item.gValorItem:
                continue

            valor = item.gValorItem

            # Determinar columnas de IVA
            exentas = ""
            iva5 = ""
            iva10 = ""

            if valor.gCamIVA:
                if valor.gCamIVA.iAfecIVA == 1:  # Gravado IVA
                    if valor.gCamIVA.dTasaIVA == Decimal("5"):
                        iva5 = self._format_currency(valor.dTotOpeItem)
                    elif valor.gCamIVA.dTasaIVA == Decimal("10"):
                        iva10 = self._format_currency(valor.dTotOpeItem)
                elif valor.gCamIVA.iAfecIVA == 2:  # Exento
                    exentas = self._format_currency(valor.dTotOpeItem)

            items_data.append(
                [
                    item.dCodInt[:10],  # Limitar longitud
                    item.dDesProSer[:30],  # Limitar longitud
                    item.dDesUniMed or "UNI",
                    str(item.dCantProSer),
                    self._format_currency(valor.dPUniProSer),
                    self._format_currency(valor.dDescItem or Decimal("0")),
                    exentas,
                    iva5,
                    iva10,
                ]
            )

        # Crear tabla con ancho total de 17 cm (9 columnas)
        items_table = Table(
            items_data,
            colWidths=[
                1.2 * cm,  # Cod
                4.5 * cm,  # Descripción
                1.3 * cm,  # Unidad
                1.3 * cm,  # Cantidad
                2.0 * cm,  # Precio Unitario
                1.7 * cm,  # Descuento
                1.7 * cm,  # Exentas
                1.7 * cm,  # 5%
                1.6 * cm,  # 10%
            ],
        )

        items_table.setStyle(
            TableStyle(
                [
                    # Encabezado
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8E8E8")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#000000")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 7),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
                    # Contenido
                    ("FONTSIZE", (0, 1), (-1, -1), 7),
                    ("ALIGN", (0, 1), (0, -1), "LEFT"),  # Código
                    ("ALIGN", (1, 1), (1, -1), "LEFT"),  # Descripción
                    ("ALIGN", (2, 1), (2, -1), "CENTER"),  # Unidad
                    ("ALIGN", (3, 1), (-1, -1), "RIGHT"),  # Resto alineado a derecha
                    # Bordes
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    # Padding (igual que tabla de datos generales)
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )

        elements.append(items_table)

        return elements

    def _build_totales(self, documento: DocumentoElectronico) -> list:
        """Construye la sección de subtotales y totales."""
        elements = []

        totales = documento.gTotSub

        # Datos de totales
        totales_data = [
            ["SUBTOTAL:", self._format_currency(totales.dTotOpe)],
            ["TOTAL A PAGAR:", self._format_currency(totales.dTotGralOpe)],
            ["TOTAL EN GUARANÍES:", self._format_currency(totales.dTotGralOpe)],
        ]

        # Agregar liquidación de IVA
        iva_data = []
        if totales.dLiqTotIVA5:
            iva_data.append(["(5%)", self._format_currency(totales.dLiqTotIVA5)])
        if totales.dLiqTotIVA10:
            iva_data.append(["(10%)", self._format_currency(totales.dLiqTotIVA10)])

        if iva_data:
            iva_data.append(["TOTAL IVA:", self._format_currency(totales.dTotIVA)])

        # Tabla de totales
        totales_table = Table(totales_data, colWidths=[14 * cm, 3 * cm])
        totales_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )

        elements.append(totales_table)

        # Tabla de liquidación IVA
        if iva_data:
            elements.append(Spacer(1, 0.2 * cm))

            iva_table = Table(
                [["LIQUIDACIÓN IVA:", "", "", ""]] + iva_data,
                colWidths=[11 * cm, 2 * cm, 2 * cm, 2 * cm],
            )
            iva_table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("LEFTPADDING", (0, 0), (-1, -1), 5),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                        ("TOPPADDING", (0, 0), (-1, -1), 3),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ]
                )
            )

            elements.append(iva_table)

        return elements

    def _build_footer(self, documento: DocumentoElectronico) -> list:
        """Construye el pie con información de consulta y QR."""
        elements = []

        # URL de consulta
        url_consulta = self._get_consulta_url()

        # Generar QR
        qr_image = None
        if QRCODE_AVAILABLE:
            try:
                qr_image = self._generate_qr(documento.CDC, url_consulta)
            except:
                pass

        # Texto de consulta
        consulta_text = (
            f"Consulte la validez de esta {self._get_tipo_documento_nombre(documento.gTimb.iTiDE)} "
            f"con el número de CDC impreso abajo en:<br/>"
            f"<b>{url_consulta}</b>"
        )

        # CDC
        cdc_formatted = self._format_cdc(documento.CDC)
        cdc_text = f"<b>CDC: {cdc_formatted}</b>"

        # Tabla con QR y texto
        footer_data = []

        if qr_image:
            footer_data.append(
                [qr_image, Paragraph(consulta_text, self.styles["KuDENormal"])]
            )
        else:
            footer_data.append([Paragraph(consulta_text, self.styles["KuDENormal"])])

        footer_table = Table(
            footer_data, colWidths=[4 * cm, 13 * cm] if qr_image else [17 * cm]
        )
        footer_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )

        elements.append(footer_table)
        elements.append(Spacer(1, 0.3 * cm))

        # CDC
        elements.append(Paragraph(cdc_text, self.styles["KuDECDC"]))
        elements.append(Spacer(1, 0.3 * cm))

        # Texto legal
        legal_text = (
            "ESTE DOCUMENTO ES UNA REPRESENTACIÓN GRÁFICA DE UN DOCUMENTO ELECTRÓNICO (XML)<br/>"
            "<b>Información de interés del facturador electrónico emisor.</b><br/>"
            "Si su documento electrónico presenta algún error, podrá solicitar la modificación "
            "dentro de las 72 horas siguientes de la emisión de este comprobante"
        )

        elements.append(Paragraph(legal_text, self.styles["KuDESmall"]))

        return elements

    def _generate_qr(self, cdc: str, url_base: str):
        """Genera código QR con el CDC."""
        if not QRCODE_AVAILABLE:
            return None

        try:
            # URL completa con CDC
            url_qr = f"{url_base}?cdc={cdc}"

            # Generar QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=1,
            )
            qr.add_data(url_qr)
            qr.make(fit=True)

            # Crear imagen
            qr_img = qr.make_image(fill_color="black", back_color="white")

            # Convertir a bytes
            buffer = io.BytesIO()
            qr_img.save(buffer, format="PNG")
            buffer.seek(0)

            # Crear objeto Image de ReportLab
            return RLImage(buffer, width=3 * cm, height=3 * cm)
        except:
            return None

    def _get_consulta_url(self) -> str:
        """Obtiene la URL de consulta según el ambiente."""
        if self.ambiente == TipoAmbiente.PROD:
            return "https://ekuatia.set.gov.py/consultas/"
        else:
            return "https://ekuatia.set.gov.py/consultas-test/"

    def _get_tipo_documento_nombre(self, tipo: int) -> str:
        """Obtiene el nombre del tipo de documento."""
        nombres = {
            1: "Factura Electrónica",
            4: "Autofactura Electrónica",
            5: "Nota de Crédito Electrónica",
            6: "Nota de Débito Electrónica",
            7: "Nota de Remisión Electrónica",
        }
        return nombres.get(tipo, "Documento Electrónico")

    def _format_currency(self, amount: Decimal) -> str:
        """Formatea un monto como moneda."""
        return f"{amount:,.0f}".replace(",", ".")

    def _format_cdc(self, cdc: str) -> str:
        """Formatea el CDC en grupos de 4 dígitos."""
        # Dividir en grupos de 4
        groups = [cdc[i : i + 4] for i in range(0, len(cdc), 4)]
        return " ".join(groups)


def generar_kude(
    documento: DocumentoElectronico,
    output_path: Optional[str] = None,
    logo_path: Optional[str] = None,
    ambiente: TipoAmbiente = TipoAmbiente.DEV,
) -> bytes:
    """
    Función helper para generar KuDE.

    Args:
        documento: Documento electrónico
        output_path: Ruta donde guardar el PDF (opcional)
        logo_path: Ruta del logo (opcional)
        ambiente: Ambiente SIFEN

    Returns:
        Bytes del PDF generado
    """
    generator = KuDEGenerator(ambiente=ambiente)
    return generator.generate(documento, output_path, logo_path)
