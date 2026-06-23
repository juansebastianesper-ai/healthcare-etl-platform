from django.core.management.base import BaseCommand
from etl.models import Patient
from etl.transformer import DataTransformer
import pandas as pd
import os


class Command(BaseCommand):
    help = 'Backfill diagnostico from sample CSV for matching patients'

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=str, help='CSV con datos para backfill')

    def handle(self, *args, **options):
        csv_path = options.get('csv') or os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'sample_patients.csv'
        )
        csv_path = os.path.abspath(csv_path)

        if not os.path.exists(csv_path):
            self.stdout.write(self.style.WARNING(f'Archivo no encontrado: {csv_path}'))
            return

        df = pd.read_csv(csv_path)
        transformer = DataTransformer()
        df, _ = transformer.transform(df)

        actualizados = 0
        for _, row in df.iterrows():
            nombre = str(row.get('nombre', '')).strip()
            edad = int(row['edad']) if pd.notna(row.get('edad')) else None
            sexo = str(row.get('sexo', '')).strip().upper()
            diagnostico = row.get('diagnostico', '')
            if not nombre or not edad or not sexo or not diagnostico:
                continue
            paciente = Patient.objects.filter(
                nombre=nombre, edad=edad, sexo=sexo
            ).first()
            if paciente and not paciente.diagnostico:
                paciente.diagnostico = diagnostico
                paciente.save(update_fields=['diagnostico'])
                actualizados += 1

        self.stdout.write(self.style.SUCCESS(f'Diagn\u00f3stico backfilled: {actualizados} pacientes'))
