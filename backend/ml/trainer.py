import logging
import json
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import joblib
from django.conf import settings
from etl.models import Patient
from .models import MLModel
from core.exceptions import InsufficientDataException, MLException

logger = logging.getLogger('ml')


class ModelTrainer:
    FEATURES = ['edad', 'imc', 'glucosa', 'colesterol',
                'presion_sistolica', 'frecuencia_cardiaca', 'fumador']

    def train(self, user=None):
        pacientes = Patient.objects.exclude(
            edad__isnull=True, riesgo__isnull=True
        ).exclude(imc__isnull=True)

        if pacientes.count() < 10:
            raise InsufficientDataException(
                f'Se requieren al menos 10 pacientes. Actuales: {pacientes.count()}'
            )

        logger.info(f'Iniciando entrenamiento con {pacientes.count()} pacientes')

        X, y, le = self._prepare_data(pacientes)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced',
            n_jobs=-1,
        )

        model.fit(X_train, y_train)
        logger.info('Modelo entrenado exitosamente')

        y_pred = model.predict(X_test)
        metrics = self._calculate_metrics(y_test, y_pred)

        model_version = self._get_next_version()
        model_record = self._save_model(model, metrics, model_version, user, le)

        logger.info(f'Modelo v{model_version} guardado. Accuracy: {metrics["accuracy"]:.4f}')
        return model_record, metrics

    def _prepare_data(self, pacientes):
        X = []
        y = []

        for p in pacientes:
            X.append([
                float(p.edad or 0),
                float(p.imc or 0),
                float(p.glucosa or 0),
                float(p.colesterol or 0),
                float(p.presion_sistolica or 0),
                float(p.frecuencia_cardiaca or 0),
                1 if p.fumador else 0,
            ])
            y.append(p.riesgo)

        le = LabelEncoder()
        y_encoded = le.fit_transform(y)

        return np.array(X), y_encoded, le

    def _calculate_metrics(self, y_true, y_pred):
        return {
            'accuracy': float(accuracy_score(y_true, y_pred)),
            'precision': float(precision_score(y_true, y_pred, average='weighted', zero_division=0)),
            'recall': float(recall_score(y_true, y_pred, average='weighted', zero_division=0)),
            'f1_score': float(f1_score(y_true, y_pred, average='weighted', zero_division=0)),
            'confusion_matrix': confusion_matrix(y_true, y_pred).tolist(),
        }

    def _get_next_version(self):
        last = MLModel.objects.order_by('-id').first()
        if last and last.version:
            try:
                return f'1.{int(last.version.split(".")[-1]) + 1}'
            except (ValueError, IndexError):
                return '1.1'
        return '1.0'

    def _save_model(self, model, metrics, version, user, label_encoder=None):
        model_dir = Path(settings.MEDIA_ROOT) / 'models'
        model_dir.mkdir(parents=True, exist_ok=True)
        model_path = model_dir / f'random_forest_v{version}.joblib'
        joblib.dump(model, model_path)

        le_path = model_dir / f'label_encoder_v{version}.joblib'
        joblib.dump(label_encoder or LabelEncoder(), le_path)

        model_record = MLModel.objects.create(
            version=version,
            accuracy=metrics['accuracy'],
            precision=metrics['precision'],
            recall=metrics['recall'],
            f1_score=metrics['f1_score'],
            matriz_confusion=metrics['confusion_matrix'],
            parametros=model.get_params(),
            activo=True,
            ruta_archivo=str(model_path),
        )

        MLModel.objects.exclude(id=model_record.id).update(activo=False)
        return model_record
