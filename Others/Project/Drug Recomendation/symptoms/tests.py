from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, PatientProfile
from medical.models import Symptom, Disease, Medicine
from symptoms.models import SymptomAssessment
from symptoms.nlp import nlp_engine


class SymptomsAndNLPTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create Symptoms
        self.s1 = Symptom.objects.create(
            name='high_fever',
            display_name='High Fever',
            category='GENERAL',
            is_emergency=False,
            synonyms='burning temperature, pyrexia, fever'
        )
        self.s2 = Symptom.objects.create(
            name='severe_chest_pain',
            display_name='Severe Chest Pain',
            category='CARDIOVASCULAR',
            is_emergency=True,
            synonyms='crushing chest pain, heart pain'
        )
        self.s3 = Symptom.objects.create(
            name='cough',
            display_name='Dry Cough',
            category='RESPIRATORY',
            is_emergency=False,
            synonyms='hacking cough'
        )

        # Create Disease & Medicine
        self.disease = Disease.objects.create(
            name='Acute Bronchitis',
            code='J20.9',
            urgency_level='MODERATE',
            description='Infection of bronchial tubes'
        )
        self.disease.symptoms.add(self.s1, self.s3)

        self.medicine = Medicine.objects.create(
            name='Paracetamol 500mg',
            generic_name='Paracetamol',
            active_ingredient='Paracetamol',
            category='Analgesic',
            approved_indications='Fever and pain relief',
            age_minimum=6,
            pregnancy_category='B'
        )
        self.disease.medicines.add(self.medicine)

        # Users
        self.patient_a = User.objects.create_user(username='patient_a', password='Password@123', role=User.Role.PATIENT)
        self.profile_a = PatientProfile.objects.create(user=self.patient_a, age=30, gender='MALE')

        self.patient_b = User.objects.create_user(username='patient_b', password='Password@123', role=User.Role.PATIENT)
        self.profile_b = PatientProfile.objects.create(user=self.patient_b, age=45, gender='FEMALE')

    def test_nlp_extraction_with_synonyms(self):
        text = "Patient feels exhausted and has a high fever with burning temperature since yesterday."
        parsed = nlp_engine.parse_symptoms_from_text(text)
        matched_names = [s.name for s in parsed['matched_symptoms']]
        self.assertIn('high_fever', matched_names)

    def test_nlp_negation_detection(self):
        text = "I have a high fever but no cough and denies chest pain."
        parsed = nlp_engine.parse_symptoms_from_text(text)
        matched_names = [s.name for s in parsed['matched_symptoms']]
        self.assertIn('high_fever', matched_names)
        self.assertNotIn('cough', matched_names)
        self.assertNotIn('severe_chest_pain', matched_names)

    def test_nlp_emergency_flag_detection(self):
        text = "Patient experiences severe chest pain and dizziness."
        parsed = nlp_engine.parse_symptoms_from_text(text)
        self.assertTrue(len(parsed['emergency_flags']) > 0)

    def test_symptom_checker_submission_workflow(self):
        self.client.login(username='patient_a', password='Password@123')
        post_data = {
            'action': 'confirm',
            'selected_symptoms': [self.s1.id, self.s3.id],
            'raw_symptom_text': 'I have had fever and cough for two days',
            'duration_days': 2,
            'severity': 'MODERATE',
        }
        response = self.client.post(reverse('symptoms:symptom_checker'), post_data)
        self.assertEqual(response.status_code, 302)

        assessment = SymptomAssessment.objects.filter(patient=self.profile_a).first()
        self.assertIsNotNone(assessment)
        self.assertEqual(assessment.duration_days, 2)
        self.assertEqual(assessment.selected_symptoms.count(), 2)
        self.assertTrue(assessment.predictions.exists())
        self.assertTrue(assessment.recommendations.exists())

    def test_patient_record_isolation(self):
        # Patient A creates an assessment
        assessment = SymptomAssessment.objects.create(
            patient=self.profile_a,
            duration_days=3,
            severity='MILD'
        )
        assessment.selected_symptoms.add(self.s1)

        # Patient B tries to view Patient A's assessment
        self.client.login(username='patient_b', password='Password@123')
        detail_url = reverse('symptoms:assessment_detail', kwargs={'pk': assessment.id})
        response = self.client.get(detail_url)
        # Should return 403 Forbidden
        self.assertEqual(response.status_code, 403)
