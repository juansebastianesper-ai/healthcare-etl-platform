import logging
import numpy as np
import joblib
from pathlib import Path
from django.conf import settings
from .models import MLModel, Prediction
from etl.models import Patient
from core.exceptions import ModelNotTrainedException, MLException

logger = logging.getLogger('ml')


class PredictorService:
    def predict_individual(self, data, user=None):
        model = MLModel.objects.filter(activo=True).first()
        if not model:
            raise ModelNotTrainedException()

        model_path = Path(model.ruta_archivo)
        if not model_path.exists():
            raise ModelNotTrainedException('Archivo del modelo no encontrado')

        clf = joblib.load(model_path)

        features = np.array([[
            float(data.get('edad', 0)),
            float(data.get('imc', 0)),
            float(data.get('glucosa', 0)),
            float(data.get('colesterol', 0)),
            float(data.get('presion_sistolica', 0)),
            float(data.get('frecuencia_cardiaca', 0)),
            1 if data.get('fumador', False) else 0,
        ]])

        prediction_encoded = clf.predict(features)[0]
        probabilities = clf.predict_proba(features)[0]

        riesgo_labels = ['BAJO', 'MEDIO', 'ALTO', 'CRITICO']
        if prediction_encoded < len(riesgo_labels):
            riesgo_pred = riesgo_labels[prediction_encoded]
        else:
            riesgo_pred = 'BAJO'

        prob = float(np.max(probabilities))

        paciente = None
        if data.get('paciente_id'):
            try:
                paciente = Patient.objects.get(id=data['paciente_id'])
            except Patient.DoesNotExist:
                pass

        pred_record = Prediction.objects.create(
            paciente=paciente,
            modelo=model,
            prediccion=riesgo_pred,
            probabilidad=prob,
            features=data,
            usuario=user,
        )

        return {
            'prediccion': riesgo_pred,
            'probabilidad': prob,
            'probabilidades': {
                label: float(probabilities[i])
                for i, label in enumerate(riesgo_labels)
                if i < len(probabilities)
            },
            'id': pred_record.id,
        }

    def predict_batch(self, pacientes_ids, user=None):
        resultados = []
        for pid in pacientes_ids:
            try:
                p = Patient.objects.get(id=pid)
                data = {
                    'paciente_id': p.id,
                    'edad': p.edad,
                    'imc': p.imc,
                    'glucosa': p.glucosa,
                    'colesterol': p.colesterol,
                    'presion_sistolica': p.presion_sistolica,
                    'frecuencia_cardiaca': p.frecuencia_cardiaca,
                    'fumador': p.fumador,
                }
                result = self.predict_individual(data, user)
                result['paciente'] = p.nombre
                resultados.append(result)
            except Patient.DoesNotExist:
                continue

        return resultados

    def predict_from_patient(self, paciente_id, user=None):
        try:
            p = Patient.objects.get(id=paciente_id)
        except Patient.DoesNotExist:
            raise MLException('Paciente no encontrado')

        data = {
            'paciente_id': p.id,
            'edad': p.edad,
            'imc': p.imc,
            'glucosa': p.glucosa,
            'colesterol': p.colesterol,
            'presion_sistolica': p.presion_sistolica,
            'frecuencia_cardiaca': p.frecuencia_cardiaca,
            'fumador': p.fumador,
        }
        return self.predict_individual(data, user)
