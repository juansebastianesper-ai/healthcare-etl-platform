from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Patient(models.Model):
    class Sexo(models.TextChoices):
        MASCULINO = 'M', 'Masculino'
        FEMENINO = 'F', 'Femenino'
        OTRO = 'O', 'Otro'

    class Riesgo(models.TextChoices):
        BAJO = 'BAJO', 'Bajo'
        MEDIO = 'MEDIO', 'Medio'
        ALTO = 'ALTO', 'Alto'
        CRITICO = 'CRITICO', 'Crítico'

    class IMClasificacion(models.TextChoices):
        BAJO_PESO = 'BAJO_PESO', 'Bajo Peso'
        NORMAL = 'NORMAL', 'Normal'
        SOBREPESO = 'SOBREPESO', 'Sobrepeso'
        OBESIDAD_I = 'OBESIDAD_I', 'Obesidad Grado I'
        OBESIDAD_II = 'OBESIDAD_II', 'Obesidad Grado II'
        OBESIDAD_III = 'OBESIDAD_III', 'Obesidad Grado III'

    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    edad = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(120)], verbose_name='Edad')
    sexo = models.CharField(max_length=1, choices=Sexo.choices, verbose_name='Sexo')
    peso = models.FloatField(validators=[MinValueValidator(0.1), MaxValueValidator(500)], verbose_name='Peso (kg)')
    altura = models.FloatField(validators=[MinValueValidator(0.3), MaxValueValidator(2.5)], verbose_name='Altura (m)')
    imc = models.FloatField(null=True, blank=True, verbose_name='Índice de Masa Corporal')
    imc_clasificacion = models.CharField(
        max_length=20, choices=IMClasificacion.choices,
        null=True, blank=True, verbose_name='Clasificación IMC'
    )
    presion_sistolica = models.IntegerField(validators=[MinValueValidator(30), MaxValueValidator(300)], verbose_name='Presión Sistólica')
    presion_diastolica = models.IntegerField(validators=[MinValueValidator(20), MaxValueValidator(200)], verbose_name='Presión Diastólica')
    glucosa = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1000)], verbose_name='Glucosa (mg/dL)')
    colesterol = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(800)], verbose_name='Colesterol (mg/dL)')
    frecuencia_cardiaca = models.IntegerField(validators=[MinValueValidator(20), MaxValueValidator(300)], verbose_name='Frecuencia Cardíaca')
    saturacion_oxigeno = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Saturación Oxígeno (%)')
    fumador = models.BooleanField(default=False, verbose_name='Fumador')
    consumidor_alcohol = models.BooleanField(default=False, verbose_name='Consumidor de Alcohol')
    actividad_fisica = models.CharField(
        max_length=20,
        choices=[
            ('SEDENTARIO', 'Sedentario'),
            ('MODERADO', 'Moderado'),
            ('ACTIVO', 'Activo'),
            ('INTENSO', 'Intenso'),
        ],
        null=True, blank=True,
        verbose_name='Actividad Física',
    )
    diagnostico = models.TextField(blank=True, null=True, verbose_name='Diagnóstico')
    temperatura = models.FloatField(null=True, blank=True, verbose_name='Temperatura (ºC)')
    antecedentes_familiares = models.TextField(blank=True, null=True, verbose_name='Antecedentes Familiares')
    fecha_consulta = models.DateField(null=True, blank=True, verbose_name='Fecha de Consulta')
    riesgo = models.CharField(
        max_length=10, choices=Riesgo.choices,
        null=True, blank=True, verbose_name='Nivel de Riesgo'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['riesgo']),
            models.Index(fields=['edad']),
            models.Index(fields=['sexo']),
            models.Index(fields=['imc']),
        ]

    def __str__(self):
        return f'{self.nombre} - {self.get_riesgo_display()}'


class ETLSource(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre de la Fuente')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    tipo_archivo = models.CharField(max_length=10, verbose_name='Tipo de Archivo')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Fuente ETL'
        verbose_name_plural = 'Fuentes ETL'

    def __str__(self):
        return self.nombre


class ETLRun(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        PROCESANDO = 'PROCESANDO', 'Procesando'
        COMPLETADO = 'COMPLETADO', 'Completado'
        ERROR = 'ERROR', 'Error'

    archivo = models.CharField(max_length=500, verbose_name='Archivo')
    fuente = models.ForeignKey(
        ETLSource, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Fuente'
    )
    registros_procesados = models.IntegerField(default=0, verbose_name='Registros Procesados')
    registros_limpios = models.IntegerField(default=0, verbose_name='Registros Limpios')
    registros_errores = models.IntegerField(default=0, verbose_name='Registros con Errores')
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.PENDIENTE, verbose_name='Estado')
    fecha_inicio = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Inicio')
    fecha_fin = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Fin')
    log_detalle = models.TextField(blank=True, null=True, verbose_name='Log Detallado')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Usuario'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ejecución ETL'
        verbose_name_plural = 'Ejecuciones ETL'
        ordering = ['-created_at']

    def __str__(self):
        return f'ETL {self.id} - {self.get_estado_display()} - {self.archivo}'
