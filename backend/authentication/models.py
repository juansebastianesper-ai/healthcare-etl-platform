from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        MEDICO = 'MEDICO', 'Médico'
        ANALISTA = 'ANALISTA', 'Analista'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.ANALISTA,
        verbose_name='Rol',
    )
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name='Teléfono')
    is_active = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'
