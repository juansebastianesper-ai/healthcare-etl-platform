import logging
import json
from datetime import datetime
from .models import ETLRun, ETLSource
from .extractor import DataExtractor
from .transformer import DataTransformer
from .loader import DataLoader
from core.exceptions import ETLException

logger = logging.getLogger('etl')


class ETLEngine:
    def __init__(self):
        self.extractor = DataExtractor()
        self.transformer = DataTransformer()
        self.loader = DataLoader()

    def run(self, file_path, source_name=None, user=None):
        etl_run = ETLRun.objects.create(
            archivo=file_path,
            estado=ETLRun.Estado.PROCESANDO,
            usuario=user,
            fecha_inicio=datetime.now(),
        )

        if source_name:
            source, _ = ETLSource.objects.get_or_create(
                nombre=source_name,
                defaults={'tipo_archivo': file_path.split('.')[-1]}
            )
            etl_run.fuente = source

        logs = []
        try:
            logs.append(f'Iniciando ETL: {file_path}')

            df = self.extractor.extract(file_path)
            logs.append(f'Extracción completada: {len(df)} registros')
            etl_run.registros_procesados = len(df)

            df_transformed, stats = self.transformer.transform(df)
            logs.append(f'Transformación completada: {stats["finales"]} registros limpios')

            cargados, errores = self.loader.load(df_transformed, etl_run)
            logs.append(f'Carga completada: {cargados} registros cargados')

            etl_run.estado = ETLRun.Estado.COMPLETADO
            etl_run.registros_limpios = cargados
            etl_run.registros_errores = errores
            etl_run.log_detalle = '\n'.join(logs)

        except Exception as e:
            etl_run.estado = ETLRun.Estado.ERROR
            logs.append(f'ERROR: {str(e)}')
            etl_run.log_detalle = '\n'.join(logs)
            logger.error(f'ETL falló: {str(e)}')
            raise ETLException(f'Proceso ETL falló: {str(e)}')

        finally:
            etl_run.fecha_fin = datetime.now()
            etl_run.save()

        return etl_run

    def run_from_content(self, df, file_name='memory_upload', source_name=None, user=None):
        etl_run = ETLRun.objects.create(
            archivo=file_name,
            estado=ETLRun.Estado.PROCESANDO,
            usuario=user,
            fecha_inicio=datetime.now(),
        )

        if source_name:
            source, _ = ETLSource.objects.get_or_create(
                nombre=source_name,
                defaults={'tipo_archivo': file_name.split('.')[-1]}
            )
            etl_run.fuente = source

        logs = []
        try:
            logs.append(f'Iniciando ETL desde contenido: {len(df)} registros')
            etl_run.registros_procesados = len(df)

            df_transformed, stats = self.transformer.transform(df)
            logs.append(f'Transformación completada: {stats["finales"]} registros limpios')

            cargados, errores = self.loader.load(df_transformed, etl_run)
            logs.append(f'Carga completada: {cargados} registros cargados')

            etl_run.estado = ETLRun.Estado.COMPLETADO
            etl_run.registros_limpios = cargados
            etl_run.registros_errores = errores
            etl_run.log_detalle = '\n'.join(logs)

        except Exception as e:
            etl_run.estado = ETLRun.Estado.ERROR
            logs.append(f'ERROR: {str(e)}')
            etl_run.log_detalle = '\n'.join(logs)
            logger.error(f'ETL falló: {str(e)}')

        finally:
            etl_run.fecha_fin = datetime.now()
            etl_run.save()

        return etl_run
