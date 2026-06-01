from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from etl.models import Patient
from authentication.models import User


class DashboardAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='medico', password='pass123',
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
            saturacion_oxigeno=95, fumador=True, riesgo='CRITICO',
        )

    def test_dashboard_endpoint(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('dashboard-main'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('kpis', resp.data)
        self.assertEqual(resp.data['kpis']['total_pacientes'], 2)
        self.assertEqual(resp.data['kpis']['pacientes_criticos'], 1)
