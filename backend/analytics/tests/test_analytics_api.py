from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from etl.models import Patient
from authentication.models import User


class AnalyticsAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='analista', password='pass123',
        )
        Patient.objects.create(
            nombre='P1', edad=30, sexo='M', peso=70, altura=1.75,
            imc=22.9, presion_sistolica=120, presion_diastolica=80,
            glucosa=90, colesterol=180, frecuencia_cardiaca=70,
            saturacion_oxigeno=98, fumador=False, riesgo='BAJO',
        )
        Patient.objects.create(
            nombre='P2', edad=60, sexo='F', peso=80, altura=1.65,
            imc=29.4, presion_sistolica=140, presion_diastolica=90,
            glucosa=130, colesterol=220, frecuencia_cardiaca=75,
            saturacion_oxigeno=95, fumador=True, riesgo='ALTO',
        )

    def test_kpis(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('analytics-kpis'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('total_pacientes', resp.data)
        self.assertEqual(resp.data['total_pacientes'], 2)

    def test_estadisticas(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('analytics-estadisticas'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('edad', resp.data)

    def test_segmentacion_riesgo(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(
            reverse('analytics-segmentacion', args=['riesgo'])
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn('BAJO', resp.data)
        self.assertIn('ALTO', resp.data)
