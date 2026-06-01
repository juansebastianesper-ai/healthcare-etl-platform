from rest_framework import serializers
from .models import MLModel, Prediction


class MLModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLModel
        fields = '__all__'


class PredictionSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.CharField(source='paciente.nombre', read_only=True)
    modelo_nombre = serializers.CharField(source='modelo.nombre', read_only=True)

    class Meta:
        model = Prediction
        fields = '__all__'


class PredictInputSerializer(serializers.Serializer):
    edad = serializers.FloatField()
    imc = serializers.FloatField()
    glucosa = serializers.FloatField()
    colesterol = serializers.FloatField()
    presion_sistolica = serializers.FloatField()
    frecuencia_cardiaca = serializers.FloatField()
    fumador = serializers.BooleanField()
    paciente_id = serializers.IntegerField(required=False, allow_null=True)
