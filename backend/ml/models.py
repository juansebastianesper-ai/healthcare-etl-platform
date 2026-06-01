from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from etl.models import Patient


class MLModel(models.Model):
    nombre = models.CharField(max_length=100, default='Random Forest Classifier')
    version = models.CharField(max_length=20, verbose_name='Versión')
    accuracy = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)], verbose_name='Accuracy')
    precision = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)], verbose_name='Precision')
    recall = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)], verbose_name='Recall')
    f1_score = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)], verbose_name='F1 Score')
    matriz_confusion = models.JSONField(null=True, blank=True, verbose_name='Matriz de Confusión')
    parametros = models.JSONField(null=True, blank=True, verbose_name='Parámetros')
    entrenado_en = models.DateTimeField(auto_now_add=True, verbose_name='Entrenado en')
    activo = models.BooleanField(default=False, verbose_name='Modelo Activo')
    ruta_archivo = models.CharField(max_length=500, blank=True, null=True, verbose_name='Ruta del Modelo')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Modelo ML'
        verbose_name_plural = 'Modelos ML'
        ordering = ['-entrenado_en']

    def __str__(self):
        return f'{self.nombre} v{self.version} (Acc: {self.accuracy:.2%})' if self.accuracy else f'{self.nombre} v{self.version}'


class Prediction(models.Model):
    paciente = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Paciente')
    modelo = models.ForeignKey(MLModel, on_delete=models.SET_NULL, null=True, verbose_name='Modelo')
    prediccion = models.CharField(max_length=10, verbose_name='Predicción')
    probabilidad = models.FloatField(verbose_name='Probabilidad')
    features = models.JSONField(verbose_name='Características')
    fecha_prediccion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Predicción')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Usuario'
    )

    class Meta:
        verbose_name = 'Predicción'
        verbose_name_plural = 'Predicciones'
        ordering = ['-fecha_prediccion']

    def __str__(self):
        return f'Pred {self.id}: {self.paciente.nombre} -> {self.prediccion} ({self.probabilidad:.1%})'
