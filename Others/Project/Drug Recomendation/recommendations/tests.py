from django.test import TestCase
from accounts.models import User, PatientProfile
from medical.models import (
    Symptom,
    Disease,
    Medicine,
    DrugInteraction,
    Allergy,
    PatientAllergy,
    PatientMedication,
    PatientMedicalHistory,
)
from symptoms.models import SymptomAssessment
from ml_engine.models import PredictionResult
from recommendations.engine import safety_engine
from recommendations.models import RecommendationRecord, SafetyIssue


class DrugSafetyScreeningTests(TestCase):
    def setUp(self):
        # Patient
        self.user = User.objects.create_user(username='safe_patient', password='Password@123', role=User.Role.PATIENT)
        self.patient = PatientProfile.objects.create(user=self.user, age=14, gender='FEMALE', is_pregnant=True)

        # Disease
        self.disease = Disease.objects.create(name='Tension Headache', code='G44.2')
        self.symptom = Symptom.objects.create(name='headache', display_name='Headache')
        self.disease.symptoms.add(self.symptom)

        # Medicines
        self.med_paracetamol = Medicine.objects.create(
            name='Paracetamol 500mg',
            generic_name='Paracetamol',
            active_ingredient='Paracetamol',
            category='Analgesic',
            approved_indications='Mild pain',
            age_minimum=6,
            pregnancy_category='B'
        )

        self.med_ibuprofen = Medicine.objects.create(
            name='Ibuprofen 400mg',
            generic_name='Ibuprofen',
            active_ingredient='Ibuprofen',
            category='NSAID',
            approved_indications='Pain and inflammation',
            contraindications='Active peptic ulcer, severe renal failure',
            age_minimum=12,
            pregnancy_category='D',
            pregnancy_warning='Contraindicated in third trimester'
        )

        self.med_aspirin = Medicine.objects.create(
            name='Aspirin 81mg',
            generic_name='Aspirin',
            active_ingredient='Aspirin',
            category='Antiplatelet',
            approved_indications='Cardiovascular risk reduction',
            age_minimum=16,
            pregnancy_category='D'
        )

        self.disease.medicines.add(self.med_paracetamol, self.med_ibuprofen, self.med_aspirin)

        # Assessment
        self.assessment = SymptomAssessment.objects.create(
            patient=self.patient,
            duration_days=2,
            severity='MILD'
        )
        self.assessment.selected_symptoms.add(self.symptom)

        # Prediction
        PredictionResult.objects.create(
            assessment=self.assessment,
            predicted_disease=self.disease,
            confidence_score=0.92,
            rank=1,
            is_primary=True
        )

    def test_allergy_hazard_causes_suppression(self):
        # Patient has documented allergy to paracetamol
        allergy = Allergy.objects.create(
            name='Paracetamol Allergy',
            allergy_type='DRUG',
            affected_active_ingredients='paracetamol'
        )
        PatientAllergy.objects.create(
            patient=self.patient,
            allergy=allergy,
            reaction_severity='ANAPHYLAXIS'
        )

        recs = safety_engine.screen_assessment_recommendations(self.assessment)
        para_rec = next((r for r in recs if r.medicine.active_ingredient == 'Paracetamol'), None)

        self.assertIsNotNone(para_rec)
        self.assertTrue(para_rec.is_suppressed)
        self.assertIn("Allergy Hazard", para_rec.suppression_reason)
        self.assertTrue(para_rec.safety_issues.filter(issue_type='ALLERGY').exists())

    def test_drug_drug_interaction_causes_suppression(self):
        # Patient takes ongoing Ibuprofen
        PatientMedication.objects.create(
            patient=self.patient,
            medicine_name='Ibuprofen 400mg',
            medicine_reference=self.med_ibuprofen,
            is_active=True
        )
        # Interaction between Aspirin and Ibuprofen
        DrugInteraction.objects.create(
            medicine_a=self.med_aspirin,
            medicine_b=self.med_ibuprofen,
            severity='SEVERE',
            description='Severe GI bleeding risk',
            action_required='Suppress recommendation'
        )

        recs = safety_engine.screen_assessment_recommendations(self.assessment)
        aspirin_rec = next((r for r in recs if r.medicine.generic_name == 'Aspirin'), None)

        self.assertIsNotNone(aspirin_rec)
        self.assertTrue(aspirin_rec.is_suppressed)
        self.assertTrue(aspirin_rec.safety_issues.filter(issue_type='DRUG_INTERACTION').exists())

    def test_medical_history_contraindication_causes_suppression(self):
        # Patient has history of peptic ulcer
        PatientMedicalHistory.objects.create(
            patient=self.patient,
            condition_name='Active Peptic Ulcer Disease',
            status='ACTIVE'
        )

        recs = safety_engine.screen_assessment_recommendations(self.assessment)
        ibu_rec = next((r for r in recs if r.medicine.generic_name == 'Ibuprofen'), None)

        self.assertIsNotNone(ibu_rec)
        self.assertTrue(ibu_rec.is_suppressed)
        self.assertTrue(ibu_rec.safety_issues.filter(issue_type='CONTRAINDICATION').exists())

    def test_age_restriction_causes_suppression(self):
        # Patient age is 14; Aspirin minimum age is 16
        recs = safety_engine.screen_assessment_recommendations(self.assessment)
        aspirin_rec = next((r for r in recs if r.medicine.generic_name == 'Aspirin'), None)

        self.assertIsNotNone(aspirin_rec)
        self.assertTrue(aspirin_rec.is_suppressed)
        self.assertTrue(aspirin_rec.safety_issues.filter(issue_type='AGE_RESTRICTION').exists())

    def test_pregnancy_hazard_causes_suppression(self):
        # Patient is pregnant; Ibuprofen is Category D
        recs = safety_engine.screen_assessment_recommendations(self.assessment)
        ibu_rec = next((r for r in recs if r.medicine.generic_name == 'Ibuprofen'), None)

        self.assertIsNotNone(ibu_rec)
        self.assertTrue(ibu_rec.is_suppressed)
        self.assertTrue(ibu_rec.safety_issues.filter(issue_type='PREGNANCY').exists())

    def test_duplicate_active_ingredient_causes_suppression(self):
        # Patient takes generic paracetamol
        PatientMedication.objects.create(
            patient=self.patient,
            medicine_name='Crocin 500mg',
            medicine_reference=self.med_paracetamol,
            is_active=True
        )

        recs = safety_engine.screen_assessment_recommendations(self.assessment)
        para_rec = next((r for r in recs if r.medicine.active_ingredient == 'Paracetamol'), None)

        self.assertIsNotNone(para_rec)
        self.assertTrue(para_rec.is_suppressed)
        self.assertTrue(para_rec.safety_issues.filter(issue_type='DUPLICATE_INGREDIENT').exists())
