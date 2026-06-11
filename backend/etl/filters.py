from django.db.models import Q
import django_filters
from .models import Patient

class PatientFilter(django_filters.FilterSet):
    imc_min = django_filters.NumberFilter(field_name='imc', lookup_expr='gte')
    imc_max = django_filters.NumberFilter(field_name='imc', lookup_expr='lte')
    hipertenso = django_filters.BooleanFilter(method='filter_hipertenso')
    diabetico = django_filters.BooleanFilter(method='filter_diabetico')

    def filter_hipertenso(self, queryset, name, value):
        if value:
            return queryset.filter(Q(presion_sistolica__gte=140) | Q(presion_diastolica__gte=90))
        return queryset

    def filter_diabetico(self, queryset, name, value):
        if value:
            return queryset.filter(glucosa__gte=126)
        return queryset

    class Meta:
        model = Patient
        fields = ['riesgo', 'sexo', 'fumador', 'peso', 'imc_clasificacion', 'imc_min', 'imc_max', 'hipertenso', 'diabetico']
