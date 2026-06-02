import logging
import csv
import pandas as pd
from io import StringIO
from rest_framework import status, viewsets, generics, parsers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Patient, ETLRun, ETLSource
from .serializers import (
    PatientSerializer, PatientListSerializer, ETLRunSerializer,
    ETLRunHistorySerializer, ETLSourceSerializer
)
from .engine import ETLEngine
from core.exceptions import ETLException
from authentication.permissions import IsAdmin, IsAnalista, IsMedico


def _read_csv(file_obj):
    raw = file_obj.read()
    try:
        content = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        content = raw.decode('latin1')
    dialect = csv.Sniffer().sniff(content[:1024])
    df = pd.read_csv(StringIO(content), sep=dialect.delimiter)
    file_obj.seek(0)
    return df

logger = logging.getLogger('etl')


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    filterset_fields = ['riesgo', 'sexo', 'fumador', 'peso', 'imc_clasificacion']
    search_fields = ['nombre', 'diagnostico']
    ordering_fields = ['edad', 'imc', 'glucosa', 'colesterol', 'fecha_registro']

    def get_serializer_class(self):
        if self.action == 'list':
            return PatientListSerializer
        return PatientSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def criticos(self, request):
        pacientes = self.get_queryset().filter(riesgo='CRITICO')
        page = self.paginate_queryset(pacientes)
        serializer = PatientListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class ETLRunViewSet(viewsets.ModelViewSet):
    queryset = ETLRun.objects.all()
    serializer_class = ETLRunSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['estado', 'fuente']
    ordering = ['-created_at']

    @action(detail=False, methods=['post'], parser_classes=[parsers.MultiPartParser, parsers.FormParser])
    def upload(self, request):
        archivo = request.FILES.get('archivo')
        if not archivo:
            raise ETLException('No se proporcionó archivo')

        try:
            if archivo.name.endswith('.csv'):
                df = _read_csv(archivo)
            elif archivo.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(archivo, engine='openpyxl')
            else:
                raise ETLException('Formato de archivo no soportado. Use CSV o Excel.')

            engine = ETLEngine()
            etl_run = engine.run_from_content(
                df=df,
                file_name=archivo.name,
                source_name=request.data.get('fuente', 'Upload'),
                user=request.user,
            )

            serializer = self.get_serializer(etl_run)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f'Error en ETL upload: {str(e)}')
            raise ETLException(f'Error procesando archivo: {str(e)}')

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        from django.db import transaction, connection
        with transaction.atomic():
            p_count, _ = Patient.objects.all().delete()
            r_count, _ = ETLRun.objects.all().delete()
            s_count, _ = ETLSource.objects.all().delete()
            tables = ['etl_patient', 'etl_etlrun', 'etl_etlsource']
            for table in tables:
                with connection.cursor() as cursor:
                    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
        return Response({
            'message': f'Borrados: {p_count} pacientes, {r_count} ejecuciones, {s_count} fuentes',
        })

    @action(detail=True, methods=['get'])
    def log(self, request, pk=None):
        etl_run = self.get_object()
        return Response({
            'id': etl_run.id,
            'log': etl_run.log_detalle,
        })

    @action(detail=False, methods=['get'])
    def history(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ETLRunHistorySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ETLRunHistorySerializer(queryset, many=True)
        return Response(serializer.data)


class ETLSourceViewSet(viewsets.ModelViewSet):
    queryset = ETLSource.objects.all()
    serializer_class = ETLSourceSerializer
    permission_classes = [IsAnalista]
