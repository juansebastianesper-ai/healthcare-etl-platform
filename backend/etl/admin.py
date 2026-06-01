from django.contrib import admin
from .models import Patient, ETLRun, ETLSource


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'edad', 'sexo', 'imc', 'riesgo', 'fecha_registro']
    list_filter = ['riesgo', 'sexo', 'imc_clasificacion', 'fumador']
    search_fields = ['nombre', 'diagnostico']
    ordering = ['-fecha_registro']


@admin.register(ETLRun)
class ETLRunAdmin(admin.ModelAdmin):
    list_display = ['id', 'archivo', 'estado', 'registros_procesados', 'registros_limpios', 'fecha_inicio']
    list_filter = ['estado', 'fuente']
    ordering = ['-created_at']


@admin.register(ETLSource)
class ETLSourceAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo_archivo', 'activo']
    list_filter = ['tipo_archivo', 'activo']
