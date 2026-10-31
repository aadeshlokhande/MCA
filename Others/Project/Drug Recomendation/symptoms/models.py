from django.db import models
from accounts.models import PatientProfile
from medical.models import Symptom


class SymptomAssessment(models.Model):
    SEVERITY_LEVELS = (
        ('MILD', 'Mild - Noticeable but does not disrupt daily routine'),
        ('MODERATE', 'Moderate - Interferes somewhat with routine activities'),
        ('SEVERE', 'Severe - Severely impacts daily functioning or causing significant distress'),
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pending Analysis'),
        ('ANALYZED', 'Analyzed by AI Pipeline'),
        ('PENDING_REVIEW', 'Awaiting Clinical Review'),
        ('REVIEWED', 'Reviewed by Healthcare Professional'),
    )

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name='assessments'
    )
    selected_symptoms = models.ManyToManyField(
        Symptom,
        related_name='assessments'
    )
    raw_symptom_text = models.TextField(
        blank=True,
        help_text="Optional natural-language description entered by the patient"
    )
    extracted_symptoms_notes = models.TextField(
        blank=True,
        help_text="Normalized symptoms identified via NLP parsing"
    )
    duration_days = models.PositiveIntegerField(
        default=1,
        help_text="Approximate symptom duration in days"
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_LEVELS,
        default='MODERATE'
    )
    has_emergency_symptoms = models.BooleanField(
        default=False,
        help_text="True if any red-flag emergency symptoms are present"
    )
    emergency_guidance_provided = models.BooleanField(
        default=False,
        help_text="True if patient was shown immediate emergency escalation instructions"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ANALYZED'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Assessment #{self.id} - {self.patient.user.get_full_name() or self.patient.user.username} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
