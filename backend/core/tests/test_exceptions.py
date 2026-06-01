from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from authentication.models import User
from etl.models import Patient


class ExceptionHandlerTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin', password='pass123', role='ADMIN',
        )

    def test_404_returns_json(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get('/api/nonexistent/')
        self.assertEqual(resp.status_code, 404)

    def test_validation_error(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(reverse('patient-list'), {
            'nombre': '', 'edad': -1, 'sexo': 'M', 'peso': -1,
            'altura': 1.75, 'presion_sistolica': 120,
            'presion_diastolica': 80, 'glucosa': 90, 'colesterol': 180,
            'frecuencia_cardiaca': 70, 'saturacion_oxigeno': 98,
            'fumador': False,
        }, format='json')
        self.assertEqual(resp.status_code, 400)


class PermissionTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_medico_cannot_train_model(self):
        user = User.objects.create_user(
            username='medico', password='pass123', role='MEDICO',
        )
        self.client.force_authenticate(user=user)
        resp = self.client.post(reverse('ml-model-train'))
        self.assertEqual(resp.status_code, 403)

    def test_analista_cannot_create_patient(self):
        user = User.objects.create_user(
            username='analista', password='pass123', role='ANALISTA',
        )
        self.client.force_authenticate(user=user)
        paciente_url = reverse('patient-list')
        resp = self.client.post(paciente_url, {
            'nombre': 'Test', 'edad': 30, 'sexo': 'M',
            'peso': 70, 'altura': 1.75, 'presion_sistolica': 120,
            'presion_diastolica': 80, 'glucosa': 90, 'colesterol': 180,
            'frecuencia_cardiaca': 70, 'saturacion_oxigeno': 98,
            'fumador': False,
        }, format='json')
        self.assertEqual(resp.status_code, 403)
