from rest_framework import serializers
from .models import Patient, ETLRun, ETLSource


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['id', 'fecha_registro', 'created_at', 'updated_at']


class PatientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'id', 'nombre', 'edad', 'sexo', 'imc', 'imc_clasificacion',
            'riesgo', 'glucosa', 'colesterol', 'fumador', 'fecha_registro'
        ]


class ETLSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ETLSource
        fields = '__all__'


class ETLRunSerializer(serializers.ModelSerializer):
    fuente_nombre = serializers.CharField(source='fuente.nombre', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = ETLRun
        fields = [
            'id', 'archivo', 'fuente', 'fuente_nombre',
            'registros_procesados', 'registros_limpios', 'registros_errores',
            'estado', 'fecha_inicio', 'fecha_fin', 'log_detalle',
            'usuario', 'usuario_nombre', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class ETLRunHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ETLRun
        fields = ['id', 'archivo', 'estado', 'registros_procesados', 'registros_limpios', 'fecha_inicio', 'fecha_fin']
