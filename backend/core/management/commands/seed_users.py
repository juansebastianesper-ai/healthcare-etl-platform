from django.core.management.base import BaseCommand
from authentication.models import User

USERS = [
    ('admin', 'admin123', 'ADMIN', True, True),
    ('analista', 'analista123', 'ANALISTA', False, False),
    ('medico', 'medico123', 'MEDICO', False, False),
]


class Command(BaseCommand):
    help = 'Crea usuarios por defecto (admin, analista, medico)'

    def handle(self, *args, **options):
        for username, password, role, is_superuser, is_staff in USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@healthcare.com',
                    'role': role,
                    'is_superuser': is_superuser,
                    'is_staff': is_staff,
                }
            )
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'{username} / {password}  role={role}'))
