"""
Configuración del Django Admin para SIFEN.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from django_sifen_api.models import (
    ConfiguracionSIFEN,
    DocumentoElectronico,
    LogSIFEN,
)


@admin.register(ConfiguracionSIFEN)
class ConfiguracionSIFENAdmin(admin.ModelAdmin):
    """Admin para configuraciones SIFEN."""
    
    list_display = [
        'empresa',
        'ruc_empresa',
        'ambiente',
        'activo_badge',
        'fecha_creacion',
    ]
    list_filter = ['ambiente', 'activo', 'fecha_creacion']
    search_fields = ['empresa', 'ruc_empresa']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    
    fieldsets = (
        ('Información General', {
            'fields': ('empresa', 'ruc_empresa', 'ambiente', 'activo')
        }),
        ('Certificado Digital', {
            'fields': ('certificado', 'certificado_contrasena_encriptada'),
            'classes': ('collapse',),
        }),
        ('CSC', {
            'fields': ('csc', 'csc_id'),
        }),
        ('Configuración Adicional', {
            'fields': ('habilitar_nota_tecnica_13',),
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',),
        }),
    )
    
    def activo_badge(self, obj):
        """Muestra badge de activo/inactivo."""
        if obj.activo:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Activo</span>'
            )
        return format_html(
            '<span style="color: gray;">○ Inactivo</span>'
        )
    activo_badge.short_description = 'Estado'
    
    actions = ['activar_configuracion']
    
    def activar_configuracion(self, request, queryset):
        """Activa una configuración y desactiva las demás."""
        if queryset.count() != 1:
            self.message_user(request, 'Seleccione solo una configuración', level='error')
            return
        
        ConfiguracionSIFEN.objects.update(activo=False)
        queryset.update(activo=True)
        self.message_user(request, 'Configuración activada exitosamente')
    activar_configuracion.short_description = 'Activar configuración seleccionada'


@admin.register(DocumentoElectronico)
class DocumentoElectronicoAdmin(admin.ModelAdmin):
    """Admin para documentos electrónicos."""
    
    list_display = [
        'numero_documento',
        'tipo_documento',
        'emisor_ruc',
        'receptor_nombre',
        'total_general',
        'estado_badge',
        'fecha_envio',
    ]
    list_filter = [
        'estado',
        'tipo_documento',
        'fecha_emision',
        'fecha_envio',
    ]
    search_fields = [
        'cdc',
        'numero_documento',
        'emisor_ruc',
        'emisor_nombre',
        'receptor_ruc',
        'receptor_nombre',
    ]
    readonly_fields = [
        'cdc',
        'fecha_envio',
        'fecha_modificacion',
        'xml_preview',
        'respuesta_preview',
    ]
    
    fieldsets = (
        ('Identificación', {
            'fields': ('cdc', 'tipo_documento', 'numero_documento', 'numero_timbrado')
        }),
        ('Emisor', {
            'fields': ('emisor_ruc', 'emisor_nombre'),
        }),
        ('Receptor', {
            'fields': ('receptor_ruc', 'receptor_nombre'),
        }),
        ('Montos', {
            'fields': ('total_operacion', 'total_iva', 'total_general'),
        }),
        ('Estado', {
            'fields': (
                'estado',
                'numero_protocolo',
                'codigo_respuesta',
                'mensaje_respuesta',
            ),
        }),
        ('XML y Respuesta', {
            'fields': ('xml_preview', 'respuesta_preview'),
            'classes': ('collapse',),
        }),
        ('Metadatos', {
            'fields': ('configuracion', 'fecha_emision', 'fecha_envio', 'fecha_modificacion'),
            'classes': ('collapse',),
        }),
    )
    
    def estado_badge(self, obj):
        """Muestra badge de estado con colores."""
        colors = {
            'pendiente': 'orange',
            'aprobado': 'green',
            'rechazado': 'red',
            'cancelado': 'gray',
            'error': 'darkred',
        }
        color = colors.get(obj.estado, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def xml_preview(self, obj):
        """Muestra preview del XML."""
        if obj.xml_firmado:
            preview = obj.xml_firmado[:500] + '...' if len(obj.xml_firmado) > 500 else obj.xml_firmado
            return format_html('<pre>{}</pre>', preview)
        return '-'
    xml_preview.short_description = 'XML Firmado (Preview)'
    
    def respuesta_preview(self, obj):
        """Muestra preview de la respuesta."""
        if obj.respuesta_sifen:
            import json
            return format_html(
                '<pre>{}</pre>',
                json.dumps(obj.respuesta_sifen, indent=2, ensure_ascii=False)
            )
        return '-'
    respuesta_preview.short_description = 'Respuesta SIFEN'
    
    actions = ['consultar_estado', 'ver_logs']
    
    def consultar_estado(self, request, queryset):
        """Consulta el estado de documentos en SIFEN."""
        from sifen import SifenClient
        from sifen.config import SifenConfig, TipoAmbiente
        
        actualizados = 0
        for doc in queryset:
            try:
                # Crear configuración
                config = SifenConfig(
                    ambiente=TipoAmbiente.DEV if doc.configuracion.ambiente == 'dev' else TipoAmbiente.PROD,
                    certificado_bytes=bytes(doc.configuracion.certificado),
                    certificado_contrasena=doc.configuracion.certificado_contrasena_encriptada,
                    csc=doc.configuracion.csc,
                    csc_id=doc.configuracion.csc_id,
                )
                
                # Consultar
                client = SifenClient(config)
                respuesta = client.consultar_documento(doc.cdc)
                
                # Actualizar estado
                if respuesta.encontrado and respuesta.estado:
                    if respuesta.estado == 'Aprobado':
                        doc.estado = 'aprobado'
                    elif respuesta.estado == 'Rechazado':
                        doc.estado = 'rechazado'
                    elif respuesta.estado == 'Cancelado':
                        doc.estado = 'cancelado'
                    doc.save()
                    actualizados += 1
            except Exception:
                pass
        
        self.message_user(request, f'{actualizados} documentos actualizados')
    consultar_estado.short_description = 'Consultar estado en SIFEN'
    
    def ver_logs(self, request, queryset):
        """Redirige a los logs del documento."""
        if queryset.count() != 1:
            self.message_user(request, 'Seleccione solo un documento', level='error')
            return
        
        doc = queryset.first()
        url = reverse('admin:django_sifen_api_logsifen_changelist') + f'?documento__id__exact={doc.id}'
        return format_html('<script>window.location.href="{}";</script>', url)
    ver_logs.short_description = 'Ver logs del documento'


@admin.register(LogSIFEN)
class LogSIFENAdmin(admin.ModelAdmin):
    """Admin para logs de SIFEN."""
    
    list_display = [
        'fecha',
        'tipo_operacion',
        'documento_link',
        'codigo_respuesta',
        'exitoso_badge',
        'duracion_ms',
    ]
    list_filter = [
        'tipo_operacion',
        'exitoso',
        'fecha',
    ]
    search_fields = [
        'documento__cdc',
        'codigo_respuesta',
        'mensaje',
    ]
    readonly_fields = [
        'documento',
        'tipo_operacion',
        'request_xml',
        'request_url',
        'response_xml',
        'codigo_respuesta',
        'mensaje',
        'fecha',
        'duracion_ms',
        'exitoso',
    ]
    
    def documento_link(self, obj):
        """Link al documento relacionado."""
        if obj.documento:
            url = reverse('admin:django_sifen_api_documentoelectronico_change', args=[obj.documento.id])
            return format_html('<a href="{}">{}</a>', url, obj.documento.cdc[:15] + '...')
        return '-'
    documento_link.short_description = 'Documento'
    
    def exitoso_badge(self, obj):
        """Badge de éxito/error."""
        if obj.exitoso:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    exitoso_badge.short_description = 'OK'
    
    def has_add_permission(self, request):
        """No permitir agregar logs manualmente."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar logs."""
        return False
