"""
Signals para la aplicación Django SIFEN.

Maneja eventos automáticos cuando se crean/modifican modelos.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from django_sifen_api.models import DocumentoElectronico, LogSIFEN


@receiver(post_save, sender=DocumentoElectronico)
def documento_creado(sender, instance, created, **kwargs):
    """
    Se ejecuta cuando se crea un documento.
    
    Puede usarse para:
    - Enviar notificaciones
    - Enviar emails
    - Actualizar estadísticas
    - Etc.
    """
    if created:
        # Aquí puedes agregar lógica personalizada
        # Por ejemplo: enviar email de confirmación
        pass


@receiver(pre_save, sender=DocumentoElectronico)
def documento_actualizado(sender, instance, **kwargs):
    """
    Se ejecuta antes de guardar un documento.
    
    Puede usarse para:
    - Validaciones adicionales
    - Auditoría de cambios
    - Etc.
    """
    if instance.pk:
        # El documento ya existe, es una actualización
        try:
            old_instance = DocumentoElectronico.objects.get(pk=instance.pk)
            
            # Detectar cambio de estado
            if old_instance.estado != instance.estado:
                # Aquí puedes agregar lógica cuando cambia el estado
                # Por ejemplo: enviar notificación
                pass
        except DocumentoElectronico.DoesNotExist:
            pass
