from django.test import TestCase
from etl.transformer import DataTransformer as transformer
import pandas as pd


class DataTransformerTest(TestCase):
    def setUp(self):
        self.transformer = transformer()
        self.valid_df = pd.DataFrame([{
            'nombre': 'Juan Perez', 'edad': 45, 'sexo': 'M',
            'peso': 75.0, 'altura': 1.75, 'presion_sistolica': 120,
            'presion_diastolica': 80, 'glucosa': 100, 'colesterol': 200,
            'frecuencia_cardiaca': 70, 'saturacion_oxigeno': 98,
            'fumador': 'No', 'diagnostico': 'Control',
        }])

    def test_transform_valid_data(self):
        result_df, stats = self.transformer.transform(self.valid_df)
        self.assertIsNotNone(result_df)
        self.assertFalse(result_df.empty)
        self.assertIn('imc', result_df.columns)
        self.assertIn('imc_clasificacion', result_df.columns)
        self.assertIn('riesgo', result_df.columns)

    def test_imc_calculation(self):
        result_df, _ = self.transformer.transform(self.valid_df)
        imc = result_df.iloc[0]['imc']
        self.assertAlmostEqual(imc, 75.0 / (1.75 ** 2), places=1)

    def test_imc_classification(self):
        df = pd.DataFrame([{
            'nombre': 'Obeso', 'edad': 30, 'sexo': 'M',
            'peso': 120.0, 'altura': 1.70, 'presion_sistolica': 120,
            'presion_diastolica': 80, 'glucosa': 100, 'colesterol': 200,
            'frecuencia_cardiaca': 70, 'saturacion_oxigeno': 98,
            'fumador': 'No', 'diagnostico': 'Obesidad',
        }])
        result_df, _ = self.transformer.transform(df)
        imc = result_df.iloc[0]['imc']
        if imc >= 40:
            self.assertEqual(result_df.iloc[0]['imc_clasificacion'], 'OBESIDAD_III')

    def test_riesgo_critico(self):
        df = pd.DataFrame([{
            'nombre': 'Critico', 'edad': 60, 'sexo': 'M',
            'peso': 80.0, 'altura': 1.70, 'presion_sistolica': 190,
            'presion_diastolica': 100, 'glucosa': 350, 'colesterol': 250,
            'frecuencia_cardiaca': 90, 'saturacion_oxigeno': 80,
            'fumador': 'Si', 'diagnostico': 'Emergencia',
        }])
        result_df, _ = self.transformer.transform(df)
        self.assertEqual(result_df.iloc[0]['riesgo'], 'CRITICO')

    def test_corregir_sexo_por_nombre_con_nombre_completo(self):
        df = pd.DataFrame([{
            'nombre': 'De Jesus Perez', 'edad': 35, 'sexo': 'O',
            'peso': 72.0, 'altura': 1.70, 'presion_sistolica': 120,
            'presion_diastolica': 80, 'glucosa': 100, 'colesterol': 200,
            'frecuencia_cardiaca': 70, 'saturacion_oxigeno': 98,
            'fumador': 'No', 'diagnostico': 'Control',
        }])

        result_df, _ = self.transformer.transform(df)

        self.assertEqual(result_df.iloc[0]['sexo'], 'M')

    def test_handles_null_values(self):
        df = pd.DataFrame([{
            'nombre': 'Null Test', 'edad': None, 'sexo': None,
            'peso': None, 'altura': None, 'presion_sistolica': None,
            'presion_diastolica': None, 'glucosa': None, 'colesterol': None,
            'frecuencia_cardiaca': None, 'saturacion_oxigeno': None,
            'fumador': None, 'diagnostico': None,
        }])
        result_df, _ = self.transformer.transform(df)
        self.assertIsNotNone(result_df)
