from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, PatientProfile, DoctorProfile
from medical.models import Allergy, PatientAllergy, PatientMedication, PatientMedicalHistory


class AccountsAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.patient_user = User.objects.create_user(
            username='test_patient',
            email='patient@example.com',
            password='TestPassword@123',
            role=User.Role.PATIENT,
            first_name='Jane',
            last_name='Doe'
        )
        self.patient_profile = PatientProfile.objects.create(
            user=self.patient_user,
            age=28,
            gender='FEMALE',
            blood_group='A+'
        )

        self.doctor_user = User.objects.create_user(
            username='test_doctor',
            email='doctor@example.com',
            password='TestPassword@123',
            role=User.Role.DOCTOR,
            first_name='John',
            last_name='Watson'
        )
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user,
            license_number='LIC-998877',
            specialization='General Practice',
            years_of_experience=8
        )

        self.admin_user = User.objects.create_superuser(
            username='test_admin',
            email='admin@example.com',
            password='TestPassword@123',
            role=User.Role.ADMIN
        )

    def test_patient_login_and_role_redirect(self):
        login_success = self.client.login(username='test_patient', password='TestPassword@123')
        self.assertTrue(login_success)
        response = self.client.get(reverse('accounts:role_redirect'))
        self.assertRedirects(response, reverse('dashboard:patient_dashboard'))

    def test_doctor_login_and_role_redirect(self):
        self.client.login(username='test_doctor', password='TestPassword@123')
        response = self.client.get(reverse('accounts:role_redirect'))
        self.assertRedirects(response, reverse('dashboard:doctor_dashboard'))

    def test_admin_login_and_role_redirect(self):
        self.client.login(username='test_admin', password='TestPassword@123')
        response = self.client.get(reverse('accounts:role_redirect'))
        self.assertRedirects(response, reverse('dashboard:admin_dashboard'))

    def test_patient_registration_workflow(self):
        reg_data = {
            'username': 'new_patient_user',
            'first_name': 'Alice',
            'last_name': 'Wonder',
            'email': 'alice@example.com',
            'phone_number': '555-1234',
            'gender': 'FEMALE',
            'blood_group': 'B+',
            'password1': 'StrongPass@2026',
            'password2': 'StrongPass@2026',
        }
        response = self.client.post(reverse('accounts:register_patient'), reg_data)
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.filter(username='new_patient_user').first()
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.role, User.Role.PATIENT)
        self.assertTrue(hasattr(new_user, 'patient_profile'))
        self.assertEqual(new_user.patient_profile.blood_group, 'B+')

    def test_doctor_registration_workflow(self):
        reg_data = {
            'username': 'new_doc_user',
            'first_name': 'Gregory',
            'last_name': 'House',
            'email': 'house@example.com',
            'license_number': 'LIC-102938',
            'specialization': 'Diagnostic Medicine',
            'years_of_experience': 15,
            'password1': 'StrongPass@2026',
            'password2': 'StrongPass@2026',
        }
        response = self.client.post(reverse('accounts:register_doctor'), reg_data)
        self.assertEqual(response.status_code, 302)
        doc = User.objects.filter(username='new_doc_user').first()
        self.assertIsNotNone(doc)
        self.assertEqual(doc.role, User.Role.DOCTOR)
        self.assertEqual(doc.doctor_profile.license_number, 'LIC-102938')

    def test_patient_allergy_crud(self):
        self.client.login(username='test_patient', password='TestPassword@123')
        allergy = Allergy.objects.create(name='Aspirin Allergy', allergy_type='DRUG', affected_active_ingredients='aspirin')
        
        # Add allergy
        add_resp = self.client.post(reverse('accounts:add_allergy'), {
            'allergy': allergy.id,
            'reaction_severity': 'SEVERE',
            'reaction_description': 'Angioedema and bronchospasm'
        })
        self.assertEqual(add_resp.status_code, 302)
        pa = PatientAllergy.objects.filter(patient=self.patient_profile, allergy=allergy).first()
        self.assertIsNotNone(pa)
        self.assertEqual(pa.reaction_severity, 'SEVERE')

        # Delete allergy
        del_resp = self.client.post(reverse('accounts:delete_allergy', kwargs={'pk': pa.id}))
        self.assertEqual(del_resp.status_code, 302)
        self.assertFalse(PatientAllergy.objects.filter(id=pa.id).exists())

    def test_unauthorized_role_access_blocked(self):
        # Patient cannot access doctor dashboard
        self.client.login(username='test_patient', password='TestPassword@123')
        resp = self.client.get(reverse('dashboard:doctor_dashboard'))
        # Should redirect to role redirect with error message
        self.assertEqual(resp.status_code, 302)
