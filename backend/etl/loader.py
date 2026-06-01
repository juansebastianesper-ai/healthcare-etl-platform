import logging
import pandas as pd
from django.db import transaction
from .models import Patient
from core.exceptions import LoadException

logger = logging.getLogger('etl')


class DataLoader:
    def load(self, df, etl_run=None):
        logger.info(f'Cargando {len(df)} registros a la base de datos')
        cargados = 0
        errores = 0

        try:
            with transaction.atomic():
                for _, row in df.iterrows():
                    try:
                        Patient.objects.create(
                            nombre=row.get('nombre', ''),
                            edad=int(row['edad']) if pd.notna(row.get('edad')) else 0,
                            sexo=row.get('sexo', 'O'),
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
                        cargados += 1
                    except Exception as e:
                        errores += 1
                        logger.error(f'Error cargando registro: {str(e)}')

        except Exception as e:
            raise LoadException(f'Error en carga masiva: {str(e)}')

        if etl_run:
            etl_run.registros_limpios = cargados
            etl_run.registros_errores = errores
            etl_run.save()

        logger.info(f'Carga completada: {cargados} cargados, {errores} errores')
        return cargados, errores


import pandas as pd
