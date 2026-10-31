from django.db import models
from symptoms.models import SymptomAssessment
from medical.models import Medicine, Disease
from accounts.models import DoctorProfile


class RecommendationRecord(models.Model):
    APPROVAL_STATUS = (
        ('PENDING', 'Pending Doctor Review'),
        ('APPROVED', 'Approved by Doctor'),
        ('REJECTED', 'Rejected by Doctor'),
        ('MODIFIED', 'Modified by Doctor'),
    )

    assessment = models.ForeignKey(
        SymptomAssessment,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.CASCADE,
        related_name='recommendation_records'
    )
    disease = models.ForeignKey(
        Disease,
        on_delete=models.CASCADE,
        related_name='disease_recommendations'
    )
    is_suppressed = models.BooleanField(
        default=False,
        help_text="True if high-risk safety conflict was detected, suppressing recommendation from normal patient view"
    )
    suppression_reason = models.TextField(
        blank=True,
        help_text="Detailed rationale for suppressing this medicine from candidate recommendations"
    )
    educational_notes = models.TextField(
        blank=True,
        help_text="Approved indication and general educational information"
    )
    doctor_review_required = models.BooleanField(
        default=True,
        help_text="Mandatory clinical verification before patient guidance"
    )
    doctor_approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS,
        default='PENDING'
    )
    doctor_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        DoctorProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_recommendations'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['is_suppressed', 'medicine__generic_name']

    def __str__(self):
        suppress_label = "[SUPPRESSED]" if self.is_suppressed else "[ACTIVE]"
        return f"{suppress_label} {self.medicine.name} for {self.disease.name} ({self.doctor_approval_status})"


class SafetyIssue(models.Model):
    ISSUE_TYPES = (
        ('ALLERGY', 'Patient Allergy Hazard'),
        ('DRUG_INTERACTION', 'Drug-Drug Interaction with Existing Medication'),
        ('CONTRAINDICATION', 'Medical History Contraindication'),
        ('AGE_RESTRICTION', 'Age-Related Restriction / Precaution'),
        ('PREGNANCY', 'Pregnancy Safety Precaution'),
        ('DUPLICATE_INGREDIENT', 'Duplicate Active Ingredient Exposure'),
        ('MISSING_DATA', 'Incomplete Medical History Warning'),
    )

    SEVERITY_LEVELS = (
        ('WARNING', 'Moderate Precaution (Requires Caution & Monitoring)'),
        ('SEVERE', 'Severe Risk (Candidate Suppressed - Urgent Review Required)'),
        ('CONTRAINDICATED', 'Absolute Contraindication (Strictly Prohibited)'),
    )

    recommendation = models.ForeignKey(
        RecommendationRecord,
        on_delete=models.CASCADE,
        related_name='safety_issues'
    )
    issue_type = models.CharField(max_length=30, choices=ISSUE_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='SEVERE')
    title = models.CharField(max_length=200)
    description = models.TextField()
    clinical_action_needed = models.TextField(
        default="Suppress candidate recommendation. Qualified healthcare provider must perform comprehensive medication review."
    )
    detected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.severity}: {self.title} ({self.issue_type})"


class DoctorReview(models.Model):
    REVIEW_STATUS = (
        ('APPROVED', 'Approved (Clinical Recommendation Endorsed)'),
        ('MODIFIED', 'Modified (Adjusted with Clinical Notes)'),
        ('REJECTED', 'Rejected (AI Candidate Inappropriate)'),
        ('REFERRED', 'Referred to Specialist / In-Person Evaluation'),
    )

    assessment = models.OneToOneField(
        SymptomAssessment,
        on_delete=models.CASCADE,
        related_name='doctor_review'
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='clinical_reviews'
    )
    status = models.CharField(max_length=20, choices=REVIEW_STATUS, default='APPROVED')
    clinical_diagnosis_notes = models.TextField(
        help_text="Doctor's independent clinical assessment and diagnostic notes"
    )
    approved_medicines = models.ManyToManyField(
        Medicine,
        related_name='doctor_approved_cases',
        blank=True
    )
    clinical_modifications = models.TextField(
        blank=True,
        help_text="Specific modifications made by doctor (dosage considerations, non-pharmacological care, substitutions)"
    )
    patient_instructions = models.TextField(
        help_text="Direct patient advice and instructions formulated by the doctor"
    )
    follow_up_advice = models.TextField(
        blank=True,
        help_text="When to return, monitoring schedule, or emergency symptoms to watch for"
    )
    reviewed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by Dr. {self.doctor.user.get_full_name() or self.doctor.user.username} - Assessment #{self.assessment.id} ({self.status})"
