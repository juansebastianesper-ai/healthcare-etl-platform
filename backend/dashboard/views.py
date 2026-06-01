import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from analytics.kpis import KPIService
from analytics.services import StatisticsService
from etl.models import ETLRun, Patient
from ml.models import Prediction, MLModel

logger = logging.getLogger('healthcare')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_main(request):
    kpis = KPIService().get_all_kpis()
    stats = StatisticsService().estadisticas_completas()

    ultimo_etl = ETLRun.objects.filter(estado='COMPLETADO').order_by('-fecha_fin').first()
    etl_count = ETLRun.objects.count()
    etl_exitosos = ETLRun.objects.filter(estado='COMPLETADO').count()

    model = MLModel.objects.filter(activo=True).first()
    predictions_count = Prediction.objects.count()

    pacientes_por_edad = StatisticsService().segmentar('edad')

    return Response({
        'kpis': kpis,
        'estadisticas': stats,
        'etl': {
            'total': etl_count,
            'exitosos': etl_exitosos,
            'ultimo_ejecucion': {
                'id': ultimo_etl.id if ultimo_etl else None,
                'archivo': ultimo_etl.archivo if ultimo_etl else None,
                'fecha': ultimo_etl.fecha_fin if ultimo_etl else None,
                'registros': ultimo_etl.registros_limpios if ultimo_etl else 0,
            } if ultimo_etl else None,
        },
        'ml': {
            'modelo_activo': model is not None,
            'modelo_version': model.version if model else None,
            'modelo_accuracy': model.accuracy if model else None,
            'predicciones_totales': predictions_count,
        },
        'segmentacion_edad': pacientes_por_edad,
        'total_pacientes': Patient.objects.count(),
    })
