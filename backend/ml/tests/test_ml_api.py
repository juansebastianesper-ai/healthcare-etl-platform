from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from etl.models import Patient
from ml.models import MLModel, Prediction
from authentication.models import User
import tempfile, joblib, os
from sklearn.ensemble import RandomForestClassifier
import numpy as np


class MLAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin', password='admin123', role='ADMIN',
        )
        self.user = User.objects.create_user(
            username='medico', password='pass123', role='MEDICO',
        )
        for i in range(15):
            peso = 70 + i
            altura = 1.75
            Patient.objects.create(
                nombre=f'P{i}', edad=30+i, sexo='M' if i % 2 == 0 else 'F',
                peso=peso, altura=altura, imc=round(peso / (altura ** 2), 1),
                presion_sistolica=120+i,
                presion_diastolica=80, glucosa=90+i, colesterol=180+i,
                frecuencia_cardiaca=70, saturacion_oxigeno=98,
                fumador=i % 2 == 0, riesgo='BAJO' if i < 10 else 'ALTO',
            )
        self.tmp_model = tempfile.NamedTemporaryFile(suffix='.joblib', delete=False)
        clf = RandomForestClassifier(n_estimators=10)
        X = np.random.rand(20, 7)
        y = np.random.randint(0, 4, 20)
        clf.fit(X, y)
        joblib.dump(clf, self.tmp_model.name)
        self.tmp_model.close()
        self.model = MLModel.objects.create(
            nombre='Random Forest', version='1.0',
            activo=True, accuracy=0.85,
            ruta_archivo=self.tmp_model.name,
        )

    def tearDown(self):
        os.unlink(self.tmp_model.name)

    def test_list_models(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('ml-model-list'))
        self.assertEqual(resp.status_code, 200)

    def test_active_model(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('ml-model-active'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data['activo'])

    def test_train_model(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(reverse('ml-model-train'))
        self.assertEqual(resp.status_code, 201)
        self.assertIn('model', resp.data)

    def test_train_model_forbidden_medico(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(reverse('ml-model-train'))
        self.assertEqual(resp.status_code, 403)

    def test_predict(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(reverse('prediction-predict'), {
            'edad': 45, 'imc': 24.5,
            'presion_sistolica': 130,
            'glucosa': 110, 'colesterol': 200, 'frecuencia_cardiaca': 72,
            'fumador': False,
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('prediccion', resp.data)

    def test_predict_from_patient(self):
        self.client.force_authenticate(user=self.user)
        paciente = Patient.objects.first()
        resp = self.client.post(reverse('prediction-predict-patient'), {
            'paciente_id': paciente.id,
        }, format='json')
        self.assertEqual(resp.status_code, 200)

    def test_prediction_list(self):
        Prediction.objects.create(
            modelo=self.model, prediccion='BAJO',
            probabilidad=0.9, features={},
        )
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('prediction-list'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('count', resp.data)
        self.assertEqual(resp.data['count'], 1)

    def test_prediction_history_pagination(self):
        for i in range(30):
            Prediction.objects.create(
                modelo=self.model, prediccion='BAJO',
                probabilidad=0.9, features={},
            )
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('prediction-history'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('count', resp.data)
        self.assertEqual(resp.data['count'], 30)
