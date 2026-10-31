from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, PatientProfile, DoctorProfile
from medical.models import Symptom, Disease, Medicine
from symptoms.models import SymptomAssessment
from recommendations.models import RecommendationRecord, DoctorReview
from dashboard.models import Notification


class DashboardAndReviewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Patient
        self.patient_user = User.objects.create_user(username='dash_patient', password='Password@123', role=User.Role.PATIENT)
        self.patient_profile = PatientProfile.objects.create(user=self.patient_user, age=33, gender='MALE')

        # Doctor
        self.doctor_user = User.objects.create_user(username='dash_doctor', password='Password@123', role=User.Role.DOCTOR)
        self.doctor_profile = DoctorProfile.objects.create(user=self.doctor_user, license_number='LIC-112233', specialization='Internal Medicine')

        # Disease & Medicine
        self.disease = Disease.objects.create(name='Hypertension', code='I10')
        self.medicine = Medicine.objects.create(
            name='Amlodipine 5mg',
            generic_name='Amlodipine',
            active_ingredient='Amlodipine',
            category='Antihypertensive',
            approved_indications='Hypertension',
            pregnancy_category='C'
        )
        self.disease.medicines.add(self.medicine)

        # Assessment
        self.assessment = SymptomAssessment.objects.create(
            patient=self.patient_profile,
            duration_days=4,
            severity='MODERATE'
        )
        self.rec = RecommendationRecord.objects.create(
            assessment=self.assessment,
            medicine=self.medicine,
            disease=self.disease,
            is_suppressed=False,
            doctor_approval_status='PENDING'
        )

    def test_patient_dashboard_view(self):
        self.client.login(username='dash_patient', password='Password@123')
        resp = self.client.get(reverse('dashboard:patient_dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Hello, dash_patient")

    def test_doctor_dashboard_view(self):
        self.client.login(username='dash_doctor', password='Password@123')
        resp = self.client.get(reverse('dashboard:doctor_dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Patient Assessment Triage Queue")

    def test_doctor_review_submission_workflow(self):
        self.client.login(username='dash_doctor', password='Password@123')
        review_url = reverse('dashboard:doctor_review_assessment', kwargs={'pk': self.assessment.id})

        post_data = {
            'status': 'APPROVED',
            'clinical_diagnosis_notes': 'Primary essential hypertension without target organ damage.',
            'patient_instructions': 'Begin dietary salt reduction, exercise 30 minutes daily.',
            'clinical_modifications': 'Start with low dose in the morning.',
            'follow_up_advice': 'Check BP in 2 weeks.',
            'approved_medicines': [self.medicine.id]
        }

        resp = self.client.post(review_url, post_data)
        self.assertEqual(resp.status_code, 302)

        # Verify DoctorReview was created
        review = DoctorReview.objects.filter(assessment=self.assessment).first()
        self.assertIsNotNone(review)
        self.assertEqual(review.status, 'APPROVED')
        self.assertEqual(review.doctor, self.doctor_profile)
        self.assertIn(self.medicine, review.approved_medicines.all())

        # Verify assessment status updated
        self.assessment.refresh_from_db()
        self.assertEqual(self.assessment.status, 'REVIEWED')

        # Verify notification created for patient
        notif = Notification.objects.filter(recipient=self.patient_user).first()
        self.assertIsNotNone(notif)
        self.assertIn("Doctor Review Completed", notif.title)

    def test_notification_read_ajax(self):
        notif = Notification.objects.create(
            recipient=self.patient_user,
            title="Test Notice",
            message="Your test notice message"
        )
        self.client.login(username='dash_patient', password='Password@123')
        resp = self.client.post(reverse('dashboard:mark_notification_read', kwargs={'pk': notif.id}))
        self.assertEqual(resp.status_code, 200)
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)
