import logging
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import MLModel, Prediction
from .serializers import MLModelSerializer, PredictionSerializer, PredictInputSerializer
from .trainer import ModelTrainer
from .predictor import PredictorService
from authentication.permissions import IsAdmin, IsAnalista, IsMedico
from core.exceptions import MLException

logger = logging.getLogger('ml')


class MLModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MLModel.objects.all()
    serializer_class = MLModelSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['activo']
    ordering = ['-entrenado_en']

    @action(detail=False, methods=['post'], permission_classes=[IsAnalista])
    def train(self, request):
        try:
            trainer = ModelTrainer()
            model, metrics = trainer.train(user=request.user)
            return Response({
                'message': 'Modelo entrenado exitosamente',
                'model': MLModelSerializer(model).data,
                'metrics': metrics,
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            raise MLException(str(e))

    @action(detail=False, methods=['get'])
    def active(self, request):
        model = MLModel.objects.filter(activo=True).first()
        if not model:
            return Response({'message': 'No hay modelo activo'}, status=status.HTTP_404_NOT_FOUND)
        return Response(MLModelSerializer(model).data)


class PredictionViewSet(viewsets.GenericViewSet):
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    permission_classes = [IsAnalista]

    def get_permissions(self):
        if self.action in ['predict', 'predict_patient']:
            return [IsAuthenticated()]
        return super().get_permissions()

    def list(self, request):
        predictions = self.get_queryset()
        page = self.paginate_queryset(predictions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def predict(self, request):
        serializer = PredictInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = PredictorService()
        result = service.predict_individual(serializer.validated_data, user=request.user)
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def predict_patient(self, request):
        paciente_id = request.data.get('paciente_id')
        if not paciente_id:
            raise MLException('Se requiere paciente_id')
        service = PredictorService()
        result = service.predict_from_patient(paciente_id, user=request.user)
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def history(self, request):
        predictions = self.get_queryset().select_related('paciente', 'modelo')
        page = self.paginate_queryset(predictions)
        if page is not None:
            data = [{
                'id': p.id,
                'paciente': p.paciente.nombre if p.paciente else 'N/A',
                'prediccion': p.prediccion,
                'probabilidad': p.probabilidad,
                'fecha': p.fecha_prediccion,
            } for p in page]
            return self.get_paginated_response(data)
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'], permission_classes=[IsAdmin])
    def delete_history(self, request):
        from django.db import connection
        count, _ = Prediction.objects.all().delete()
        engine = connection.vendor
        with connection.cursor() as cursor:
            if engine == 'sqlite':
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='ml_prediction'")
            elif engine == 'postgresql':
                cursor.execute("ALTER SEQUENCE ml_prediction_id_seq RESTART WITH 1")
        return Response({'message': f'Historial borrado: {count} predicciones eliminadas'})
