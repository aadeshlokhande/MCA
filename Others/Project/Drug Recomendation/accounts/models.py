from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = 'PATIENT', 'Patient'
        DOCTOR = 'DOCTOR', 'Doctor'
        ADMIN = 'ADMIN', 'Administrator'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PATIENT,
        help_text="Role-based access level for user permissions."
    )
    phone_number = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(
        default=False,
        help_text="Verification status for doctor credentials or patient phone."
    )

    def is_patient(self):
        return self.role == self.Role.PATIENT

    def is_doctor(self):
        return self.role == self.Role.DOCTOR

    def is_administrator(self):
        return self.role == self.Role.ADMIN or self.is_superuser


class PatientProfile(models.Model):
    GENDER_CHOICES = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='patient_profile'
    )
    date_of_birth = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='MALE')
    blood_group = models.CharField(max_length=10, blank=True)
    is_pregnant = models.BooleanField(
        default=False,
        help_text="Relevant for pregnancy-contraindicated medications."
    )
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=25, blank=True)
    notes = models.TextField(blank=True, help_text="Relevant non-sensitive clinical notes.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.date_of_birth and not self.age:
            today = timezone.now().date()
            self.age = today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} (Age: {self.age or 'N/A'})"


class DoctorProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    license_number = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=100, default='General Practice')
    hospital_affiliation = models.CharField(max_length=150, blank=True)
    years_of_experience = models.PositiveIntegerField(default=1)
    bio = models.TextField(blank=True)
    is_approved = models.BooleanField(
        default=True,
        help_text="Administrator approval for active clinical reviewing."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} - {self.specialization}"
