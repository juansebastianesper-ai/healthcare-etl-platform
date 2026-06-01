import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .kpis import KPIService
from .services import StatisticsService

logger = logging.getLogger('healthcare')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def kpis_view(request):
    kpis = KPIService().get_all_kpis()
    return Response(kpis)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estadisticas_view(request):
    campo = request.query_params.get('campo')
    service = StatisticsService()
    if campo:
        return Response(service.calcular_estadisticas(campo))
    return Response(service.estadisticas_completas())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def segmentacion_view(request, criterio):
    try:
        data = StatisticsService().segmentar(criterio)
        return Response(data)
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
