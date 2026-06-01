import logging
import csv
import io
from django.http import HttpResponse
from django.db.models import Count
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from etl.models import Patient, ETLRun
from ml.models import Prediction, MLModel

logger = logging.getLogger('reports')


class ReportService:
    def export_pdf(self, report_type='general'):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(letter),
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        styles = getSampleStyleSheet()
        elements = []
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            alignment=1,
        )

        elements.append(Paragraph('Healthcare ETL Platform - Reporte', title_style))
        elements.append(Spacer(1, 20))

        if report_type == 'pacientes':
            self._build_patients_section(elements, styles)
        elif report_type == 'etl':
            self._build_etl_section(elements, styles)
        elif report_type == 'ml':
            self._build_ml_section(elements, styles)
        else:
            self._build_patients_section(elements, styles)
            elements.append(Spacer(1, 20))
            self._build_etl_section(elements, styles)
            elements.append(Spacer(1, 20))
            self._build_ml_section(elements, styles)

        doc.build(elements)
        buffer.seek(0)
        return buffer

    def _build_patients_section(self, elements, styles):
        elements.append(Paragraph('Pacientes', styles['Heading2']))
        elements.append(Spacer(1, 10))

        total = Patient.objects.count()
        por_riesgo = Patient.objects.values('riesgo').annotate(count=Count('id'))
        por_sexo = Patient.objects.values('sexo').annotate(count=Count('id'))

        elements.append(Paragraph(f'Total de Pacientes: {total}', styles['Normal']))
        elements.append(Paragraph('Distribución por Riesgo:', styles['Normal']))

        data = [['Riesgo', 'Cantidad']]
        for r in por_riesgo:
            data.append([r['riesgo'], str(r['count'])])
        data.append(['TOTAL', str(total)])

        t = Table(data, colWidths=[100, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(t)

    def _build_etl_section(self, elements, styles):
        elements.append(Paragraph('Ejecuciones ETL', styles['Heading2']))
        elements.append(Spacer(1, 10))

        runs = ETLRun.objects.all()[:20]
        elements.append(Paragraph(f'Últimas {len(runs)} ejecuciones:', styles['Normal']))

        data = [['ID', 'Archivo', 'Estado', 'Registros', 'Fecha']]
        for r in runs:
            data.append([
                str(r.id), r.archivo[:30], r.get_estado_display(),
                str(r.registros_limpios),
                r.fecha_inicio.strftime('%Y-%m-%d %H:%M') if r.fecha_inicio else 'N/A'
            ])

        t = Table(data, colWidths=[40, 150, 80, 80, 120])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#198754')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(t)

    def _build_ml_section(self, elements, styles):
        elements.append(Paragraph('Machine Learning', styles['Heading2']))
        elements.append(Spacer(1, 10))

        model = MLModel.objects.filter(activo=True).first()
        if model:
            elements.append(Paragraph(f'Modelo activo: {model.nombre} v{model.version}', styles['Normal']))
            elements.append(Paragraph(f'Accuracy: {model.accuracy:.2%}', styles['Normal']))
            elements.append(Paragraph(f'Precision: {model.precision:.2%}', styles['Normal']))
            elements.append(Paragraph(f'F1 Score: {model.f1_score:.2%}', styles['Normal']))
        else:
            elements.append(Paragraph('No hay modelo activo', styles['Normal']))

        preds = Prediction.objects.count()
        elements.append(Paragraph(f'Predicciones realizadas: {preds}', styles['Normal']))

    def export_csv(self, report_type='pacientes'):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report.csv"'

        writer = csv.writer(response)

        if report_type == 'pacientes':
            writer.writerow(['ID', 'Nombre', 'Edad', 'Sexo', 'IMC', 'Clasif. IMC',
                           'Glucosa', 'Colesterol', 'Riesgo', 'Fumador', 'Fecha'])
            for p in Patient.objects.all():
                writer.writerow([
                    p.id, p.nombre, p.edad, p.get_sexo_display(), p.imc,
                    p.get_imc_clasificacion_display(), p.glucosa, p.colesterol,
                    p.get_riesgo_display(), 'Sí' if p.fumador else 'No',
                    p.fecha_registro.strftime('%Y-%m-%d')
                ])
        elif report_type == 'predicciones':
            writer.writerow(['ID', 'Paciente', 'Predicción', 'Probabilidad', 'Fecha'])
            for p in Prediction.objects.all()[:100]:
                writer.writerow([
                    p.id, p.paciente.nombre if p.paciente else 'N/A',
                    p.prediccion, f'{p.probabilidad:.2%}',
                    p.fecha_prediccion.strftime('%Y-%m-%d %H:%M')
                ])

        return response

    def export_excel(self, report_type='pacientes'):
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = report_type.capitalize()

        if report_type == 'pacientes':
            headers = ['ID', 'Nombre', 'Edad', 'Sexo', 'IMC', 'Clasif. IMC',
                      'Glucosa', 'Colesterol', 'Riesgo', 'Fumador', 'Fecha']
            ws.append(headers)
            for p in Patient.objects.all():
                ws.append([
                    p.id, p.nombre, p.edad, p.get_sexo_display(), p.imc,
                    p.get_imc_clasificacion_display(), p.glucosa, p.colesterol,
                    p.get_riesgo_display(), 'Sí' if p.fumador else 'No',
                    p.fecha_registro.strftime('%Y-%m-%d')
                ])
        elif report_type == 'etl':
            headers = ['ID', 'Archivo', 'Estado', 'Procesados', 'Limpios', 'Errores', 'Fecha']
            ws.append(headers)
            for r in ETLRun.objects.all()[:100]:
                ws.append([
                    r.id, r.archivo, r.get_estado_display(),
                    r.registros_procesados, r.registros_limpios,
                    r.registros_errores,
                    r.fecha_inicio.strftime('%Y-%m-%d %H:%M') if r.fecha_inicio else ''
                ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report.xlsx"'
        wb.save(response)
        return response
