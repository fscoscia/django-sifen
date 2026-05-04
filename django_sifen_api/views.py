"""
Views y ViewSets para la API REST de SIFEN.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from django_sifen_api.models import (
    ConfiguracionSIFEN,
    DocumentoElectronico,
    LogSIFEN,
)
from django_sifen_api.serializers import (
    CrearDocumentoSerializer,
    DocumentoElectronicoSerializer,
    LogSIFENSerializer,
    ConfiguracionSIFENSerializer,
)
from sifen import SifenClient, SifenConfig
from sifen.config import TipoAmbiente
from sifen.exceptions import SifenException


class DocumentoElectronicoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de documentos electrónicos.
    
    Endpoints:
    - GET /api/documentos/ - Listar documentos
    - POST /api/documentos/ - Crear y enviar documento
    - GET /api/documentos/{cdc}/ - Obtener documento
    - POST /api/documentos/{cdc}/consultar/ - Consultar estado en SIFEN
    - GET /api/documentos/{cdc}/xml/ - Obtener XML firmado
    """
    
    queryset = DocumentoElectronico.objects.all()
    serializer_class = DocumentoElectronicoSerializer
    lookup_field = 'cdc'
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtra documentos según parámetros."""
        queryset = super().get_queryset()
        
        # Filtrar por estado
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtrar por tipo de documento
        tipo = self.request.query_params.get('tipo_documento')
        if tipo:
            queryset = queryset.filter(tipo_documento=tipo)
        
        # Filtrar por emisor
        emisor_ruc = self.request.query_params.get('emisor_ruc')
        if emisor_ruc:
            queryset = queryset.filter(emisor_ruc=emisor_ruc)
        
        # Filtrar por receptor
        receptor_ruc = self.request.query_params.get('receptor_ruc')
        if receptor_ruc:
            queryset = queryset.filter(receptor_ruc=receptor_ruc)
        
        # Filtrar por rango de fechas
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        if fecha_desde:
            queryset = queryset.filter(fecha_emision__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_emision__lte=fecha_hasta)
        
        return queryset
    
    def create(self, request):
        """
        Crea y envía un documento electrónico a SIFEN.
        
        Request body: Datos del documento en formato JSON
        Response: CDC, estado y mensaje de SIFEN
        """
        # Validar datos
        serializer = CrearDocumentoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Obtener configuración
            config_id = serializer.validated_data.get('configuracion_id')
            if config_id:
                config_model = get_object_or_404(ConfiguracionSIFEN, id=config_id, activo=True)
            else:
                config_model = ConfiguracionSIFEN.objects.filter(activo=True).first()
                if not config_model:
                    return Response(
                        {'error': 'No hay configuración SIFEN activa'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Crear configuración SIFEN
            config = self._build_sifen_config(config_model)
            
            # Convertir a DocumentoElectronico
            documento = serializer.create_sifen_documento(serializer.validated_data)
            
            # Enviar a SIFEN
            client = SifenClient(config)
            respuesta = client.enviar_documento(documento)
            
            # Guardar en base de datos
            doc_model = self._save_documento(documento, respuesta, config_model)
            
            # Retornar respuesta
            return Response({
                'id': doc_model.id,
                'cdc': respuesta.cdc,
                'estado': 'aprobado' if respuesta.aprobado else 'rechazado',
                'codigo': respuesta.codigo,
                'mensaje': respuesta.mensaje,
                'protocolo': respuesta.numero_protocolo,
                'fecha_recepcion': respuesta.fecha_recepcion,
            }, status=status.HTTP_201_CREATED)
            
        except SifenException as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error inesperado: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def consultar(self, request, cdc=None):
        """
        Consulta el estado de un documento en SIFEN.
        
        Response: Estado actual del documento
        """
        documento = self.get_object()
        
        try:
            # Obtener configuración
            config = self._build_sifen_config(documento.configuracion)
            
            # Consultar en SIFEN
            client = SifenClient(config)
            respuesta = client.consultar_documento(cdc)
            
            # Actualizar estado si cambió
            if respuesta.encontrado and respuesta.estado:
                if respuesta.estado == 'Aprobado':
                    documento.estado = 'aprobado'
                elif respuesta.estado == 'Rechazado':
                    documento.estado = 'rechazado'
                elif respuesta.estado == 'Cancelado':
                    documento.estado = 'cancelado'
                documento.save()
            
            return Response({
                'cdc': cdc,
                'encontrado': respuesta.encontrado,
                'estado': respuesta.estado,
                'fecha_aprobacion': respuesta.fecha_aprobacion,
            })
            
        except SifenException as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def xml(self, request, cdc=None):
        """
        Obtiene el XML firmado del documento.
        
        Response: XML firmado
        """
        documento = self.get_object()
        
        return Response({
            'cdc': cdc,
            'xml': documento.xml_firmado,
        })
    
    @action(detail=True, methods=['get'])
    def logs(self, request, cdc=None):
        """
        Obtiene los logs de comunicación con SIFEN para este documento.
        
        Response: Lista de logs
        """
        documento = self.get_object()
        logs = documento.logs.all()
        serializer = LogSIFENSerializer(logs, many=True)
        
        return Response(serializer.data)
    
    def _build_sifen_config(self, config_model: ConfiguracionSIFEN) -> SifenConfig:
        """
        Construye SifenConfig desde el modelo Django.
        
        Args:
            config_model: Modelo de configuración.
        
        Returns:
            SifenConfig configurado.
        """
        return SifenConfig(
            ambiente=TipoAmbiente.DEV if config_model.ambiente == 'dev' else TipoAmbiente.PROD,
            certificado_bytes=bytes(config_model.certificado),
            certificado_contrasena=config_model.certificado_contrasena_encriptada,
            csc=config_model.csc,
            csc_id=config_model.csc_id,
            habilitar_nota_tecnica_13=config_model.habilitar_nota_tecnica_13,
        )
    
    def _save_documento(self, documento, respuesta, config_model):
        """
        Guarda el documento en la base de datos.
        
        Args:
            documento: DocumentoElectronico de SIFEN.
            respuesta: Respuesta de SIFEN.
            config_model: Configuración utilizada.
        
        Returns:
            Modelo DocumentoElectronico guardado.
        """
        from sifen.xml import generate_xml
        from lxml import etree
        from sifen.crypto import sign_xml_element
        
        # Generar XML firmado
        xml_string = generate_xml(documento)
        root = etree.fromstring(xml_string.encode('utf-8'))
        signed_root = sign_xml_element(
            root,
            self._build_sifen_config(config_model),
            documento.Id
        )
        xml_firmado = etree.tostring(signed_root, encoding='unicode')
        
        # Crear modelo
        doc_model = DocumentoElectronico.objects.create(
            cdc=respuesta.cdc or documento.CDC,
            tipo_documento=documento.gTimb.iTiDE,
            numero_documento=f"{documento.gTimb.dEst}-{documento.gTimb.dPunExp}-{documento.gTimb.dNumDoc}",
            numero_timbrado=documento.gTimb.dNumTim,
            fecha_emision=documento.gDatGralOpe.dFeEmiDE,
            emisor_ruc=documento.gEmis.dRucEm,
            emisor_nombre=documento.gEmis.dNomEmi,
            receptor_ruc=documento.gDatRec.dNumIDRec,
            receptor_nombre=documento.gDatRec.dNomRec,
            total_operacion=documento.gTotSub.dTotOpe,
            total_iva=documento.gTotSub.dTotIVA,
            total_general=documento.gTotSub.dTotGralOpe,
            estado='aprobado' if respuesta.aprobado else 'rechazado',
            numero_protocolo=respuesta.numero_protocolo,
            codigo_respuesta=respuesta.codigo,
            mensaje_respuesta=respuesta.mensaje,
            xml_firmado=xml_firmado,
            respuesta_sifen={
                'codigo': respuesta.codigo,
                'mensaje': respuesta.mensaje,
                'cdc': respuesta.cdc,
                'protocolo': respuesta.numero_protocolo,
                'fecha_recepcion': respuesta.fecha_recepcion.isoformat() if respuesta.fecha_recepcion else None,
            },
            configuracion=config_model,
        )
        
        return doc_model


class ConsultaRUCViewSet(viewsets.ViewSet):
    """
    ViewSet para consulta de RUC.
    
    Endpoints:
    - GET /api/consultas/ruc/ - Consultar RUC en SIFEN
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def consultar(self, request):
        """
        Consulta un RUC en SIFEN.
        
        Query params:
        - ruc: RUC sin DV
        - dv: Dígito verificador
        
        Response: Datos del contribuyente
        """
        ruc = request.query_params.get('ruc')
        dv = request.query_params.get('dv')
        
        if not ruc or not dv:
            return Response(
                {'error': 'Parámetros ruc y dv son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Obtener configuración activa
            config_model = ConfiguracionSIFEN.objects.filter(activo=True).first()
            if not config_model:
                return Response(
                    {'error': 'No hay configuración SIFEN activa'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Crear configuración
            config = SifenConfig(
                ambiente=TipoAmbiente.DEV if config_model.ambiente == 'dev' else TipoAmbiente.PROD,
                certificado_bytes=bytes(config_model.certificado),
                certificado_contrasena=config_model.certificado_contrasena_encriptada,
                csc=config_model.csc,
                csc_id=config_model.csc_id,
            )
            
            # Consultar
            client = SifenClient(config)
            respuesta = client.consultar_ruc(ruc, dv)
            
            return Response({
                'encontrado': respuesta.encontrado,
                'contribuyente': {
                    'ruc': respuesta.contribuyente.ruc,
                    'dv': respuesta.contribuyente.dv,
                    'nombre': respuesta.contribuyente.nombre,
                    'tipo': respuesta.contribuyente.tipo_contribuyente,
                    'estado': respuesta.contribuyente.estado,
                } if respuesta.encontrado else None,
                'codigo': respuesta.codigo,
                'mensaje': respuesta.mensaje,
            })
            
        except SifenException as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ValidacionViewSet(viewsets.ViewSet):
    """
    ViewSet para validaciones.
    
    Endpoints:
    - POST /api/validaciones/validar_ruc/ - Validar RUC
    - POST /api/validaciones/calcular_dv/ - Calcular DV de RUC
    - POST /api/validaciones/validar_cdc/ - Validar CDC
    """
    
    @action(detail=False, methods=['post'])
    def validar_ruc(self, request):
        """Valida un RUC."""
        ruc = request.data.get('ruc')
        dv = request.data.get('dv')
        
        if not ruc:
            return Response(
                {'error': 'Parámetro ruc es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        es_valido = SifenClient.validar_ruc(ruc, dv)
        
        return Response({
            'valido': es_valido,
            'ruc': ruc,
            'dv': dv,
            'ruc_formateado': SifenClient.formatear_ruc(ruc, dv) if es_valido and dv else None,
        })
    
    @action(detail=False, methods=['post'])
    def calcular_dv(self, request):
        """Calcula el DV de un RUC."""
        ruc = request.data.get('ruc')
        
        if not ruc:
            return Response(
                {'error': 'Parámetro ruc es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        dv = SifenClient.calcular_dv_ruc(ruc)
        
        return Response({
            'ruc': ruc,
            'dv': dv,
            'ruc_completo': f"{ruc}-{dv}",
        })
    
    @action(detail=False, methods=['post'])
    def validar_cdc(self, request):
        """Valida un CDC."""
        cdc = request.data.get('cdc')
        
        if not cdc:
            return Response(
                {'error': 'Parámetro cdc es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        es_valido = SifenClient.validar_cdc(cdc)
        
        return Response({
            'valido': es_valido,
            'cdc': cdc,
        })


class ConfiguracionSIFENViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de configuraciones SIFEN.
    
    Endpoints:
    - GET /api/configuraciones/ - Listar configuraciones
    - POST /api/configuraciones/ - Crear configuración
    - GET /api/configuraciones/{id}/ - Obtener configuración
    - PUT /api/configuraciones/{id}/ - Actualizar configuración
    - DELETE /api/configuraciones/{id}/ - Eliminar configuración
    """
    
    queryset = ConfiguracionSIFEN.objects.all()
    serializer_class = ConfiguracionSIFENSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Activa una configuración y desactiva las demás."""
        configuracion = self.get_object()
        
        # Desactivar todas las demás
        ConfiguracionSIFEN.objects.exclude(pk=pk).update(activo=False)
        
        # Activar esta
        configuracion.activo = True
        configuracion.save()
        
        return Response({
            'mensaje': f'Configuración {configuracion.empresa} activada'
        })
