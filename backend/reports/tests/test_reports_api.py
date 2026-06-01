from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from etl.models import Patient
from authentication.models import User


class ReportsAPITest(TestCase):
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

    def test_pdf_report(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('report-pdf', args=['general']))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/pdf')

    def test_csv_report(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('report-csv', args=['pacientes']))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('text/csv', resp['Content-Type'])

    def test_excel_report(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('report-excel', args=['pacientes']))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(
            resp['Content-Type'],
            ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
             'application/vnd.ms-excel']
        )

    def test_reports_unauthenticated(self):
        resp = self.client.get(reverse('report-pdf', args=['general']))
        self.assertEqual(resp.status_code, 401)
