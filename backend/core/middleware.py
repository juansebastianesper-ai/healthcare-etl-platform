import logging
import traceback
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('healthcare')


class ExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        logger.error(f'Unhandled exception: {str(exception)}')
        logger.error(traceback.format_exc())

        if hasattr(exception, 'status_code'):
            status_code = exception.status_code
        else:
            status_code = 500

        return JsonResponse({
            'error': True,
            'message': str(exception) if status_code < 500 else 'Error interno del servidor',
            'code': getattr(exception, 'code', 'server_error'),
        }, status=status_code)


class ETLLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if '/api/etl/' in request.path:
            logger.info(f'ETL Request: {request.method} {request.path} by {request.user}')

    def process_response(self, request, response):
        if '/api/etl/' in request.path:
            logger.info(f'ETL Response: {response.status_code} for {request.path}')
        return response
