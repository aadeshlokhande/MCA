from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden

from .models import User, PatientProfile, DoctorProfile
from .forms import (
    PatientRegistrationForm,
    DoctorRegistrationForm,
    UserLoginForm,
    PatientProfileForm,
    PatientAllergyForm,
    PatientMedicationForm,
    PatientMedicalHistoryForm,
)
from .decorators import patient_required
from medical.models import PatientAllergy, PatientMedication, PatientMedicalHistory
from audit.models import log_audit_event, AuditLog
from dashboard.models import Notification


def register_patient(request):
    if request.user.is_authenticated:
        return redirect('accounts:role_redirect')

    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            log_audit_event(request, AuditLog.Action.REGISTRATION, f"New patient registered: {user.username}", user=user)
            messages.success(request, "Registration successful! You may now sign in to access your patient portal.")
            return redirect('accounts:login')
        else:
            messages.error(request, "Please correct the errors in the registration form.")
    else:
        form = PatientRegistrationForm()

    return render(request, 'accounts/register_patient.html', {'form': form})


def register_doctor(request):
    if request.user.is_authenticated:
        return redirect('accounts:role_redirect')

    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            log_audit_event(request, AuditLog.Action.REGISTRATION, f"New doctor registered: {user.username} (License: {form.cleaned_data.get('license_number')})", user=user)
            messages.success(request, "Doctor registration submitted successfully! Please sign in to access clinical review.")
            return redirect('accounts:login')
        else:
            messages.error(request, "Please correct the errors in the registration form.")
    else:
        form = DoctorRegistrationForm()

    return render(request, 'accounts/register_doctor.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('accounts:role_redirect')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            log_audit_event(request, AuditLog.Action.LOGIN, f"User {user.username} logged in successfully.", user=user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            return redirect('accounts:role_redirect')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def user_logout(request):
    username = request.user.username
    log_audit_event(request, AuditLog.Action.LOGOUT, f"User {username} logged out.")
    logout(request)
    messages.info(request, "You have been logged out securely.")
    return redirect('accounts:login')


@login_required
def role_redirect(request):
    """Direct user to their dedicated role-based landing dashboard."""
    user = request.user
    if user.is_administrator():
        return redirect('dashboard:admin_dashboard')
    elif user.is_doctor():
        return redirect('dashboard:doctor_dashboard')
    else:
        return redirect('dashboard:patient_dashboard')


@login_required
@patient_required
def profile_view(request):
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your medical profile has been updated successfully.")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please review the highlighted errors.")
    else:
        form = PatientProfileForm(instance=profile)

    allergies = profile.allergies.select_related('allergy').all()
    medications = profile.current_medications.all()
    history = profile.medical_history.all()

    allergy_form = PatientAllergyForm()
    medication_form = PatientMedicationForm()
    history_form = PatientMedicalHistoryForm()

    context = {
        'profile': profile,
        'form': form,
        'allergies': allergies,
        'medications': medications,
        'history': history,
        'allergy_form': allergy_form,
        'medication_form': medication_form,
        'history_form': history_form,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
@patient_required
@require_POST
def add_allergy(request):
    profile = request.user.patient_profile
    form = PatientAllergyForm(request.POST)
    if form.is_valid():
        allergy_instance = form.save(commit=False)
        allergy_instance.patient = profile
        try:
            allergy_instance.save()
            messages.success(request, f"Added allergy: {allergy_instance.allergy.name}")
        except Exception:
            messages.warning(request, "This allergy is already recorded in your profile.")
    else:
        messages.error(request, "Unable to add allergy. Please check your inputs.")
    return redirect('accounts:profile')


@login_required
@patient_required
@require_POST
def delete_allergy(request, pk):
    profile = request.user.patient_profile
    allergy = get_object_or_404(PatientAllergy, pk=pk, patient=profile)
    name = allergy.allergy.name
    allergy.delete()
    messages.info(request, f"Removed allergy: {name}")
    return redirect('accounts:profile')


@login_required
@patient_required
@require_POST
def add_medication(request):
    profile = request.user.patient_profile
    form = PatientMedicationForm(request.POST)
    if form.is_valid():
        med = form.save(commit=False)
        med.patient = profile
        med.save()
        messages.success(request, f"Recorded existing medication: {med.medicine_name}")
    else:
        messages.error(request, "Unable to add medication. Please check your inputs.")
    return redirect('accounts:profile')


@login_required
@patient_required
@require_POST
def delete_medication(request, pk):
    profile = request.user.patient_profile
    med = get_object_or_404(PatientMedication, pk=pk, patient=profile)
    name = med.medicine_name
    med.delete()
    messages.info(request, f"Removed medication record: {name}")
    return redirect('accounts:profile')


@login_required
@patient_required
@require_POST
def add_medical_history(request):
    profile = request.user.patient_profile
    form = PatientMedicalHistoryForm(request.POST)
    if form.is_valid():
        item = form.save(commit=False)
        item.patient = profile
        item.save()
        messages.success(request, f"Added medical condition: {item.condition_name}")
    else:
        messages.error(request, "Unable to add medical history. Please check your inputs.")
    return redirect('accounts:profile')


@login_required
@patient_required
@require_POST
def delete_medical_history(request, pk):
    profile = request.user.patient_profile
    item = get_object_or_404(PatientMedicalHistory, pk=pk, patient=profile)
    name = item.condition_name
    item.delete()
    messages.info(request, f"Removed medical history record: {name}")
    return redirect('accounts:profile')
