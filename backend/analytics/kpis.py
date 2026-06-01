import logging
from django.db.models import Avg, Count, Q, StdDev, FloatField
from django.db.models.functions import Cast
from etl.models import Patient

logger = logging.getLogger('healthcare')


class KPIService:
    def get_all_kpis(self):
        total = Patient.objects.count()
        if total == 0:
            return self._empty_kpis()

        return {
            'total_pacientes': total,
            'pacientes_criticos': Patient.objects.filter(riesgo='CRITICO').count(),
            'hipertensos': self._contar_hipertensos(),
            'diabeticos': self._contar_diabeticos(),
            'fumadores': Patient.objects.filter(fumador=True).count(),
            'riesgo_promedio': self._calcular_riesgo_promedio(),
            'distribucion_riesgo': self._distribucion_riesgo(),
            'distribucion_sexo': self._distribucion_sexo(),
            'distribucion_imc': self._distribucion_imc(),
            'edad_promedio': self._edad_promedio(),
            'imc_promedio': self._imc_promedio(),
            'glucosa_promedio': self._glucosa_promedio(),
            'tasa_riesgo_alto': self._tasa_riesgo_alto(),
        }

    def _empty_kpis(self):
        return {
            'total_pacientes': 0, 'pacientes_criticos': 0, 'hipertensos': 0,
            'diabeticos': 0, 'fumadores': 0, 'riesgo_promedio': 0,
            'distribucion_riesgo': {}, 'distribucion_sexo': {},
            'distribucion_imc': {}, 'edad_promedio': 0, 'imc_promedio': 0,
            'glucosa_promedio': 0, 'tasa_riesgo_alto': 0,
        }

    def _contar_hipertensos(self):
        return Patient.objects.filter(
            Q(presion_sistolica__gte=140) | Q(presion_diastolica__gte=90)
        ).count()

    def _contar_diabeticos(self):
        return Patient.objects.filter(glucosa__gte=126).count()

    def _calcular_riesgo_promedio(self):
        pesos = {'BAJO': 1, 'MEDIO': 2, 'ALTO': 3, 'CRITICO': 4}
        total = Patient.objects.count()
        if total == 0:
            return 0
        suma = sum(
            pesos.get(p.riesgo, 0) for p in Patient.objects.only('riesgo')
        )
        return round(suma / total, 2)

    def _distribucion_riesgo(self):
        return dict(Patient.objects.values('riesgo').annotate(
            count=Count('id')
        ).values_list('riesgo', 'count'))

    def _distribucion_sexo(self):
        return dict(Patient.objects.values('sexo').annotate(
            count=Count('id')
        ).values_list('sexo', 'count'))

    def _distribucion_imc(self):
        return dict(Patient.objects.values('imc_clasificacion').annotate(
            count=Count('id')
        ).values_list('imc_clasificacion', 'count'))

    def _edad_promedio(self):
        return Patient.objects.aggregate(avg=Avg('edad'))['avg'] or 0

    def _imc_promedio(self):
        return round(Patient.objects.aggregate(avg=Avg('imc'))['avg'] or 0, 1)

    def _glucosa_promedio(self):
        return round(Patient.objects.aggregate(avg=Avg('glucosa'))['avg'] or 0, 1)

    def _tasa_riesgo_alto(self):
        total = Patient.objects.count()
        if total == 0:
            return 0
        altos = Patient.objects.filter(riesgo__in=['ALTO', 'CRITICO']).count()
        return round((altos / total) * 100, 1)
