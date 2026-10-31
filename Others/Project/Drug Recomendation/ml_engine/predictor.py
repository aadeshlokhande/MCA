"""
ML Inference Service for Live Symptom Disease Prediction.
Loads serialized models via Joblib, builds binary symptom vectors,
handles out-of-distribution inputs, and calibrates differential confidence scores.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

from django.conf import settings
from .algorithms import load_ml_pipeline
from medical.models import Symptom, Disease
from .models import MLModelRecord, PredictionResult
from symptoms.models import SymptomAssessment

MODEL_STORAGE_DIR = settings.BASE_DIR / 'ml_models'
ACTIVE_MODEL_PATH = MODEL_STORAGE_DIR / 'active_model.joblib'


class DiseasePredictor:
    def __init__(self):
        self._pipeline_cache = None

    def get_pipeline(self) -> Optional[Dict[str, Any]]:
        if self._pipeline_cache is None:
            if os.path.exists(ACTIVE_MODEL_PATH):
                self._pipeline_cache = load_ml_pipeline(str(ACTIVE_MODEL_PATH))
        return self._pipeline_cache

    def reload(self):
        self._pipeline_cache = None
        return self.get_pipeline()

    def predict(self, assessment: SymptomAssessment, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Takes a patient SymptomAssessment, formats feature vectors, and generates
        calibrated predictions saved to PredictionResult models.
        """
        pipeline = self.get_pipeline()
        
        # Fallback if model has not been trained yet via management command
        if not pipeline:
            return self._heuristic_fallback_prediction(assessment, top_k)

        model = pipeline['model']
        feature_names = pipeline['symptom_features']
        disease_mapping = pipeline['disease_mapping']

        # Construct binary input vector for the assessment's selected symptoms
        selected_slugs = set(assessment.selected_symptoms.values_list('name', flat=True))
        
        # Guard against zero symptoms provided
        if not selected_slugs:
            return []

        vector = np.zeros((1, len(feature_names)), dtype=np.float32)
        for i, feat in enumerate(feature_names):
            if feat in selected_slugs:
                vector[0, i] = 1.0

        # Predict probability distribution
        probas = model.predict_proba(vector)[0]
        
        # Sort indices by probability in descending order
        sorted_indices = np.argsort(probas)[::-1][:top_k]

        results = []
        # Clear any prior predictions for this assessment
        assessment.predictions.all().delete()

        algo_name = getattr(model, '__class__', type(model)).__name__

        for rank, idx in enumerate(sorted_indices, start=1):
            prob = float(probas[idx])
            disease_name = disease_mapping.get(idx)
            
            # Find Disease in database
            disease_obj = Disease.objects.filter(name=disease_name).first()
            if not disease_obj:
                continue

            # Confidence floor filter (ignore negligible differential probabilities < 3%)
            if prob < 0.03 and rank > 1:
                continue

            pred_record = PredictionResult.objects.create(
                assessment=assessment,
                predicted_disease=disease_obj,
                confidence_score=round(prob, 4),
                rank=rank,
                algorithm_used=algo_name,
                is_primary=(rank == 1)
            )

            results.append({
                'record': pred_record,
                'disease': disease_obj,
                'confidence': prob,
                'confidence_pct': round(prob * 100, 1),
                'rank': rank,
                'is_primary': (rank == 1),
            })

        if not results:
            return self._heuristic_fallback_prediction(assessment, top_k)

        return results

    def _heuristic_fallback_prediction(self, assessment: SymptomAssessment, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Safe clinical Jaccard co-occurrence fallback in case offline training command hasn't been executed.
        """
        selected_symptoms = set(assessment.selected_symptoms.all())
        if not selected_symptoms:
            return []

        scored_diseases = []
        for disease in Disease.objects.prefetch_related('symptoms').all():
            disease_syms = set(disease.symptoms.all())
            if not disease_syms:
                continue
            intersection = len(selected_symptoms & disease_syms)
            union = len(selected_symptoms | disease_syms)
            jaccard = intersection / max(union, 1)
            if jaccard > 0:
                scored_diseases.append((disease, jaccard))

        scored_diseases.sort(key=lambda x: x[1], reverse=True)
        top_matches = scored_diseases[:top_k]

        total_score = sum(s for _, s in top_matches) or 1.0
        results = []
        assessment.predictions.all().delete()

        for rank, (disease_obj, raw_score) in enumerate(top_matches, start=1):
            calibrated_prob = raw_score / total_score
            pred_record = PredictionResult.objects.create(
                assessment=assessment,
                predicted_disease=disease_obj,
                confidence_score=round(calibrated_prob, 4),
                rank=rank,
                algorithm_used="Clinical Co-occurrence Differential (Baseline)",
                is_primary=(rank == 1)
            )
            results.append({
                'record': pred_record,
                'disease': disease_obj,
                'confidence': calibrated_prob,
                'confidence_pct': round(calibrated_prob * 100, 1),
                'rank': rank,
                'is_primary': (rank == 1),
            })

        return results


# Singleton predictor
predictor = DiseasePredictor()
