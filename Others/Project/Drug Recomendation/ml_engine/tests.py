import os
import tempfile
import numpy as np
from django.test import TestCase
from ml_engine.data import generate_benchmark_dataset, train_test_split
from ml_engine.algorithms import (
    NativeDecisionTree,
    NativeRandomForest,
    NativeNaiveBayes,
    evaluate_model,
    save_ml_pipeline,
    load_ml_pipeline,
)


class MachineLearningPipelineTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Generate small dataset for testing
        cls.X, cls.y, cls.feature_names, cls.disease_names = generate_benchmark_dataset(
            samples_per_disease=25,
            noise_rate=0.04,
            random_state=42
        )
        cls.X_train, cls.X_test, cls.y_train, cls.y_test = train_test_split(
            cls.X, cls.y, test_size=0.2, random_state=42
        )
        cls.n_classes = len(cls.disease_names)

    def test_dataset_generation_properties(self):
        self.assertEqual(len(self.X), 25 * self.n_classes)
        self.assertEqual(self.X.shape[1], len(self.feature_names))
        self.assertEqual(len(np.unique(self.y)), self.n_classes)

    def test_train_test_split_integrity(self):
        # Ensure disjoint train and test sets (no data leakage)
        self.assertEqual(len(self.X_train) + len(self.X_test), len(self.X))
        self.assertEqual(len(self.y_train) + len(self.y_test), len(self.y))
        # Verify all classes present in both splits
        self.assertEqual(len(np.unique(self.y_train)), self.n_classes)
        self.assertEqual(len(np.unique(self.y_test)), self.n_classes)

    def test_decision_tree_classifier(self):
        dt = NativeDecisionTree(max_depth=12)
        dt.fit(self.X_train, self.y_train)
        preds = dt.predict(self.X_test)
        probas = dt.predict_proba(self.X_test)

        self.assertEqual(len(preds), len(self.y_test))
        self.assertEqual(probas.shape, (len(self.y_test), self.n_classes))
        # Probabilities sum to ~1
        np.testing.assert_allclose(np.sum(probas, axis=1), 1.0, atol=1e-5)

        metrics = evaluate_model(self.y_test, preds, self.n_classes)
        self.assertGreater(metrics['accuracy'], 0.70)
        self.assertGreater(metrics['f1'], 0.70)

    def test_random_forest_classifier(self):
        rf = NativeRandomForest(n_estimators=10, max_depth=12)
        rf.fit(self.X_train, self.y_train)
        preds = rf.predict(self.X_test)
        probas = rf.predict_proba(self.X_test)

        self.assertEqual(len(preds), len(self.y_test))
        self.assertEqual(probas.shape, (len(self.y_test), self.n_classes))
        np.testing.assert_allclose(np.sum(probas, axis=1), 1.0, atol=1e-5)

        metrics = evaluate_model(self.y_test, preds, self.n_classes)
        self.assertGreater(metrics['accuracy'], 0.75)
        self.assertGreater(metrics['f1'], 0.75)

    def test_naive_bayes_classifier(self):
        nb = NativeNaiveBayes(alpha=1.0)
        nb.fit(self.X_train, self.y_train)
        preds = nb.predict(self.X_test)
        probas = nb.predict_proba(self.X_test)

        self.assertEqual(len(preds), len(self.y_test))
        self.assertEqual(probas.shape, (len(self.y_test), self.n_classes))
        np.testing.assert_allclose(np.sum(probas, axis=1), 1.0, atol=1e-5)

        metrics = evaluate_model(self.y_test, preds, self.n_classes)
        self.assertGreater(metrics['accuracy'], 0.80)
        self.assertGreater(metrics['f1'], 0.80)

    def test_evaluation_metrics_and_confusion_matrix(self):
        y_true = np.array([0, 1, 2, 0, 1, 2])
        y_pred = np.array([0, 1, 1, 0, 1, 2])
        metrics = evaluate_model(y_true, y_pred, n_classes=3)
        self.assertIn('accuracy', metrics)
        self.assertIn('precision', metrics)
        self.assertIn('recall', metrics)
        self.assertIn('f1', metrics)
        self.assertIn('confusion_matrix', metrics)
        self.assertEqual(len(metrics['confusion_matrix']), 3)

    def test_joblib_pipeline_serialization(self):
        rf = NativeRandomForest(n_estimators=5, max_depth=5)
        rf.fit(self.X_train, self.y_train)

        disease_map = {i: name for i, name in enumerate(self.disease_names)}
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            save_ml_pipeline(rf, self.feature_names, disease_map, tmp_path)
            loaded = load_ml_pipeline(tmp_path)
            self.assertIsNotNone(loaded)
            self.assertEqual(len(loaded['symptom_features']), len(self.feature_names))
            self.assertEqual(loaded['disease_mapping'], disease_map)
            
            # Predict with loaded model
            preds_orig = rf.predict(self.X_test)
            preds_loaded = loaded['model'].predict(self.X_test)
            np.testing.assert_array_equal(preds_orig, preds_loaded)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
