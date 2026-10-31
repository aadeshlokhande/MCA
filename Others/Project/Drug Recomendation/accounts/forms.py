from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, PatientProfile, DoctorProfile
from medical.models import PatientAllergy, PatientMedication, PatientMedicalHistory, Allergy, Medicine, Disease


class PatientRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control glass-input', 'placeholder': 'name@example.com'}))
    phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': '+1 (555) 000-0000'}))
    
    # Profile fields
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control glass-input', 'type': 'date'}))
    gender = forms.ChoiceField(choices=PatientProfile.GENDER_CHOICES, widget=forms.Select(attrs={'class': 'form-select glass-input'}))
    blood_group = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': 'e.g. O+, A-'}))
    is_pregnant = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-control glass-input')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.PATIENT
        if commit:
            user.save()
            PatientProfile.objects.create(
                user=user,
                date_of_birth=self.cleaned_data.get('date_of_birth'),
                gender=self.cleaned_data.get('gender', 'MALE'),
                blood_group=self.cleaned_data.get('blood_group', ''),
                is_pregnant=self.cleaned_data.get('is_pregnant', False),
            )
        return user


class DoctorRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control glass-input'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control glass-input'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control glass-input'}))
    phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control glass-input'}))
    
    # Doctor Profile fields
    license_number = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': 'e.g. MED-849204'}))
    specialization = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': 'e.g. Internal Medicine / General Practice'}))
    hospital_affiliation = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': 'e.g. Metro Health Medical Center'}))
    years_of_experience = forms.IntegerField(min_value=0, initial=1, widget=forms.NumberInput(attrs={'class': 'form-control glass-input'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control glass-input')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.DOCTOR
        if commit:
            user.save()
            DoctorProfile.objects.create(
                user=user,
                license_number=self.cleaned_data.get('license_number'),
                specialization=self.cleaned_data.get('specialization'),
                hospital_affiliation=self.cleaned_data.get('hospital_affiliation', ''),
                years_of_experience=self.cleaned_data.get('years_of_experience', 1),
            )
        return user


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control glass-input',
            'placeholder': 'Enter your username or email'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control glass-input',
            'placeholder': 'Enter your password'
        })


class PatientProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control glass-input'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control glass-input'}))
    phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control glass-input'}))

    class Meta:
        model = PatientProfile
        fields = ['date_of_birth', 'age', 'gender', 'blood_group', 'is_pregnant', 'emergency_contact_name', 'emergency_contact_phone', 'notes']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control glass-input', 'type': 'date'}),
            'age': forms.NumberInput(attrs={'class': 'form-control glass-input', 'min': '0', 'max': '130'}),
            'gender': forms.Select(attrs={'class': 'form-select glass-input'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control glass-input'}),
            'is_pregnant': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control glass-input'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control glass-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control glass-input', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['phone_number'].initial = self.instance.user.phone_number

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        if commit:
            user.save()
            profile.save()
        return profile


class PatientAllergyForm(forms.ModelForm):
    class Meta:
        model = PatientAllergy
        fields = ['allergy', 'reaction_severity', 'reaction_description', 'diagnosed_date']
        widgets = {
            'allergy': forms.Select(attrs={'class': 'form-select glass-input'}),
            'reaction_severity': forms.Select(attrs={'class': 'form-select glass-input'}),
            'reaction_description': forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': 'e.g. Skin hives, facial swelling'}),
            'diagnosed_date': forms.DateInput(attrs={'class': 'form-control glass-input', 'type': 'date'}),
        }


class PatientMedicationForm(forms.ModelForm):
    class Meta:
        model = PatientMedication
        fields = ['medicine_name', 'medicine_reference', 'dosage', 'frequency', 'started_date', 'prescribed_by', 'is_active']
        widgets = {
            'medicine_name': forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': 'e.g. Metformin 500mg'}),
            'medicine_reference': forms.Select(attrs={'class': 'form-select glass-input'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': 'e.g. 500mg'}),
            'frequency': forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': 'e.g. Twice daily with meals'}),
            'started_date': forms.DateInput(attrs={'class': 'form-control glass-input', 'type': 'date'}),
            'prescribed_by': forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': 'e.g. Dr. Jane Smith'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PatientMedicalHistoryForm(forms.ModelForm):
    class Meta:
        model = PatientMedicalHistory
        fields = ['condition_name', 'disease_reference', 'status', 'diagnosed_date', 'notes']
        widgets = {
            'condition_name': forms.TextInput(attrs={'class': 'form-control glass-input', 'placeholder': 'e.g. Peptic Ulcer Disease'}),
            'disease_reference': forms.Select(attrs={'class': 'form-select glass-input'}),
            'status': forms.Select(attrs={'class': 'form-select glass-input'}),
            'diagnosed_date': forms.DateInput(attrs={'class': 'form-control glass-input', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control glass-input', 'rows': 2, 'placeholder': 'Relevant medical background'}),
        }
