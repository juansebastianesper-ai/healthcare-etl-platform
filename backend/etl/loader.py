import logging
import pandas as pd
from django.db import transaction
from django.db.models import Q
from .models import Patient
from core.exceptions import LoadException

logger = logging.getLogger('etl')

CAMPOS_ACTUALIZABLES = [
    'peso', 'altura', 'imc', 'imc_clasificacion',
    'presion_sistolica', 'presion_diastolica',
    'glucosa', 'colesterol', 'frecuencia_cardiaca',
    'saturacion_oxigeno', 'fumador', 'diagnostico', 'riesgo',
]


class DataLoader:
    def load(self, df, etl_run=None):
        logger.info(f'Cargando {len(df)} registros a la base de datos')
        creados = 0
        actualizados = 0
        errores = 0

        try:
            existentes = self._get_existentes(df)
            to_create = []
            to_update = []

            for _, row in df.iterrows():
                try:
                    nombre = str(row.get('nombre', '')).strip()
                    edad = int(row['edad']) if pd.notna(row.get('edad')) else 0
                    sexo = str(row.get('sexo', 'O')).strip().upper()
                    clave = (nombre, edad, sexo)

                    paciente = Patient(
                        nombre=nombre,
                        edad=edad,
                        sexo=sexo,
                        peso=float(row['peso']) if pd.notna(row.get('peso')) else 0,
                        altura=float(row['altura']) if pd.notna(row.get('altura')) else 0,
                        imc=float(row['imc']) if pd.notna(row.get('imc')) else None,
                        imc_clasificacion=row.get('imc_clasificacion', None),
                        presion_sistolica=int(row['presion_sistolica']) if pd.notna(row.get('presion_sistolica')) else 0,
                        presion_diastolica=int(row['presion_diastolica']) if pd.notna(row.get('presion_diastolica')) else 0,
                        glucosa=float(row['glucosa']) if pd.notna(row.get('glucosa')) else 0,
                        colesterol=float(row['colesterol']) if pd.notna(row.get('colesterol')) else 0,
                        frecuencia_cardiaca=int(row['frecuencia_cardiaca']) if pd.notna(row.get('frecuencia_cardiaca')) else 0,
                        saturacion_oxigeno=float(row['saturacion_oxigeno']) if pd.notna(row.get('saturacion_oxigeno')) else 0,
                        fumador=bool(row['fumador']) if pd.notna(row.get('fumador')) else False,
                        diagnostico=row.get('diagnostico', ''),
                        riesgo=row.get('riesgo', 'BAJO'),
                    )

                    if clave in existentes:
                        paciente.id = existentes[clave]
                        to_update.append(paciente)
                    else:
                        to_create.append(paciente)

                except Exception as e:
                    errores += 1
                    logger.error(f'Error preparando registro: {str(e)}')

            if to_create:
                creados = self._bulk_create(to_create)

            if to_update:
                actualizados = self._bulk_update(to_update)

        except Exception as e:
            raise LoadException(f'Error en carga masiva: {str(e)}')

        total_ok = creados + actualizados
        if etl_run:
            etl_run.registros_limpios = total_ok
            etl_run.registros_errores = errores
            etl_run.save()

        logger.info(f'Carga completada: {creados} creados, {actualizados} actualizados, {errores} errores')
        return total_ok, errores

    def _get_existentes(self, df):
        combinaciones = set()
        for _, row in df.iterrows():
            nombre = str(row.get('nombre', '')).strip()
            edad = int(row['edad']) if pd.notna(row.get('edad')) else 0
            sexo = str(row.get('sexo', 'O')).strip().upper()
            if nombre:
                combinaciones.add((nombre, edad, sexo))

        if not combinaciones:
            return {}

        query = Q()
        for nombre, edad, sexo in combinaciones:
            query |= Q(nombre=nombre, edad=edad, sexo=sexo)

        existentes = Patient.objects.filter(query).only('id', 'nombre', 'edad', 'sexo')
        return {(p.nombre, p.edad, p.sexo): p.id for p in existentes}

    def _bulk_create(self, pacientes):
        total = 0
        with transaction.atomic():
            for i in range(0, len(pacientes), 500):
                batch = pacientes[i:i + 500]
                try:
                    with transaction.atomic():
                        Patient.objects.bulk_create(batch)
                    total += len(batch)
                except Exception as e:
                    logger.error(f'Error insertando lote {i // 500}: {str(e)}')
        return total

    def _bulk_update(self, pacientes):
        total = 0
        with transaction.atomic():
            for i in range(0, len(pacientes), 500):
                batch = pacientes[i:i + 500]
                try:
                    with transaction.atomic():
                        Patient.objects.bulk_update(batch, CAMPOS_ACTUALIZABLES)
                    total += len(batch)
                except Exception as e:
                    logger.error(f'Error actualizando lote {i // 500}: {str(e)}')
        return total
