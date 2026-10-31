from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, PatientProfile
from medical.models import Symptom, Disease
from symptoms.models import SymptomAssessment
from reports.pdf_generator import generate_assessment_pdf


class ReportsPDFGenerationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='pdf_patient', password='Password@123', role=User.Role.PATIENT)
        self.profile = PatientProfile.objects.create(user=self.user, age=40, gender='MALE')

        self.other_user = User.objects.create_user(username='other_patient', password='Password@123', role=User.Role.PATIENT)
        self.other_profile = PatientProfile.objects.create(user=self.other_user, age=22, gender='FEMALE')

        self.symptom = Symptom.objects.create(name='fatigue', display_name='Fatigue')
        self.disease = Disease.objects.create(name='Anemia', code='D50.9')
        self.disease.symptoms.add(self.symptom)

        self.assessment = SymptomAssessment.objects.create(
            patient=self.profile,
            duration_days=5,
            severity='MODERATE'
        )
        self.assessment.selected_symptoms.add(self.symptom)

    def test_pdf_buffer_generation(self):
        buf = generate_assessment_pdf(self.assessment)
        self.assertIsNotNone(buf)
        content = buf.getvalue()
        self.assertGreater(len(content), 1000)
        # Check PDF header bytes (%PDF)
        self.assertTrue(content.startswith(b'%PDF'))

    def test_download_pdf_http_view_authorized(self):
        self.client.login(username='pdf_patient', password='Password@123')
        resp = self.client.get(reverse('reports:download_assessment_pdf', kwargs={'pk': self.assessment.id}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/pdf')
        self.assertIn(f'Clinical_Assessment_Report_#{self.assessment.id}.pdf', resp['Content-Disposition'])

    def test_download_pdf_http_view_unauthorized(self):
        self.client.login(username='other_patient', password='Password@123')
        resp = self.client.get(reverse('reports:download_assessment_pdf', kwargs={'pk': self.assessment.id}))
        self.assertEqual(resp.status_code, 403)
