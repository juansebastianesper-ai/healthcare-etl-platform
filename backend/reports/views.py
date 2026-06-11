import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .services import ReportService
from core.exceptions import ReportException
from authentication.permissions import IsAdminOrMedico

logger = logging.getLogger('healthcare')


@api_view(['GET'])
@permission_classes([IsAdminOrMedico])
def report_pdf(request, report_type='general'):
    try:
        buffer = ReportService().export_pdf(report_type)
        from django.http import HttpResponse
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report.pdf"'
        return response
    except Exception as e:
        raise ReportException(f'Error generando PDF: {str(e)}')


@api_view(['GET'])
@permission_classes([IsAdminOrMedico])
def report_csv(request, report_type='pacientes'):
    try:
        return ReportService().export_csv(report_type)
    except Exception as e:
        raise ReportException(f'Error generando CSV: {str(e)}')


@api_view(['GET'])
@permission_classes([IsAdminOrMedico])
def report_excel(request, report_type='pacientes'):
    try:
        return ReportService().export_excel(report_type)
    except Exception as e:
        raise ReportException(f'Error generando Excel: {str(e)}')
