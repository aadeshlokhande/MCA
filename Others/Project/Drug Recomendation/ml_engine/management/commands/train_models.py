"""
Django management command to execute the Machine Learning Training & Evaluation Pipeline.
Trains and compares:
1. Decision Tree Classifier
2. Random Forest Classifier
3. Naive Bayes Classifier
Calculates Accuracy, Precision, Recall, F1-Score, and Confusion Matrix.
Stores training metrics in MLModelRecord and serializes the active model using Joblib.
"""

import json
from django.core.management.base import BaseCommand
from django.conf import settings
from ml_engine.data import generate_benchmark_dataset, train_test_split
from ml_engine.algorithms import (
    get_classifier,
    evaluate_model,
    save_ml_pipeline,
)
from ml_engine.models import MLModelRecord, DatasetRecord
from ml_engine.predictor import ACTIVE_MODEL_PATH, predictor
from audit.models import AuditLog, log_audit_event


class Command(BaseCommand):
    help = "Trains, compares, and evaluates Decision Tree, Random Forest, and Naive Bayes models"

    def add_arguments(self, parser):
        parser.add_argument(
            '--samples-per-disease',
            type=int,
            default=150,
            help="Number of probabilistic clinical symptom samples per disease"
        )
        parser.add_argument(
            '--test-size',
            type=float,
            default=0.20,
            help="Fraction of data held out for testing without data leakage"
        )

    def handle(self, *args, **options):
        samples_per_disease = options['samples_per_disease']
        test_size = options['test_size']

        self.stdout.write(self.style.NOTICE("Generating benchmark clinical symptom matrix..."))
        X, y, feature_names, disease_names = generate_benchmark_dataset(
            samples_per_disease=samples_per_disease,
            noise_rate=0.06,
            random_state=42
        )

        n_samples, n_features = X.shape
        n_classes = len(disease_names)
        self.stdout.write(f"Dataset generated: {n_samples} samples, {n_features} features, {n_classes} target diseases.")

        # Record dataset provenance
        dataset_rec, _ = DatasetRecord.objects.update_or_create(
            name="Clinical Symptom-Disease Differential Benchmark v1.0",
            defaults={
                'source': "Curated Medical Benchmark grounding WHO/ICD-10 clinical profiles",
                'num_records': n_samples,
                'num_symptoms': n_features,
                'num_diseases': n_classes,
                'is_validated': True,
                'description': f"Probabilistic multi-class clinical symptom co-occurrence matrix with {n_classes} diseases."
            }
        )

        # Train-test split (stratified, zero data leakage)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        self.stdout.write(f"Train split: {len(y_train)} samples | Test split: {len(y_test)} samples.")

        algorithms = [
            ('DECISION_TREE', 'Decision Tree Classifier'),
            ('NAIVE_BAYES', 'Multinomial Naive Bayes'),
            ('RANDOM_FOREST', 'Random Forest Classifier (Ensemble)'),
        ]

        evaluated_models = []
        disease_mapping = {i: name for i, name in enumerate(disease_names)}

        self.stdout.write(self.style.NOTICE("\nTraining and evaluating models..."))
        self.stdout.write("-" * 75)
        self.stdout.write(f"{'Algorithm':<35} | {'Accuracy':<10} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10}")
        self.stdout.write("-" * 75)

        for algo_key, display_name in algorithms:
            clf = get_classifier(algo_key)
            clf.fit(X_train, y_train)

            # Evaluate strictly on un-seen test split to prevent data leakage
            y_pred = clf.predict(X_test)
            metrics = evaluate_model(y_test, y_pred, n_classes=n_classes)

            # Store metrics in database
            model_rec = MLModelRecord.objects.create(
                name=display_name,
                algorithm=algo_key,
                version='1.0.0',
                is_active=False,
                accuracy=metrics['accuracy'],
                precision_score=metrics['precision'],
                recall_score=metrics['recall'],
                f1_score=metrics['f1'],
                confusion_matrix_json=json.dumps(metrics['confusion_matrix']),
                training_samples_count=len(y_train),
                features_count=n_features,
                notes=f"Trained on {len(y_train)} samples, evaluated on {len(y_test)} held-out test samples."
            )

            evaluated_models.append((algo_key, clf, metrics, model_rec))

            self.stdout.write(
                f"{display_name:<35} | "
                f"{metrics['accuracy']*100:>8.2f}% | "
                f"{metrics['precision']*100:>8.2f}% | "
                f"{metrics['recall']*100:>8.2f}% | "
                f"{metrics['f1']*100:>8.2f}%"
            )

        self.stdout.write("-" * 75)

        # Select best model (typically Random Forest) and activate it
        best_algo, best_clf, best_metrics, best_rec = max(evaluated_models, key=lambda x: x[2]['f1'])
        
        # Mark active in DB
        MLModelRecord.objects.filter(is_active=True).update(is_active=False)
        best_rec.is_active = True
        best_rec.save()

        # Save active pipeline to Joblib file
        save_ml_pipeline(
            model=best_clf,
            symptom_names=feature_names,
            disease_mapping=disease_mapping,
            filepath=str(ACTIVE_MODEL_PATH)
        )

        # Refresh inference engine
        predictor.reload()

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSelected Active Production Model: {best_rec.name} (F1: {best_metrics['f1']*100:.2f}%)"
            )
        )
        self.stdout.write(self.style.SUCCESS(f"Saved serialized Joblib pipeline to: {ACTIVE_MODEL_PATH}"))

        # Log audit trail
        log_audit_event(
            request=None,
            action=AuditLog.Action.MODEL_TRAINED,
            details=f"Trained 3 models. Active model set to {best_rec.name} (Acc: {best_metrics['accuracy']*100:.2f}%, F1: {best_metrics['f1']*100:.2f}%)."
        )
