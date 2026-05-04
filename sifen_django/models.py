"""
Modelos Django para almacenar configuración y documentos electrónicos SIFEN.
"""

from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class ConfiguracionSIFEN(models.Model):
    """
    Modelo para almacenar la configuración de SIFEN en la base de datos.
    
    Permite almacenar el certificado digital directamente en la DB,
    evitando la necesidad de archivos en el filesystem.
    """
    
    AMBIENTE_CHOICES = [
        ('DEV', 'Desarrollo'),
        ('PROD', 'Producción'),
    ]
    
    nombre = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nombre identificador de esta configuración (ej: 'principal', 'sucursal_1')"
    )
    
    ambiente = models.CharField(
        max_length=4,
        choices=AMBIENTE_CHOICES,
        default='DEV',
        help_text="Ambiente de SIFEN a utilizar"
    )
    
    # Certificado almacenado en la base de datos
    certificado_pfx = models.BinaryField(
        help_text="Archivo PFX del certificado digital (almacenado como bytes)"
    )
    
    certificado_contrasena = models.CharField(
        max_length=255,
        help_text="Contraseña del certificado (se recomienda encriptar)"
    )
    
    # CSC (Código de Seguridad del Contribuyente)
    csc = models.CharField(
        max_length=32,
        validators=[MinLengthValidator(32)],
        help_text="Código de Seguridad del Contribuyente"
    )
    
    csc_id = models.CharField(
        max_length=4,
        help_text="ID del CSC"
    )
    
    # Configuraciones adicionales
    habilitar_nota_tecnica_13 = models.BooleanField(
        default=True,
        help_text="Habilitar cambios de la Nota Técnica 13 (campos IVA)"
    )
    
    activo = models.BooleanField(
        default=True,
        help_text="Si esta configuración está activa"
    )
    
    # Metadata
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuración SIFEN"
        verbose_name_plural = "Configuraciones SIFEN"
        ordering = ['-activo', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_ambiente_display()})"
    
    def to_sifen_config(self):
        """
        Convierte este modelo a una instancia de SifenConfig.
        
        Returns:
            SifenConfig configurado con los datos de este modelo.
        """
        from sifen.config import SifenConfig, TipoAmbiente
        
        return SifenConfig(
            ambiente=TipoAmbiente[self.ambiente],
            certificado_bytes=bytes(self.certificado_pfx),  # Desde la DB
            certificado_contrasena=self.certificado_contrasena,
            csc=self.csc,
            csc_id=self.csc_id,
            habilitar_nota_tecnica_13=self.habilitar_nota_tecnica_13,
        )
    
    @classmethod
    def get_activa(cls):
        """
        Obtiene la configuración activa.
        
        Returns:
            ConfiguracionSIFEN activa o None si no hay ninguna.
        """
        return cls.objects.filter(activo=True).first()


class DocumentoElectronicoModel(models.Model):
    """
    Modelo para almacenar Documentos Electrónicos enviados a SIFEN.
    """
    
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('cancelado', 'Cancelado'),
    ]
    
    TIPO_CHOICES = [
        (1, 'Factura Electrónica'),
        (4, 'Factura Electrónica de Exportación'),
        (5, 'Factura Electrónica de Importación'),
        (6, 'Autofactura Electrónica'),
        (7, 'Nota de Crédito Electrónica'),
        (8, 'Nota de Débito Electrónica'),
        (9, 'Nota de Remisión Electrónica'),
        (10, 'Comprobante de Retención Electrónico'),
    ]
    
    # Identificación
    cdc = models.CharField(
        max_length=44,
        unique=True,
        null=True,
        blank=True,
        help_text="Código de Control del Documento"
    )
    
    tipo_documento = models.IntegerField(
        choices=TIPO_CHOICES,
        help_text="Tipo de documento electrónico"
    )
    
    numero_documento = models.CharField(
        max_length=50,
        help_text="Número del documento"
    )
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='borrador',
        help_text="Estado del documento"
    )
    
    # XMLs
    xml_original = models.TextField(
        help_text="XML del documento antes de firmar"
    )
    
    xml_firmado = models.TextField(
        null=True,
        blank=True,
        help_text="XML del documento firmado digitalmente"
    )
    
    # Datos estructurados (JSON)
    datos_json = models.JSONField(
        null=True,
        blank=True,
        help_text="Datos del documento en formato JSON para consultas rápidas"
    )
    
    # QR
    qr_data = models.TextField(
        null=True,
        blank=True,
        help_text="Datos para generar el código QR"
    )
    
    # Relación genérica con factura/venta del usuario
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Tipo de objeto relacionado (ej: Factura, Venta)"
    )
    
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="ID del objeto relacionado"
    )
    
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Configuración usada
    configuracion = models.ForeignKey(
        ConfiguracionSIFEN,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="Configuración SIFEN utilizada"
    )
    
    # Fechas
    fecha_emision = models.DateTimeField(
        help_text="Fecha de emisión del documento"
    )
    
    fecha_envio = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha de envío a SIFEN"
    )
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Documento Electrónico"
        verbose_name_plural = "Documentos Electrónicos"
        ordering = ['-fecha_emision']
        indexes = [
            models.Index(fields=['cdc']),
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_emision']),
            models.Index(fields=['tipo_documento']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_documento_display()} - {self.numero_documento}"
    
    def get_qr_url(self):
        """Genera la URL del código QR."""
        if self.qr_data:
            from sifen.config import SifenConfig, TipoAmbiente
            if self.configuracion:
                config = self.configuracion.to_sifen_config()
                return f"{config.url_consulta_qr}{self.qr_data}"
        return None
    
    def to_dict(self):
        """Convierte el documento a diccionario."""
        return {
            'cdc': self.cdc,
            'tipo_documento': self.tipo_documento,
            'numero_documento': self.numero_documento,
            'estado': self.estado,
            'fecha_emision': self.fecha_emision.isoformat() if self.fecha_emision else None,
            'qr_url': self.get_qr_url(),
            'datos': self.datos_json,
        }


class RespuestaSIFEN(models.Model):
    """
    Modelo para almacenar respuestas de SIFEN.
    """
    
    documento = models.ForeignKey(
        DocumentoElectronicoModel,
        on_delete=models.CASCADE,
        related_name='respuestas',
        help_text="Documento relacionado"
    )
    
    tipo_operacion = models.CharField(
        max_length=50,
        help_text="Tipo de operación (recepcion, consulta, etc.)"
    )
    
    codigo_respuesta = models.CharField(
        max_length=10,
        help_text="Código de respuesta de SIFEN"
    )
    
    mensaje = models.TextField(
        help_text="Mensaje de respuesta"
    )
    
    respuesta_completa = models.JSONField(
        help_text="Respuesta completa de SIFEN en JSON"
    )
    
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Respuesta SIFEN"
        verbose_name_plural = "Respuestas SIFEN"
        ordering = ['-creado_en']
    
    def __str__(self):
        return f"{self.tipo_operacion} - {self.codigo_respuesta}"


class Lote(models.Model):
    """
    Modelo para almacenar lotes de documentos electrónicos.
    """
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('error', 'Error'),
    ]
    
    numero_lote = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text="Número de lote asignado por SIFEN"
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )
    
    documentos = models.ManyToManyField(
        DocumentoElectronicoModel,
        related_name='lotes',
        help_text="Documentos incluidos en este lote"
    )
    
    configuracion = models.ForeignKey(
        ConfiguracionSIFEN,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    
    fecha_envio = models.DateTimeField(
        null=True,
        blank=True
    )
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"
        ordering = ['-creado_en']
    
    def __str__(self):
        return f"Lote {self.numero_lote or self.id} - {self.estado}"


class EventoDE(models.Model):
    """
    Modelo para almacenar eventos de documentos electrónicos.
    """
    
    TIPO_EVENTO_CHOICES = [
        ('cancelacion', 'Cancelación'),
        ('inutilizacion', 'Inutilización'),
        ('conformidad', 'Conformidad'),
        ('disconformidad', 'Disconformidad'),
        ('desconocimiento', 'Desconocimiento'),
        ('notificacion', 'Notificación'),
    ]
    
    documento = models.ForeignKey(
        DocumentoElectronicoModel,
        on_delete=models.CASCADE,
        related_name='eventos'
    )
    
    tipo_evento = models.CharField(
        max_length=20,
        choices=TIPO_EVENTO_CHOICES
    )
    
    motivo = models.TextField(
        help_text="Motivo del evento"
    )
    
    xml_evento = models.TextField(
        null=True,
        blank=True,
        help_text="XML del evento firmado"
    )
    
    enviado = models.BooleanField(
        default=False
    )
    
    fecha_envio = models.DateTimeField(
        null=True,
        blank=True
    )
    
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Evento DE"
        verbose_name_plural = "Eventos DE"
        ordering = ['-creado_en']
    
    def __str__(self):
        return f"{self.get_tipo_evento_display()} - {self.documento}"
