import logging
import numpy as np
from collections import Counter
from django.db import models
from django.db.models import Avg
from etl.models import Patient

logger = logging.getLogger('healthcare')


class StatisticsService:
    def calcular_estadisticas(self, campo):
        valores = Patient.objects.filter(
            **{f'{campo}__isnull': False}
        ).values_list(campo, flat=True)

        valores_list = [float(v) for v in valores if v is not None]

        if not valores_list:
            return {
                'campo': campo,
                'media': 0, 'mediana': 0, 'moda': 0,
                'desviacion_std': 0, 'minimo': 0, 'maximo': 0,
                'q1': 0, 'q3': 0, 'count': 0,
            }

        arr = np.array(valores_list)
        counts = Counter(valores_list)
        moda_val = counts.most_common(1)[0][0] if counts else 0

        return {
            'campo': campo,
            'media': round(float(np.mean(arr)), 2),
            'mediana': round(float(np.median(arr)), 2),
            'moda': round(float(moda_val), 2),
            'desviacion_std': round(float(np.std(arr, ddof=1)), 2),
            'minimo': round(float(np.min(arr)), 2),
            'maximo': round(float(np.max(arr)), 2),
            'q1': round(float(np.percentile(arr, 25)), 2),
            'q3': round(float(np.percentile(arr, 75)), 2),
            'count': int(len(arr)),
        }

    def estadisticas_completas(self):
        campos = ['edad', 'imc', 'glucosa', 'colesterol',
                  'presion_sistolica', 'presion_diastolica',
                  'frecuencia_cardiaca', 'saturacion_oxigeno']
        return {c: self.calcular_estadisticas(c) for c in campos}

    def segmentar(self, criterio):
        segmentaciones = {
            'edad': lambda: self._segmentar_edad(),
            'sexo': lambda: self._segmentar_sexo(),
            'riesgo': lambda: self._segmentar_riesgo(),
            'imc': lambda: self._segmentar_imc(),
            'diagnostico': lambda: self._segmentar_diagnostico(),
        }
        func = segmentaciones.get(criterio)
        if not func:
            raise ValueError(f'Criterio de segmentación no válido: {criterio}')
        return func()

    def _segmentar_edad(self):
        rangos = [
            (0, 18, '0-18'), (19, 30, '19-30'), (31, 45, '31-45'),
            (46, 60, '46-60'), (61, 100, '61+'),
        ]
        resultado = {}
        for min_e, max_e, label in rangos:
            qs = Patient.objects.filter(edad__gte=min_e, edad__lte=max_e)
            resultado[label] = {
                'total': qs.count(),
                'criticos': qs.filter(riesgo='CRITICO').count(),
                'edad_promedio': qs.aggregate(avg=Avg('edad'))['avg'] or 0,
            }
        return resultado

    def _segmentar_sexo(self):
        return {
            sexo: {
                'total': Patient.objects.filter(sexo=sexo).count(),
                'edad_promedio': Patient.objects.filter(sexo=sexo).aggregate(
                    avg=Avg('edad')
                )['avg'] or 0,
            }
            for sexo in ['M', 'F']
        }

    def _segmentar_riesgo(self):
        return {
            riesgo: Patient.objects.filter(riesgo=riesgo).count()
            for riesgo in ['BAJO', 'MEDIO', 'ALTO', 'CRITICO']
        }

    def _segmentar_imc(self):
        return {
            clasif: Patient.objects.filter(imc_clasificacion=clasif).count()
            for clasif in ['BAJO_PESO', 'NORMAL', 'SOBREPESO',
                           'OBESIDAD_I', 'OBESIDAD_II', 'OBESIDAD_III']
        }

    def _segmentar_diagnostico(self):
        resultados = Patient.objects.values('diagnostico').annotate(
            total=models.Count('id')
        ).order_by('-total')[:10]
        return {r['diagnostico'] or 'SIN DIAGNÓSTICO': r['total'] for r in resultados}
