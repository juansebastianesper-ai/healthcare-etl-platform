import logging
import pandas as pd
import numpy as np
from core.exceptions import TransformException

logger = logging.getLogger('etl')

COLUMNAS_REQUERIDAS = [
    'nombre', 'edad', 'sexo', 'peso', 'altura',
    'presion_sistolica', 'presion_diastolica',
    'glucosa', 'colesterol', 'frecuencia_cardiaca',
    'saturacion_oxigeno', 'fumador'
]

COLUMNAS_NUMERICAS = [
    'edad', 'peso', 'altura', 'presion_sistolica',
    'presion_diastolica', 'glucosa', 'colesterol',
    'frecuencia_cardiaca', 'saturacion_oxigeno'
]

RANGOS_CLINICOS = {
    'presion_sistolica': (70, 220),
    'presion_diastolica': (40, 140),
    'glucosa': (20, 600),
    'colesterol': (50, 500),
    'frecuencia_cardiaca': (30, 220),
    'saturacion_oxigeno': (50, 100),
    'edad': (0, 120),
    'peso': (1, 300),
    'altura': (0.3, 2.5),
}


class DataTransformer:
    def transform(self, df):
        logger.info('Iniciando transformación de datos')
        df = df.copy()
        registros_iniciales = len(df)
        errores = 0

        df = self._normalizar_columnas(df)
        df = self._eliminar_duplicados(df)
        df = self._corregir_tipos(df)
        df = self._limpiar_errores_ortograficos(df)
        df = self._imputar_nulos(df)
        df = self._validar_rangos_clinicos(df)
        df = self._normalizar_variables_categoricas(df)
        df = self._calcular_imc(df)
        df = self._clasificar_imc(df)
        df = self._clasificar_riesgo(df)

        registros_finales = len(df)
        logger.info(f'Transformación completada: {registros_finales} registros limpios')

        return df, {
            'iniciales': registros_iniciales,
            'finales': registros_finales,
            'eliminados': registros_iniciales - registros_finales,
        }

    def _normalizar_columnas(self, df):
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        mapping = {
            'presión_sistólica': 'presion_sistolica',
            'presión_diastólica': 'presion_diastolica',
            'frecuencia_cardíaca': 'frecuencia_cardiaca',
            'saturación_oxígeno': 'saturacion_oxigeno',
            'saturacion_oxigeno': 'saturacion_oxigeno',
            'colesterol_total': 'colesterol',
            'glucosa_en_ayunas': 'glucosa',
        }
        df = df.rename(columns=mapping)
        for col in COLUMNAS_REQUERIDAS:
            if col not in df.columns:
                raise TransformException(f'Columna requerida no encontrada: {col}')
        return df

    def _eliminar_duplicados(self, df):
        antes = len(df)
        df = df.drop_duplicates(subset=['nombre', 'edad', 'sexo'], keep='last')
        despues = len(df)
        if antes > despues:
            logger.info(f'Duplicados eliminados: {antes - despues}')
        return df

    def _corregir_tipos(self, df):
        for col in COLUMNAS_NUMERICAS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df['fumador'] = df['fumador'].map({
            'SI': True, 'si': True, 'Si': True, 'SÍ': True, 'sí': True,
            'YES': True, 'yes': True, 'Yes': True, 'Y': True, '1': True, 1: True, 'true': True, True: True,
            'NO': False, 'no': False, 'No': False, 'N': False, '0': False, 0: False, 'false': False, False: False,
        })
        df['fumador'] = df['fumador'].fillna(False).astype(bool)
        return df

    def _limpiar_errores_ortograficos(self, df):
        if 'sexo' in df.columns:
            df['sexo'] = df['sexo'].str.strip().str.upper()
            df['sexo'] = df['sexo'].replace({
                'HOMBRE': 'M', 'VARON': 'M', 'MASCULINO': 'M', 'M': 'M',
                'MUJER': 'F', 'FEMENINO': 'F', 'FEMENINA': 'F', 'F': 'F',
            })
            df.loc[~df['sexo'].isin(['M', 'F']), 'sexo'] = 'O'

        if 'nombre' in df.columns:
            df['nombre'] = df['nombre'].str.strip().str.title()
            df['nombre'] = df['nombre'].replace(r'\s+', ' ', regex=True)

        return df

    def _imputar_nulos(self, df):
        for col in COLUMNAS_NUMERICAS:
            if col in df.columns:
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    median_val = df[col].median()
                    df[col] = df[col].fillna(median_val)
                    logger.info(f'Nulos imputados en {col}: {null_count} con mediana={median_val:.2f}')
        return df

    def _validar_rangos_clinicos(self, df):
        for col, (min_val, max_val) in RANGOS_CLINICOS.items():
            if col in df.columns:
                fuera_rango = ((df[col] < min_val) | (df[col] > max_val)).sum()
                if fuera_rango > 0:
                    df[col] = df[col].clip(min_val, max_val)
                    logger.info(f'Valores fuera de rango corregidos en {col}: {fuera_rango}')
        return df

    def _normalizar_variables_categoricas(self, df):
        if 'diagnostico' in df.columns:
            df['diagnostico'] = df['diagnostico'].str.strip().str.upper()
        return df

    def _calcular_imc(self, df):
        df['imc'] = np.where(
            (df['peso'] > 0) & (df['altura'] > 0),
            df['peso'] / (df['altura'] ** 2),
            np.nan
        )
        df['imc'] = df['imc'].round(1)
        logger.info(f'IMC calculado para {df["imc"].notna().sum()} pacientes')
        return df

    def _clasificar_imc(self, df):
        condiciones = [
            df['imc'] < 18.5,
            (df['imc'] >= 18.5) & (df['imc'] < 25),
            (df['imc'] >= 25) & (df['imc'] < 30),
            (df['imc'] >= 30) & (df['imc'] < 35),
            (df['imc'] >= 35) & (df['imc'] < 40),
            df['imc'] >= 40,
        ]
        clasificaciones = [
            'BAJO_PESO', 'NORMAL', 'SOBREPESO',
            'OBESIDAD_I', 'OBESIDAD_II', 'OBESIDAD_III'
        ]
        df['imc_clasificacion'] = np.select(condiciones, clasificaciones, default='NORMAL')
        return df

    def _clasificar_riesgo(self, df):
        condiciones = [
            (df['presion_sistolica'] > 180) | (df['glucosa'] > 300) | (df['saturacion_oxigeno'] < 85),
            (df['presion_sistolica'] > 160) | (df['glucosa'] > 250) | (df['colesterol'] > 300) | (df['imc'] >= 35),
            (df['presion_sistolica'] > 140) | (df['glucosa'] > 200) | (df['colesterol'] > 240) | (df['fumador'] == True) | (df['imc'] >= 30),
        ]
        riesgos = ['CRITICO', 'ALTO', 'MEDIO']
        df['riesgo'] = np.select(condiciones, riesgos, default='BAJO')
        logger.info(f'Riesgo clasificado: {df["riesgo"].value_counts().to_dict()}')
        return df
