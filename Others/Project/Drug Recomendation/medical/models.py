from django.db import models
from accounts.models import PatientProfile


class Symptom(models.Model):
    CATEGORY_CHOICES = (
        ('GENERAL', 'General / Constitutional'),
        ('RESPIRATORY', 'Respiratory'),
        ('DIGESTIVE', 'Digestive / Gastrointestinal'),
        ('CARDIOVASCULAR', 'Cardiovascular'),
        ('NEUROLOGICAL', 'Neurological'),
        ('MUSCULOSKELETAL', 'Musculoskeletal'),
        ('DERMATOLOGICAL', 'Skin & Hair'),
        ('UROLOGICAL', 'Urological / Renal'),
        ('PSYCHOLOGICAL', 'Mental & Behavioral'),
    )

    name = models.CharField(max_length=100, unique=True, help_text="Normalized identifier, e.g. 'high_fever'")
    display_name = models.CharField(max_length=120, help_text="Human readable name, e.g. 'High Fever'")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='GENERAL')
    description = models.TextField(blank=True)
    is_emergency = models.BooleanField(
        default=False,
        help_text="Flag for emergency/red-flag symptoms requiring immediate medical evaluation."
    )
    synonyms = models.TextField(
        blank=True,
        help_text="Comma-separated synonyms or lay terms for NLP matching (e.g. 'head ache, cephalalgia, throbbing head')"
    )

    class Meta:
        ordering = ['display_name']

    def __str__(self):
        return f"{self.display_name} {'[EMERGENCY RED-FLAG]' if self.is_emergency else ''}"


class Disease(models.Model):
    URGENCY_CHOICES = (
        ('LOW', 'Low - Self-Limiting / Routine Care'),
        ('MODERATE', 'Moderate - Medical Consultation Recommended'),
        ('HIGH', 'High - Prompt Medical Attention Required'),
        ('EMERGENCY', 'Critical - Immediate Emergency Care Required'),
    )

    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=50, blank=True, help_text="ICD-10 or clinical reference code")
    description = models.TextField()
    symptoms = models.ManyToManyField(Symptom, related_name='diseases', blank=True)
    urgency_level = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='MODERATE')
    general_advice = models.TextField(blank=True, help_text="General lifestyle and non-prescription self-care guidelines")
    specialist_type = models.CharField(max_length=100, default='General Physician')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Allergy(models.Model):
    ALLERGY_TYPES = (
        ('DRUG', 'Drug / Medication Allergy'),
        ('FOOD', 'Food Allergy'),
        ('ENVIRONMENTAL', 'Environmental Allergy'),
        ('OTHER', 'Other'),
    )

    name = models.CharField(max_length=120, unique=True)
    allergy_type = models.CharField(max_length=20, choices=ALLERGY_TYPES, default='DRUG')
    description = models.TextField(blank=True)
    affected_active_ingredients = models.TextField(
        blank=True,
        help_text="Comma-separated active ingredients that cross-react (e.g. 'amoxicillin, ampicillin, penicillin v')"
    )

    class Meta:
        verbose_name_plural = 'Allergies'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_allergy_type_display()})"


class PatientAllergy(models.Model):
    SEVERITY_CHOICES = (
        ('MILD', 'Mild (Rash, Itching)'),
        ('MODERATE', 'Moderate (Urticaria, Angioedema)'),
        ('SEVERE', 'Severe (Breathing difficulty, Bronchospasm)'),
        ('ANAPHYLAXIS', 'Life-Threatening Anaphylaxis'),
    )

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='allergies')
    allergy = models.ForeignKey(Allergy, on_delete=models.CASCADE)
    reaction_severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MODERATE')
    reaction_description = models.TextField(blank=True)
    diagnosed_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('patient', 'allergy')
        verbose_name_plural = 'Patient Allergies'

    def __str__(self):
        return f"{self.patient} - {self.allergy.name} ({self.reaction_severity})"


class Medicine(models.Model):
    PREGNANCY_CATEGORIES = (
        ('A', 'Category A - Adequate, well-controlled studies failed to demonstrate risk'),
        ('B', 'Category B - Animal studies show no risk, or animal studies show risk but human studies do not'),
        ('C', 'Category C - Animal studies show adverse effects, lack of adequate human studies; use only if potential benefit justifies risk'),
        ('D', 'Category D - Positive evidence of human fetal risk, but benefits may warrant use in life-threatening situations'),
        ('X', 'Category X - Demonstrated fetal abnormalities or evidence of fetal risk; CONTRAINDICATED in pregnancy'),
        ('N', 'Category N - Not classified or insufficient data'),
    )

    name = models.CharField(max_length=150, help_text="Brand or common formulation name, e.g. 'Paracetamol 500mg'")
    generic_name = models.CharField(max_length=150, help_text="Standardized generic name, e.g. 'Paracetamol'")
    active_ingredient = models.CharField(max_length=150, help_text="Primary active pharmaceutical ingredient")
    category = models.CharField(max_length=100, help_text="e.g. 'Analgesic / Antipyretic'")
    dosage_form = models.CharField(max_length=50, default='Oral Tablet', help_text="e.g. 'Tablet', 'Capsule', 'Syrup'")
    is_prescription_only = models.BooleanField(
        default=True,
        help_text="Requires doctor prescription. Prescription-only medicines cannot be recommended for self-medication."
    )
    approved_indications = models.TextField(help_text="General approved clinical indications and use cases")
    indicated_diseases = models.ManyToManyField(Disease, related_name='medicines', blank=True)
    contraindications = models.TextField(
        blank=True,
        help_text="Clinical contraindications (e.g. 'Active peptic ulcer, severe renal impairment, asthma exacerbation')"
    )
    known_precautions = models.TextField(
        blank=True,
        help_text="Clinical warnings and precautions (e.g. 'Monitor liver enzymes with prolonged therapy, take with food')"
    )
    age_minimum = models.PositiveIntegerField(
        default=0,
        help_text="Minimum patient age in years approved for administration (e.g. 18 for adult only, 12 for pediatric precaution)"
    )
    age_maximum = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum age in years if geriatric precaution exists"
    )
    pregnancy_category = models.CharField(max_length=5, choices=PREGNANCY_CATEGORIES, default='C')
    pregnancy_warning = models.TextField(blank=True, help_text="Pregnancy and lactation safety precautions")
    is_controlled_substance = models.BooleanField(default=False)
    source_reference = models.CharField(
        max_length=200,
        default='WHO Model List of Essential Medicines / Curated Clinical Reference Data',
        help_text="Verified source provenance"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['generic_name', 'name']

    def __str__(self):
        rx_tag = "[Rx Only]" if self.is_prescription_only else "[OTC]"
        return f"{self.name} ({self.generic_name}) {rx_tag}"


class DrugInteraction(models.Model):
    SEVERITY_CHOICES = (
        ('MILD', 'Mild - Minor clinical significance, minimal monitoring needed'),
        ('MODERATE', 'Moderate - Assess risk, consider dosage adjustment or timing separation'),
        ('SEVERE', 'Severe - Significant clinical hazard, avoid combination or close monitoring required'),
        ('CONTRAINDICATED', 'Contraindicated - High risk of severe adverse events or toxicity, DO NOT CO-ADMINISTER'),
    )

    medicine_a = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='interactions_as_a')
    medicine_b = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='interactions_as_b')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MODERATE')
    description = models.TextField(help_text="Clinical mechanism of the interaction and physiological risk")
    action_required = models.TextField(help_text="Recommended clinical action (e.g. 'Suppress recommendation, professional review mandatory')")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('medicine_a', 'medicine_b')
        verbose_name_plural = 'Drug Interactions'

    def __str__(self):
        return f"Interaction: {self.medicine_a.generic_name} + {self.medicine_b.generic_name} ({self.severity})"


class PatientMedication(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='current_medications')
    medicine_name = models.CharField(max_length=150)
    medicine_reference = models.ForeignKey(Medicine, on_delete=models.SET_NULL, null=True, blank=True)
    dosage = models.CharField(max_length=100, help_text="e.g. '500 mg twice daily'")
    frequency = models.CharField(max_length=100, blank=True)
    started_date = models.DateField(null=True, blank=True)
    prescribed_by = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_active', '-created_at']

    def __str__(self):
        return f"{self.patient} - {self.medicine_name} ({'Active' if self.is_active else 'Inactive'})"


class PatientMedicalHistory(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Active / Ongoing'),
        ('MANAGED', 'Medically Managed / Controlled'),
        ('CHRONIC', 'Chronic Condition'),
        ('RESOLVED', 'Resolved / Historical'),
    )

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='medical_history')
    condition_name = models.CharField(max_length=150, help_text="e.g. 'Asthma', 'Chronic Kidney Disease', 'Peptic Ulcer'")
    disease_reference = models.ForeignKey(Disease, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    diagnosed_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Patient Medical Histories'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient} - {self.condition_name} ({self.status})"
