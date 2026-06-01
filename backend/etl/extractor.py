import logging
import pandas as pd
from pathlib import Path
from core.exceptions import ExtractException

logger = logging.getLogger('etl')


class DataExtractor:
    EXTENSIONES_SOPORTADAS = {
        '.csv': 'csv',
        '.xlsx': 'excel',
        '.xls': 'excel',
    }

    def extract(self, file_path):
        ext = Path(file_path).suffix.lower()
        if ext not in self.EXTENSIONES_SOPORTADAS:
            raise ExtractException(f'Formato no soportado: {ext}')

        try:
            logger.info(f'Extrayendo datos desde: {file_path}')
            if ext == '.csv':
                df = pd.read_csv(file_path, encoding='utf-8')
            else:
                df = pd.read_excel(file_path, engine='openpyxl')

            logger.info(f'Datos extraídos: {len(df)} registros, {len(df.columns)} columnas')
            return df

        except FileNotFoundError:
            raise ExtractException(f'Archivo no encontrado: {file_path}')
        except Exception as e:
            raise ExtractException(f'Error al leer el archivo: {str(e)}')

    def get_file_info(self, file_path):
        ext = Path(file_path).suffix.lower()
        return {
            'file_name': Path(file_path).name,
            'extension': ext,
            'size_bytes': Path(file_path).stat().st_size if Path(file_path).exists() else 0,
            'type': self.EXTENSIONES_SOPORTADAS.get(ext, 'unknown'),
        }
