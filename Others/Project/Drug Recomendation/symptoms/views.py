from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST, require_GET

from accounts.decorators import patient_required
from .models import SymptomAssessment
from .forms import SymptomCheckerForm
from medical.models import Symptom
from .nlp import nlp_engine
from ml_engine.predictor import predictor
from recommendations.engine import safety_engine
from audit.models import log_audit_event, AuditLog
from dashboard.models import Notification


@login_required
@patient_required
def symptom_checker(request):
    """
    Interactive Symptom Checker:
    - Step 1: Input selection (searchable list, duration, severity, natural language text)
    - Optional Confirmation Screen before ML prediction analysis
    """
    profile = request.user.patient_profile
    all_symptoms = Symptom.objects.all().order_by('category', 'display_name')

    # Group symptoms by category for clean UI tab/accordion organization
    categories = {}
    for sym in all_symptoms:
        cat_display = sym.get_category_display()
        categories.setdefault(cat_display, []).append(sym)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Confirmation step check
        if action == 'confirm':
            # Confirmed submission: create assessment and trigger ML & Safety screening
            form = SymptomCheckerForm(request.POST)
            if form.is_valid():
                assessment = form.save(commit=False)
                assessment.patient = profile

                # Check if emergency symptoms are present
                selected_syms = form.cleaned_data['selected_symptoms']
                emergency_syms = [s for s in selected_syms if s.is_emergency]
                if emergency_syms:
                    assessment.has_emergency_symptoms = True
                    assessment.emergency_notes = f"Emergency symptoms detected: {', '.join(s.display_name for s in emergency_syms)}"

                assessment.save()
                form.save_m2m()

                # Run Machine Learning Disease Prediction Pipeline
                predictions = predictor.predict(assessment, top_k=3)
                log_audit_event(
                    request,
                    AuditLog.Action.PREDICTION_RUN,
                    f"ML Prediction generated {len(predictions)} differential conditions for Assessment #{assessment.id}."
                )

                # Run Clinical Safety & Drug Interaction Screening
                recommendations = safety_engine.screen_assessment_recommendations(assessment)
                log_audit_event(
                    request,
                    AuditLog.Action.RECOMMENDATION_SCREENED,
                    f"Screened {len(recommendations)} candidate medicines for Assessment #{assessment.id}."
                )

                # Create user in-app notification
                Notification.objects.create(
                    recipient=request.user,
                    title="Symptom Assessment Completed",
                    message=f"Assessment #{assessment.id} has been analyzed. Please review the differential conditions and clinical safety screening.",
                    level='SUCCESS',
                    link=f"/symptoms/assessment/{assessment.id}/"
                )

                messages.success(request, "Your symptom assessment has been analyzed by the decision-support pipeline.")
                return redirect('symptoms:assessment_detail', pk=assessment.id)
            else:
                messages.error(request, "Please review the highlighted errors.")
        elif action == 'preview':
            # Pre-analysis confirmation preview
            form = SymptomCheckerForm(request.POST)
            if form.is_valid():
                selected_syms = form.cleaned_data['selected_symptoms']
                raw_text = form.cleaned_data.get('raw_symptom_text', '')
                duration = form.cleaned_data.get('duration_days', 1)
                severity = form.cleaned_data.get('severity', 'MODERATE')
                
                # Check emergency
                emergency_syms = [s for s in selected_syms if s.is_emergency]
                
                context = {
                    'preview_mode': True,
                    'form': form,
                    'selected_symptoms': selected_syms,
                    'raw_text': raw_text,
                    'duration_days': duration,
                    'severity': severity,
                    'emergency_symptoms': emergency_syms,
                    'categories': categories,
                }
                return render(request, 'symptoms/symptom_checker.html', context)
    else:
        form = SymptomCheckerForm()

    context = {
        'form': form,
        'categories': categories,
        'preview_mode': False,
    }
    return render(request, 'symptoms/symptom_checker.html', context)


@login_required
@require_GET
def nlp_extract_api(request):
    """
    AJAX endpoint to extract normalized symptoms from free-text descriptions.
    """
    text = request.GET.get('text', '').strip()
    if not text:
        return JsonResponse({'matched_symptoms': [], 'emergency_flags': []})

    parsed = nlp_engine.parse_symptoms_from_text(text)
    symptoms_data = [
        {
            'id': sym.id,
            'name': sym.name,
            'display_name': sym.display_name,
            'category': sym.get_category_display(),
            'is_emergency': sym.is_emergency
        }
        for sym in parsed['matched_symptoms']
    ]

    return JsonResponse({
        'matched_symptoms': symptoms_data,
        'emergency_flags': parsed['emergency_flags'],
        'negated_mentions': parsed['negated_mentions'],
    })


@login_required
def assessment_detail(request, pk):
    """
    Displays full assessment result:
    - Patient summary
    - Reported symptoms & duration
    - Differential conditions predicted by ML (with calibrated confidence)
    - Screened medicine recommendations & prominent safety warnings
    - Doctor clinical review status and physician notes
    """
    assessment = get_object_or_404(
        SymptomAssessment.objects.select_related('patient__user').prefetch_related(
            'selected_symptoms',
            'predictions__predicted_disease',
            'recommendations__medicine',
            'recommendations__safety_issues',
            'recommendations__disease',
        ),
        pk=pk
    )

    # Permission check: Patient can only view their own; Doctor and Admin can view any
    if request.user.is_patient():
        if assessment.patient.user != request.user:
            log_audit_event(
                request,
                AuditLog.Action.ACCESS_DENIED,
                f"Unauthorized attempt to access Assessment #{pk} belonging to {assessment.patient.user.username}"
            )
            return HttpResponseForbidden("Access Denied: You are not authorized to view this patient assessment.")

    # Doctor review record if present
    doctor_review = getattr(assessment, 'doctor_review', None)

    predictions = assessment.predictions.all().order_by('rank')
    recommendations = assessment.recommendations.all().order_by('is_suppressed', 'medicine__name')

    context = {
        'assessment': assessment,
        'predictions': predictions,
        'recommendations': recommendations,
        'doctor_review': doctor_review,
        'is_doctor': request.user.is_doctor(),
    }
    return render(request, 'symptoms/assessment_detail.html', context)


@login_required
@patient_required
def assessment_history(request):
    """Lists past assessments for the logged-in patient."""
    profile = request.user.patient_profile
    assessments = profile.assessments.prefetch_related(
        'selected_symptoms',
        'predictions__predicted_disease'
    ).order_by('-created_at')

    context = {
        'assessments': assessments,
    }
    return render(request, 'symptoms/assessment_history.html', context)
