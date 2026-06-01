import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('healthcare')


class HealthcareBaseException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = 'Ha ocurrido un error interno'
    code = 'internal_error'

    def __init__(self, detail=None, code=None):
        if detail:
            self.detail = detail
        if code:
            self.code = code
        super().__init__(self.detail)


class ETLException(HealthcareBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Error en el proceso ETL'
    code = 'etl_error'


class ExtractException(ETLException):
    detail = 'Error al extraer datos'
    code = 'extract_error'


class TransformException(ETLException):
    detail = 'Error al transformar datos'
    code = 'transform_error'


class LoadException(ETLException):
    detail = 'Error al cargar datos'
    code = 'load_error'


class MLException(HealthcareBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Error en el modelo de Machine Learning'
    code = 'ml_error'


class ModelNotTrainedException(MLException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'El modelo no ha sido entrenado aún'
    code = 'model_not_trained'


class InsufficientDataException(MLException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Datos insuficientes para entrenar el modelo'
    code = 'insufficient_data'


class ReportException(HealthcareBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Error al generar el reporte'
    code = 'report_error'


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            'error': True,
            'code': getattr(exc, 'code', 'error'),
            'message': response.data.get('detail', str(exc)),
            'details': response.data,
        }
        return response

    if isinstance(exc, HealthcareBaseException):
        logger.error(f'{exc.code}: {exc.detail}', exc_info=True)
        return Response({
            'error': True,
            'code': exc.code,
            'message': exc.detail,
        }, status=exc.status_code)

    logger.critical(f'Error no manejado: {str(exc)}', exc_info=True)
    return Response({
        'error': True,
        'code': 'unexpected_error',
        'message': 'Ha ocurrido un error inesperado',
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
