from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from etl.models import Patient, ETLRun, ETLSource
from authentication.models import User
import json


class ETLAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin', password='admin123', role='ADMIN',
        )
        self.user = User.objects.create_user(
            username='medico', password='pass123', role='MEDICO',
        )
        self.patient = Patient.objects.create(
            nombre='Test Paciente', edad=45, sexo='M',
            peso=75.0, altura=1.75, imc=24.5, presion_sistolica=120,
            presion_diastolica=80, glucosa=100, colesterol=200,
            frecuencia_cardiaca=70, saturacion_oxigeno=98,
            fumador=False, riesgo='BAJO',
        )
        self.source = ETLSource.objects.create(
            nombre='Test Source', tipo_archivo='CSV',
        )

    def test_list_patients(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('patient-list'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)

    def test_retrieve_patient(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('patient-detail', args=[self.patient.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['nombre'], 'Test Paciente')

    def test_create_patient_admin(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(reverse('patient-list'), {
            'nombre': 'New Patient', 'edad': 30, 'sexo': 'F',
            'peso': 60.0, 'altura': 1.65, 'presion_sistolica': 110,
            'presion_diastolica': 70, 'glucosa': 90, 'colesterol': 180,
            'frecuencia_cardiaca': 72, 'saturacion_oxigeno': 97,
            'fumador': False,
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Patient.objects.count(), 2)

    def test_create_patient_medico_forbidden(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(reverse('patient-list'), {
            'nombre': 'New Patient', 'edad': 30, 'sexo': 'F',
            'peso': 60.0, 'altura': 1.65, 'presion_sistolica': 110,
            'presion_diastolica': 70, 'glucosa': 90, 'colesterol': 180,
            'frecuencia_cardiaca': 72, 'saturacion_oxigeno': 97,
            'fumador': False,
        }, format='json')
        self.assertEqual(resp.status_code, 403)

    def test_criticos_endpoint(self):
        Patient.objects.create(
            nombre='Critico', edad=70, sexo='M',
            peso=80.0, altura=1.70, imc=27.7, presion_sistolica=180,
            presion_diastolica=100, glucosa=350, colesterol=250,
            frecuencia_cardiaca=90, saturacion_oxigeno=82,
            fumador=True, riesgo='CRITICO',
        )
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('patient-criticos'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_patients_by_riesgo(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(f"{reverse('patient-list')}?riesgo=BAJO")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)

    def test_etl_run_list(self):
        ETLRun.objects.create(
            archivo='test.csv', fuente=self.source,
            estado='COMPLETADO', registros_procesados=10,
        )
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('etl-run-list'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)

    def test_etl_history_pagination(self):
        for i in range(30):
            ETLRun.objects.create(
                archivo=f'test{i}.csv', fuente=self.source,
                estado='COMPLETADO', registros_procesados=1,
            )
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('etl-run-history'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('count', resp.data)
        self.assertEqual(resp.data['count'], 30)
        self.assertLessEqual(len(resp.data['results']), 25)
