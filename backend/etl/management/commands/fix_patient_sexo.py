from django.core.management.base import BaseCommand
from etl.models import Patient
from etl.transformer import _inferir_sexo_por_nombre


class Command(BaseCommand):
    help = 'Corrige el sexo de pacientes basado en su nombre'

    def handle(self, *args, **options):
        corregidos = 0
        for p in Patient.objects.all().iterator():
            sexo_inferido = _inferir_sexo_por_nombre(p.nombre)
            if sexo_inferido and p.sexo != sexo_inferido:
                p.sexo = sexo_inferido
                p.save(update_fields=['sexo'])
                corregidos += 1
                self.stdout.write(f'  ID {p.id}: {p.nombre} -> {sexo_inferido}')

        self.stdout.write(self.style.SUCCESS(f'Pacientes corregidos: {corregidos}'))
