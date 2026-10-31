from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden

from symptoms.models import SymptomAssessment
from .pdf_generator import generate_assessment_pdf
from audit.models import log_audit_event, AuditLog


@login_required
def download_assessment_pdf(request, pk):
    """
    Module 9: Downloadable PDF Assessment Summary Report.
    Includes patient details, reported symptoms, differential predictions,
    medicine info, safety warnings, and doctor review status.
    """
    assessment = get_object_or_404(
        SymptomAssessment.objects.select_related('patient__user').prefetch_related(
            'selected_symptoms',
            'predictions__predicted_disease',
            'recommendations__medicine',
            'recommendations__safety_issues',
        ),
        pk=pk
    )

    # Security check: Patients may only access their own assessments
    if request.user.is_patient() and assessment.patient.user != request.user:
        log_audit_event(
            request,
            AuditLog.Action.ACCESS_DENIED,
            f"Unauthorized PDF download attempt for Assessment #{pk}"
        )
        return HttpResponseForbidden("Access Denied: You cannot download medical records of another patient.")

    pdf_buffer = generate_assessment_pdf(assessment)
    filename = f"Clinical_Assessment_Report_#{assessment.id}.pdf"

    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    log_audit_event(
        request,
        AuditLog.Action.ASSESSMENT_CREATED,
        f"Downloaded PDF Report for Assessment #{assessment.id}."
    )

    return response
