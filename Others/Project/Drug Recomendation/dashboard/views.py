import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseForbidden

from accounts.decorators import patient_required, doctor_required, admin_required
from accounts.models import PatientProfile, DoctorProfile
from symptoms.models import SymptomAssessment
from recommendations.models import RecommendationRecord, DoctorReview
from medical.models import Medicine
from ml_engine.models import MLModelRecord, DatasetRecord
from audit.models import AuditLog, log_audit_event
from .models import Notification


@login_required
@patient_required
def patient_dashboard(request):
    """
    Module 7: Patient Dashboard
    - Profile summary
    - Recent symptom assessments
    - Allergy & medication summary
    - Quick access to Symptom Checker
    """
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    recent_assessments = profile.assessments.prefetch_related(
        'selected_symptoms',
        'predictions__predicted_disease'
    ).order_by('-created_at')[:5]

    allergies = profile.allergies.select_related('allergy').all()
    medications = profile.current_medications.filter(is_active=True)
    history = profile.medical_history.all()

    total_assessments = profile.assessments.count()
    has_emergency_recent = profile.assessments.filter(has_emergency_symptoms=True).exists()

    context = {
        'profile': profile,
        'recent_assessments': recent_assessments,
        'allergies': allergies,
        'medications': medications,
        'history': history,
        'total_assessments': total_assessments,
        'has_emergency_recent': has_emergency_recent,
    }
    return render(request, 'dashboard/patient_dashboard.html', context)


@login_required
@doctor_required
def doctor_dashboard(request):
    """
    Module 8: Doctor Dashboard
    - View patient assessments
    - Filter by status (Pending Review, Reviewed, etc.)
    - Clinical triage overview
    """
    doctor_profile = request.user.doctor_profile
    status_filter = request.GET.get('status', 'ALL')

    assessments = SymptomAssessment.objects.select_related(
        'patient__user'
    ).prefetch_related(
        'selected_symptoms',
        'predictions__predicted_disease',
        'recommendations'
    ).order_by('-created_at')

    if status_filter == 'PENDING':
        assessments = assessments.filter(doctor_review__isnull=True)
    elif status_filter == 'REVIEWED':
        assessments = assessments.filter(doctor_review__isnull=False)

    pending_count = SymptomAssessment.objects.filter(doctor_review__isnull=True).count()
    reviewed_count = SymptomAssessment.objects.filter(doctor_review__isnull=False).count()
    total_count = SymptomAssessment.objects.count()

    context = {
        'doctor_profile': doctor_profile,
        'assessments': assessments,
        'pending_count': pending_count,
        'reviewed_count': reviewed_count,
        'total_count': total_count,
        'status_filter': status_filter,
    }
    return render(request, 'dashboard/doctor_dashboard.html', context)


@login_required
@doctor_required
def doctor_review_assessment(request, pk):
    """
    Doctor Clinical Review Workspace:
    - Examine reported symptoms & medical history
    - Review ML differential diagnosis
    - Review medicine recommendations & drug safety warnings
    - Record professional notes, approve, reject, or modify recommendations
    """
    doctor_profile = request.user.doctor_profile
    assessment = get_object_or_404(
        SymptomAssessment.objects.select_related('patient__user').prefetch_related(
            'selected_symptoms',
            'predictions__predicted_disease',
            'recommendations__medicine',
            'recommendations__safety_issues',
            'recommendations__disease',
            'patient__allergies__allergy',
            'patient__current_medications',
            'patient__medical_history',
        ),
        pk=pk
    )

    existing_review = getattr(assessment, 'doctor_review', None)

    if request.method == 'POST':
        status = request.POST.get('status', 'APPROVED')
        clinical_notes = request.POST.get('clinical_diagnosis_notes', '').strip()
        patient_instructions = request.POST.get('patient_instructions', '').strip()
        modifications = request.POST.get('clinical_modifications', '').strip()
        follow_up = request.POST.get('follow_up_advice', '').strip()
        approved_med_ids = request.POST.getlist('approved_medicines')

        if not clinical_notes or not patient_instructions:
            messages.error(request, "Clinical diagnostic notes and patient instructions are mandatory.")
        else:
            if existing_review:
                review = existing_review
                review.status = status
                review.clinical_diagnosis_notes = clinical_notes
                review.patient_instructions = patient_instructions
                review.clinical_modifications = modifications
                review.follow_up_advice = follow_up
                review.doctor = doctor_profile
                review.save()
            else:
                review = DoctorReview.objects.create(
                    assessment=assessment,
                    doctor=doctor_profile,
                    status=status,
                    clinical_diagnosis_notes=clinical_notes,
                    patient_instructions=patient_instructions,
                    clinical_modifications=modifications,
                    follow_up_advice=follow_up
                )

            # Update approved medicines
            review.approved_medicines.set(Medicine.objects.filter(id__in=approved_med_ids))

            # Update recommendation records approval status
            for rec in assessment.recommendations.all():
                if str(rec.medicine_id) in approved_med_ids:
                    rec.doctor_approval_status = 'APPROVED'
                else:
                    rec.doctor_approval_status = 'REJECTED' if status == 'REJECTED' else 'MODIFIED'
                rec.reviewed_by = doctor_profile
                rec.reviewed_at = review.reviewed_at
                rec.save()

            assessment.status = 'REVIEWED'
            assessment.save()

            # Create notification for the patient
            Notification.objects.create(
                recipient=assessment.patient.user,
                title="Doctor Review Completed",
                message=f"Dr. {doctor_profile.user.get_full_name()} has reviewed your symptom assessment #{assessment.id}.",
                level='SUCCESS',
                link=f"/symptoms/assessment/{assessment.id}/"
            )

            log_audit_event(
                request,
                AuditLog.Action.DOCTOR_REVIEW,
                f"Doctor Dr. {doctor_profile.user.username} submitted review for Assessment #{assessment.id} with status {status}."
            )

            messages.success(request, f"Clinical review for Assessment #{assessment.id} saved successfully.")
            return redirect('dashboard:doctor_review_assessment', pk=assessment.id)

    predictions = assessment.predictions.all().order_by('rank')
    recommendations = assessment.recommendations.all().order_by('is_suppressed', 'medicine__name')

    context = {
        'assessment': assessment,
        'predictions': predictions,
        'recommendations': recommendations,
        'existing_review': existing_review,
        'patient': assessment.patient,
    }
    return render(request, 'dashboard/doctor_review.html', context)


@login_required
@admin_required
def admin_dashboard(request):
    """
    Module 10 & ML Evaluation Analytics Dashboard:
    - Displays trained models comparison (Accuracy, Precision, Recall, F1)
    - Confusion matrix visualizer
    - Dataset validation metrics
    - System audit logs and security events
    """
    models_records = MLModelRecord.objects.all().order_by('-is_active', '-accuracy')
    dataset_records = DatasetRecord.objects.all().order_by('-created_at')
    recent_logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:20]

    # Model comparison chart data (for Chart.js)
    chart_labels = []
    accuracy_data = []
    precision_data = []
    recall_data = []
    f1_data = []

    for m in models_records:
        chart_labels.append(m.name)
        accuracy_data.append(round(m.accuracy * 100, 2))
        precision_data.append(round(m.precision_score * 100, 2))
        recall_data.append(round(m.recall_score * 100, 2))
        f1_data.append(round(m.f1_score * 100, 2))

    chart_payload = {
        'labels': chart_labels,
        'accuracy': accuracy_data,
        'precision': precision_data,
        'recall': recall_data,
        'f1': f1_data,
    }

    # Confusion Matrix of Active Model
    active_model = models_records.filter(is_active=True).first()
    confusion_matrix_data = []
    if active_model and active_model.confusion_matrix_json:
        try:
            confusion_matrix_data = json.loads(active_model.confusion_matrix_json)
        except Exception:
            confusion_matrix_data = []

    context = {
        'models_records': models_records,
        'dataset_records': dataset_records,
        'recent_logs': recent_logs,
        'active_model': active_model,
        'chart_payload_json': json.dumps(chart_payload),
        'confusion_matrix_json': json.dumps(confusion_matrix_data),
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
@require_POST
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save()
    return JsonResponse({'status': 'ok'})
