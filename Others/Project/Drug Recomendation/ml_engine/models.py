from django.db import models
from symptoms.models import SymptomAssessment
from medical.models import Disease


class MLModelRecord(models.Model):
    ALGORITHM_CHOICES = (
        ('RANDOM_FOREST', 'Random Forest Classifier'),
        ('DECISION_TREE', 'Decision Tree Classifier'),
        ('NAIVE_BAYES', 'Multinomial / Gaussian Naive Bayes'),
    )

    name = models.CharField(max_length=120)
    algorithm = models.CharField(max_length=30, choices=ALGORITHM_CHOICES, default='RANDOM_FOREST')
    version = models.CharField(max_length=30, default='1.0.0')
    is_active = models.BooleanField(
        default=False,
        help_text="Active model currently selected for live inference"
    )
    accuracy = models.FloatField(default=0.0)
    precision_score = models.FloatField(default=0.0)
    recall_score = models.FloatField(default=0.0)
    f1_score = models.FloatField(default=0.0)
    confusion_matrix_json = models.TextField(blank=True, default='{}')
    classification_report_json = models.TextField(blank=True, default='{}')
    training_samples_count = models.PositiveIntegerField(default=0)
    features_count = models.PositiveIntegerField(default=0)
    trained_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-trained_at']

    def __str__(self):
        return f"{self.name} v{self.version} [Acc: {self.accuracy*100:.1f}%, F1: {self.f1_score*100:.1f}%] {'(ACTIVE)' if self.is_active else ''}"


class DatasetRecord(models.Model):
    name = models.CharField(max_length=150)
    source = models.CharField(max_length=200, help_text="Legitimate dataset origin provenance")
    num_records = models.PositiveIntegerField(default=0)
    num_symptoms = models.PositiveIntegerField(default=0)
    num_diseases = models.PositiveIntegerField(default=0)
    is_validated = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.num_records} samples, {self.num_diseases} diseases)"


class PredictionResult(models.Model):
    assessment = models.ForeignKey(
        SymptomAssessment,
        on_delete=models.CASCADE,
        related_name='predictions'
    )
    predicted_disease = models.ForeignKey(
        Disease,
        on_delete=models.CASCADE,
        related_name='predictions'
    )
    confidence_score = models.FloatField(
        help_text="Calibrated prediction probability (0.0 to 1.0)"
    )
    rank = models.PositiveIntegerField(
        default=1,
        help_text="1 = primary differential condition, 2 = secondary, etc."
    )
    algorithm_used = models.CharField(max_length=60, default='Random Forest')
    is_primary = models.BooleanField(default=False)
    clinical_disclaimer = models.TextField(
        default="Academic decision-support prototype. Machine learning predictions are differential statistical approximations and do NOT constitute confirmed clinical diagnosis."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['assessment', 'rank']

    def __str__(self):
        return f"{self.assessment} -> {self.predicted_disease.name} ({self.confidence_score*100:.1f}%)"
