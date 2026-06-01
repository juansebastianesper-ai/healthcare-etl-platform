from django.contrib import admin
from .models import MLModel, Prediction


@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'version', 'accuracy', 'activo', 'entrenado_en']
    list_filter = ['activo']


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['id', 'paciente', 'prediccion', 'probabilidad', 'fecha_prediccion']
    list_filter = ['prediccion']
