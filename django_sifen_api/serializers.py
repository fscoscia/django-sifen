"""
Serializers para la API REST de SIFEN.

Convierte entre JSON y objetos Python/Django.
"""

from rest_framework import serializers
from decimal import Decimal
from datetime import datetime, date

from django_sifen_api.models import (
    ConfiguracionSIFEN,
    DocumentoElectronico,
    LogSIFEN,
)
from sifen.models import (
    DocumentoElectronico as SifenDocumento,
    IdentificacionDE,
    DatosGeneralesDE,
    Emisor,
    Receptor,
    Item,
    ActividadEconomica,
)
from sifen.utils import calcular_valor_item, calcular_totales
from sifen.models.totales import CondicionOperacion, Pago


class ActividadEconomicaSerializer(serializers.Serializer):
    """Serializer para actividades económicas."""
    codigo = serializers.CharField(max_length=10, source='cActEco')
    descripcion = serializers.CharField(max_length=200, source='dDesActEco')


class EmisorSerializer(serializers.Serializer):
    """Serializer para datos del emisor."""
    ruc = serializers.CharField(max_length=20)
    dv = serializers.IntegerField()
    nombre = serializers.CharField(max_length=200)
    nombre_fantasia = serializers.CharField(max_length=200, required=False, allow_blank=True)
    direccion = serializers.CharField(max_length=500)
    numero_casa = serializers.IntegerField(required=False, allow_null=True)
    departamento = serializers.IntegerField()
    distrito = serializers.IntegerField()
    ciudad = serializers.IntegerField()
    telefono = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    actividades_economicas = ActividadEconomicaSerializer(many=True)


class ReceptorSerializer(serializers.Serializer):
    """Serializer para datos del receptor."""
    naturaleza = serializers.IntegerField()  # 1=contribuyente, 2=no contribuyente
    tipo_operacion = serializers.IntegerField()  # 1=B2B, 2=B2C, etc.
    ruc = serializers.CharField(max_length=20, required=False, allow_blank=True)
    # D208 (iTipIDRec): obligatorio si naturaleza=2 (no contribuyente).
    # 1=Cédula py, 2=Pasaporte, 3=Cédula extranjera, 4=Carnet de residencia,
    # 5=Innominado (solo B2C), 6=Tarjeta diplomática, 9=Otro.
    tipo_identificacion = serializers.IntegerField(required=False, allow_null=True)
    # D209 (dDTipIDRec): descripción, requerida cuando tipo_identificacion=9 (Otro).
    descripcion_tipo_identificacion = serializers.CharField(
        max_length=200, required=False, allow_blank=True
    )
    nombre = serializers.CharField(max_length=200)
    direccion = serializers.CharField(max_length=500, required=False, allow_blank=True)
    departamento = serializers.IntegerField(required=False, allow_null=True)
    distrito = serializers.IntegerField(required=False, allow_null=True)
    ciudad = serializers.IntegerField(required=False, allow_null=True)
    telefono = serializers.CharField(max_length=20, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)


class ItemSerializer(serializers.Serializer):
    """Serializer para ítems del documento."""
    codigo = serializers.CharField(max_length=50)
    descripcion = serializers.CharField(max_length=500)
    unidad_medida = serializers.IntegerField()
    cantidad = serializers.DecimalField(max_digits=10, decimal_places=4)
    precio_unitario = serializers.DecimalField(max_digits=15, decimal_places=2)
    tasa_iva = serializers.IntegerField()  # 0, 5, 10
    descuento = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        default=Decimal('0')
    )
    observacion = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        default=''
    )


class PagoSerializer(serializers.Serializer):
    """Serializer para formas de pago."""
    tipo_pago = serializers.IntegerField()  # 1=efectivo, 2=cheque, etc.
    monto = serializers.DecimalField(max_digits=15, decimal_places=2)
    moneda = serializers.CharField(max_length=3, default='PYG')


class CrearDocumentoSerializer(serializers.Serializer):
    """
    Serializer para crear un documento electrónico.
    
    Recibe datos en formato JSON y los convierte a DocumentoElectronico.
    """
    
    # Identificación
    tipo_documento = serializers.IntegerField()
    numero_timbrado = serializers.IntegerField()
    establecimiento = serializers.CharField(max_length=3)
    punto_expedicion = serializers.CharField(max_length=3)
    numero_documento = serializers.CharField(max_length=7)
    
    # Datos generales
    fecha_emision = serializers.DateField(required=False, default=date.today)
    tipo_emision = serializers.IntegerField(default=1)  # 1=normal
    codigo_seguridad = serializers.CharField(max_length=9)
    
    # Partes
    emisor = EmisorSerializer()
    receptor = ReceptorSerializer()
    items = ItemSerializer(many=True)
    
    # Condición de operación
    condicion_operacion = serializers.IntegerField()  # 1=contado, 2=crédito
    pagos = PagoSerializer(many=True, required=False)
    
    # Configuración a usar
    configuracion_id = serializers.IntegerField(required=False)
    
    def validate_items(self, value):
        """Valida que haya al menos un ítem."""
        if not value:
            raise serializers.ValidationError("Debe incluir al menos un ítem")
        return value
    
    def validate(self, data):
        """Validaciones cruzadas."""
        # Si es contado, debe tener pagos
        if data['condicion_operacion'] == 1 and not data.get('pagos'):
            raise serializers.ValidationError({
                'pagos': 'Operación al contado debe incluir formas de pago'
            })
        
        return data
    
    def create_sifen_documento(self, validated_data):
        """
        Convierte datos validados a DocumentoElectronico de SIFEN.
        
        Returns:
            DocumentoElectronico listo para enviar.
        """
        # Crear items con cálculos automáticos
        items = []
        for item_data in validated_data['items']:
            valor_item = calcular_valor_item(
                precio_unitario=item_data['precio_unitario'],
                cantidad=item_data['cantidad'],
                tasa_iva=item_data['tasa_iva'],
                descuento=item_data.get('descuento', Decimal('0'))
            )
            
            items.append(Item(
                dCodInt=item_data['codigo'],
                dDesProSer=item_data['descripcion'],
                cUniMed=item_data['unidad_medida'],
                dCantProSer=item_data['cantidad'],
                gValorItem=valor_item,
                dInfItem=item_data.get('observacion') or None,
            ))
        
        # Calcular totales
        totales = calcular_totales(items)
        
        # Crear emisor
        emisor_data = validated_data['emisor']
        emisor = Emisor(
            dRucEm=f"{emisor_data['ruc']}-{emisor_data['dv']}",
            dDVEmi=emisor_data['dv'],
            iTipCont=1,  # Persona jurídica por defecto
            dNomEmi=emisor_data['nombre'],
            dNomFanEmi=emisor_data.get('nombre_fantasia'),
            dDirEmi=emisor_data['direccion'],
            dNumCas=emisor_data.get('numero_casa'),
            cDepEmi=emisor_data['departamento'],
            cDisEmi=emisor_data['distrito'],
            cCiuEmi=emisor_data['ciudad'],
            dTelEmi=emisor_data['telefono'],
            dEmailE=emisor_data['email'],
            gActEco=[
                ActividadEconomica(**act)
                for act in emisor_data['actividades_economicas']
            ],
        )
        
        # Crear receptor
        receptor_data = validated_data['receptor']
        receptor = Receptor(
            iNatRec=receptor_data['naturaleza'],
            iTiOpe=receptor_data['tipo_operacion'],
            iTipIDRec=receptor_data.get('tipo_identificacion'),
            dDTipIDRec=receptor_data.get('descripcion_tipo_identificacion'),
            dNumIDRec=receptor_data.get('ruc'),
            dNomRec=receptor_data['nombre'],
            dDirRec=receptor_data.get('direccion'),
            cDepRec=receptor_data.get('departamento'),
            cDisRec=receptor_data.get('distrito'),
            cCiuRec=receptor_data.get('ciudad'),
            dTelRec=receptor_data.get('telefono'),
            dEmailRec=receptor_data.get('email'),
        )
        
        # Crear condición de operación
        pagos_list = []
        if validated_data.get('pagos'):
            for pago_data in validated_data['pagos']:
                pagos_list.append(Pago(
                    iTiPago=pago_data['tipo_pago'],
                    dMonTiPag=pago_data['monto'],
                    cMoneTiPag=pago_data.get('moneda', 'PYG'),
                ))
        
        condicion = CondicionOperacion(
            iCondOpe=validated_data['condicion_operacion'],
            gPaConEIni=pagos_list,
        )
        
        # Crear documento completo
        documento = SifenDocumento(
            dVerFor=150,
            gTimb=IdentificacionDE(
                iTiDE=validated_data['tipo_documento'],
                dNumTim=validated_data['numero_timbrado'],
                dEst=validated_data['establecimiento'],
                dPunExp=validated_data['punto_expedicion'],
                dNumDoc=validated_data['numero_documento'],
                dFeIniT=datetime.now(),
            ),
            gDatGralOpe=DatosGeneralesDE(
                dFeEmiDE=validated_data.get('fecha_emision', date.today()),
                iTipEmi=validated_data.get('tipo_emision', 1),
                dCodSeg=validated_data['codigo_seguridad'],
            ),
            gEmis=emisor,
            gDatRec=receptor,
            gCamItem=items,
            gTotSub=totales,
            gPaConEIni=condicion,
        )
        
        return documento


class DocumentoElectronicoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo DocumentoElectronico."""
    
    tipo_documento_display = serializers.CharField(
        source='get_tipo_documento_display',
        read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display',
        read_only=True
    )
    
    class Meta:
        model = DocumentoElectronico
        fields = [
            'id',
            'cdc',
            'tipo_documento',
            'tipo_documento_display',
            'numero_documento',
            'numero_timbrado',
            'fecha_emision',
            'fecha_envio',
            'emisor_ruc',
            'emisor_nombre',
            'receptor_ruc',
            'receptor_nombre',
            'total_operacion',
            'total_iva',
            'total_general',
            'estado',
            'estado_display',
            'numero_protocolo',
            'codigo_respuesta',
            'mensaje_respuesta',
            'configuracion',
        ]
        read_only_fields = [
            'id',
            'cdc',
            'fecha_envio',
            'estado',
            'numero_protocolo',
            'codigo_respuesta',
            'mensaje_respuesta',
        ]


class LogSIFENSerializer(serializers.ModelSerializer):
    """Serializer para logs de SIFEN."""
    
    tipo_operacion_display = serializers.CharField(
        source='get_tipo_operacion_display',
        read_only=True
    )
    
    class Meta:
        model = LogSIFEN
        fields = [
            'id',
            'documento',
            'tipo_operacion',
            'tipo_operacion_display',
            'codigo_respuesta',
            'mensaje',
            'fecha',
            'duracion_ms',
            'exitoso',
        ]
        read_only_fields = fields


class ConfiguracionSIFENSerializer(serializers.ModelSerializer):
    """Serializer para configuración SIFEN."""
    
    ambiente_display = serializers.CharField(
        source='get_ambiente_display',
        read_only=True
    )
    
    class Meta:
        model = ConfiguracionSIFEN
        fields = [
            'id',
            'empresa',
            'ruc_empresa',
            'ambiente',
            'ambiente_display',
            'activo',
            'habilitar_nota_tecnica_13',
            'fecha_creacion',
            'fecha_modificacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_modificacion']
