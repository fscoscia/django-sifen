"""
Modelos Django para almacenar documentos electrónicos y configuración SIFEN.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class ConfiguracionSIFEN(models.Model):
    """
    Configuración de SIFEN por empresa.
    
    Almacena certificados y credenciales para comunicarse con SIFEN.
    """
    
    AMBIENTE_CHOICES = [
        ('dev', 'Desarrollo'),
        ('prod', 'Producción'),
    ]
    
    empresa = models.CharField(
        max_length=200,
        help_text="Nombre de la empresa"
    )
    ruc_empresa = models.CharField(
        max_length=20,
        unique=True,
        help_text="RUC de la empresa (formato: XXXXXXXX-X)"
    )
    ambiente = models.CharField(
        max_length=10,
        choices=AMBIENTE_CHOICES,
        default='dev',
        help_text="Ambiente de SIFEN"
    )
    
    # Certificado digital
    certificado = models.BinaryField(
        help_text="Certificado PFX en formato binario"
    )
    certificado_contrasena_encriptada = models.CharField(
        max_length=500,
        help_text="Contraseña del certificado (encriptada)"
    )
    
    # Código de Seguridad del Contribuyente
    csc = models.CharField(
        max_length=100,
        help_text="Código de Seguridad del Contribuyente"
    )
    csc_id = models.CharField(
        max_length=10,
        help_text="ID del CSC"
    )
    
    # Configuración adicional
    activo = models.BooleanField(
        default=True,
        help_text="Si esta configuración está activa"
    )
    habilitar_nota_tecnica_13 = models.BooleanField(
        default=True,
        help_text="Habilitar cambios de Nota Técnica 13"
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuración SIFEN"
        verbose_name_plural = "Configuraciones SIFEN"
        ordering = ['-activo', 'empresa']
    
    def __str__(self):
        return f"{self.empresa} ({self.get_ambiente_display()})"


class DocumentoElectronico(models.Model):
    """
    Registro de documentos electrónicos enviados a SIFEN.
    """
    
    TIPO_DOCUMENTO_CHOICES = [
        (1, 'Factura Electrónica'),
        (4, 'Autofactura Electrónica'),
        (5, 'Nota de Crédito Electrónica'),
        (6, 'Nota de Débito Electrónica'),
        (7, 'Nota de Remisión Electrónica'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('cancelado', 'Cancelado'),
        ('error', 'Error'),
    ]
    
    # Identificación del documento
    cdc = models.CharField(
        max_length=44,
        unique=True,
        db_index=True,
        help_text="Código de Control del documento"
    )
    tipo_documento = models.IntegerField(
        choices=TIPO_DOCUMENTO_CHOICES,
        help_text="Tipo de documento electrónico"
    )
    numero_documento = models.CharField(
        max_length=20,
        help_text="Número del documento (formato: 001-001-0000001)"
    )
    numero_timbrado = models.BigIntegerField(
        help_text="Número de timbrado"
    )
    
    # Fechas
    fecha_emision = models.DateField(
        help_text="Fecha de emisión del documento"
    )
    fecha_envio = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de envío a SIFEN"
    )
    
    # Partes del documento
    emisor_ruc = models.CharField(
        max_length=20,
        db_index=True,
        help_text="RUC del emisor"
    )
    emisor_nombre = models.CharField(
        max_length=200,
        help_text="Nombre del emisor"
    )
    receptor_ruc = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        db_index=True,
        help_text="RUC del receptor"
    )
    receptor_nombre = models.CharField(
        max_length=200,
        help_text="Nombre del receptor"
    )
    
    # Montos
    total_operacion = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Total de la operación sin IVA"
    )
    total_iva = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Total de IVA"
    )
    total_general = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Total general (con IVA)"
    )
    
    # Estado y respuesta
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        db_index=True,
        help_text="Estado del documento"
    )
    numero_protocolo = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Número de protocolo de SIFEN"
    )
    codigo_respuesta = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Código de respuesta de SIFEN"
    )
    mensaje_respuesta = models.TextField(
        null=True,
        blank=True,
        help_text="Mensaje de respuesta de SIFEN"
    )
    
    # XMLs
    xml_firmado = models.TextField(
        help_text="XML del documento firmado digitalmente"
    )
    respuesta_sifen = models.JSONField(
        null=True,
        blank=True,
        help_text="Respuesta completa de SIFEN en formato JSON"
    )
    
    # Relación con configuración
    configuracion = models.ForeignKey(
        ConfiguracionSIFEN,
        on_delete=models.PROTECT,
        related_name='documentos',
        help_text="Configuración SIFEN utilizada"
    )
    
    # Metadatos
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Documento Electrónico"
        verbose_name_plural = "Documentos Electrónicos"
        ordering = ['-fecha_envio']
        indexes = [
            models.Index(fields=['-fecha_envio']),
            models.Index(fields=['estado', '-fecha_envio']),
            models.Index(fields=['emisor_ruc', '-fecha_envio']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_documento_display()} {self.numero_documento} - {self.cdc[:10]}..."


class LogSIFEN(models.Model):
    """
    Log de comunicaciones con SIFEN.
    
    Registra todas las peticiones y respuestas para auditoría.
    """
    
    TIPO_OPERACION_CHOICES = [
        ('recepcion_de', 'Recepción DE'),
        ('consulta_de', 'Consulta DE'),
        ('consulta_ruc', 'Consulta RUC'),
        ('recepcion_lote', 'Recepción Lote'),
        ('consulta_lote', 'Consulta Lote'),
        ('recepcion_evento', 'Recepción Evento'),
    ]
    
    documento = models.ForeignKey(
        DocumentoElectronico,
        on_delete=models.CASCADE,
        related_name='logs',
        null=True,
        blank=True,
        help_text="Documento relacionado (si aplica)"
    )
    tipo_operacion = models.CharField(
        max_length=50,
        choices=TIPO_OPERACION_CHOICES,
        help_text="Tipo de operación realizada"
    )
    
    # Request
    request_xml = models.TextField(
        help_text="XML de la petición enviada"
    )
    request_url = models.CharField(
        max_length=500,
        help_text="URL del servicio"
    )
    
    # Response
    response_xml = models.TextField(
        help_text="XML de la respuesta recibida"
    )
    codigo_respuesta = models.CharField(
        max_length=10,
        help_text="Código de respuesta"
    )
    mensaje = models.TextField(
        help_text="Mensaje de respuesta"
    )
    
    # Metadatos
    fecha = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Fecha y hora de la operación"
    )
    duracion_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="Duración de la operación en milisegundos"
    )
    exitoso = models.BooleanField(
        default=True,
        help_text="Si la operación fue exitosa"
    )
    
    class Meta:
        verbose_name = "Log SIFEN"
        verbose_name_plural = "Logs SIFEN"
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['-fecha']),
            models.Index(fields=['tipo_operacion', '-fecha']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_operacion_display()} - {self.fecha.strftime('%Y-%m-%d %H:%M:%S')}"
