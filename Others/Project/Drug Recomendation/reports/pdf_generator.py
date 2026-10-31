"""
Clinical PDF Assessment Report Generator using ReportLab.
Produces a formatted, auditable PDF summary including:
- Clinical header & patient demographics
- Reported symptoms, duration, and severity
- AI Differential Diagnosis predictions with calibrated confidence
- Screened medicine educational summaries & active safety warnings
- Suppressed recommendations and contraindication alerts
- Doctor clinical review, notes, endorsements, and signature block
- Academic prototype disclaimers
"""

import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from symptoms.models import SymptomAssessment


def generate_assessment_pdf(assessment: SymptomAssessment) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#172B45')
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#5E6C84')
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#3984E8'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#172B45')
    )
    warning_style = ParagraphStyle(
        'WarningBox',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#E05252')
    )
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Italic'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#718096')
    )

    elements = []

    # 1. Header
    elements.append(Paragraph("AI-Based Drug Recommendation System", title_style))
    elements.append(Paragraph("Clinical Decision-Support & Medication Safety Assessment Report", subtitle_style))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#3984E8'), spaceAfter=12))

    # 2. Patient Demographics & Assessment Metadata Table
    patient = assessment.patient
    user = patient.user
    
    patient_data = [
        [
            Paragraph(f"<b>Patient Name:</b> {user.get_full_name() or user.username}", body_style),
            Paragraph(f"<b>Assessment ID:</b> #{assessment.id}", body_style),
        ],
        [
            Paragraph(f"<b>Age / Gender:</b> {patient.age or 'N/A'} yrs / {patient.get_gender_display()}", body_style),
            Paragraph(f"<b>Date:</b> {assessment.created_at.strftime('%B %d, %Y %H:%M UTC')}", body_style),
        ],
        [
            Paragraph(f"<b>Blood Group:</b> {patient.blood_group or 'Not Recorded'}", body_style),
            Paragraph(f"<b>Clinical Status:</b> {assessment.get_status_display()}", body_style),
        ],
    ]

    p_table = Table(patient_data, colWidths=[270, 270])
    p_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F5F8FC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#DCE6F2')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(p_table)
    elements.append(Spacer(1, 10))

    # Emergency Banner if detected
    if assessment.has_emergency_symptoms:
        em_banner = [
            [Paragraph("<b>CRITICAL RED-FLAG SYMPTOMS DETECTED</b><br/>One or more emergency symptoms were reported. This patient requires prompt in-person clinical or emergency medical evaluation.", warning_style)]
        ]
        em_table = Table(em_banner, colWidths=[540])
        em_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FDE8E8')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E05252')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(em_table)
        elements.append(Spacer(1, 10))

    # 3. Reported Symptoms
    elements.append(Paragraph("1. Reported Symptoms & History", h2_style))
    syms_list = ", ".join(s.display_name for s in assessment.selected_symptoms.all())
    syms_data = [
        [Paragraph(f"<b>Selected Symptoms:</b> {syms_list}", body_style)],
        [Paragraph(f"<b>Duration:</b> {assessment.duration_days} days &nbsp;|&nbsp; <b>Reported Severity:</b> {assessment.get_severity_display()}", body_style)],
    ]
    if assessment.raw_symptom_text:
        syms_data.append([Paragraph(f"<b>Patient's Own Description:</b> \"{assessment.raw_symptom_text}\"", body_style)])

    s_table = Table(syms_data, colWidths=[540])
    s_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFFFFF')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#EEF3F8')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(s_table)
    elements.append(Spacer(1, 10))

    # 4. Machine Learning Differential Diagnosis
    elements.append(Paragraph("2. AI Differential Condition Predictions", h2_style))
    predictions = list(assessment.predictions.all().order_by('rank'))

    if predictions:
        pred_table_data = [
            [
                Paragraph("<b>Rank</b>", body_style),
                Paragraph("<b>Possible Condition</b>", body_style),
                Paragraph("<b>Urgency</b>", body_style),
                Paragraph("<b>Calibrated Confidence</b>", body_style),
            ]
        ]
        for p in predictions:
            pred_table_data.append([
                Paragraph(f"#{p.rank}", body_style),
                Paragraph(f"<b>{p.predicted_disease.name}</b> (ICD: {p.predicted_disease.code or 'N/A'})", body_style),
                Paragraph(p.predicted_disease.get_urgency_level_display(), body_style),
                Paragraph(f"{p.confidence_score * 100:.1f}%", body_style),
            ])
        pred_table = Table(pred_table_data, colWidths=[40, 240, 160, 100])
        pred_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EEF3F8')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DCE6F2')),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(pred_table)
    else:
        elements.append(Paragraph("No ML differential predictions recorded.", body_style))

    elements.append(Spacer(1, 10))

    # 5. Screened Medicine Information & Drug Safety
    elements.append(Paragraph("3. Screened Medicine Information & Safety Alerts", h2_style))
    recs = list(assessment.recommendations.all().order_by('is_suppressed', 'medicine__name'))

    if recs:
        med_table_data = [
            [
                Paragraph("<b>Medicine</b>", body_style),
                Paragraph("<b>Classification / Indication</b>", body_style),
                Paragraph("<b>Safety Status & Review Decision</b>", body_style),
            ]
        ]
        for r in recs:
            status_text = f"<b>{r.get_doctor_approval_status_display()}</b>"
            if r.is_suppressed:
                status_text += f"<br/><font color='#E05252'><b>[SUPPRESSED]</b> {r.suppression_reason}</font>"
            else:
                status_text += "<br/><font color='#22A06B'>Passes baseline screening</font>"

            med_table_data.append([
                Paragraph(f"<b>{r.medicine.name}</b><br/>{r.medicine.generic_name} ({'Rx Only' if r.medicine.is_prescription_only else 'OTC'})", body_style),
                Paragraph(f"{r.medicine.category}<br/><i>{r.medicine.approved_indications}</i>", body_style),
                Paragraph(status_text, body_style),
            ])
        med_table = Table(med_table_data, colWidths=[150, 210, 180])
        med_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EEF3F8')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DCE6F2')),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(med_table)
    else:
        elements.append(Paragraph("No verified medicine data available for the indicated conditions.", body_style))

    elements.append(Spacer(1, 10))

    # 6. Doctor Review & Clinical Endorsement Block
    elements.append(Paragraph("4. Healthcare Professional Review", h2_style))
    doc_review = getattr(assessment, 'doctor_review', None)

    if doc_review:
        doctor_user = doc_review.doctor.user
        doc_data = [
            [Paragraph(f"<b>Reviewing Clinician:</b> Dr. {doctor_user.get_full_name()} ({doc_review.doctor.specialization})", body_style)],
            [Paragraph(f"<b>Clinical Diagnostic Impression:</b> {doc_review.clinical_diagnosis_notes}", body_style)],
            [Paragraph(f"<b>Patient Instructions:</b> {doc_review.patient_instructions}", body_style)],
        ]
        if doc_review.clinical_modifications:
            doc_data.append([Paragraph(f"<b>Clinical Modifications:</b> {doc_review.clinical_modifications}", body_style)])
        if doc_review.follow_up_advice:
            doc_data.append([Paragraph(f"<b>Follow-Up Guidance:</b> {doc_review.follow_up_advice}", body_style)])

        doc_data.append([Paragraph(f"<i>Electronically authenticated on {doc_review.reviewed_at.strftime('%Y-%m-%d %H:%M UTC')} | License #{doc_review.doctor.license_number}</i>", disclaimer_style)])

        doc_table = Table(doc_data, colWidths=[540])
        doc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F5F8FC')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#22A06B')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(doc_table)
    else:
        pending_data = [
            [Paragraph("<b>STATUS: PENDING INDEPENDENT CLINICAL REVIEW</b><br/>This assessment has not yet been reviewed or signed off by a qualified physician. Predictions must not be treated as a confirmed diagnosis, and medicine details are solely for clinical decision-support review.", warning_style)]
        ]
        pend_table = Table(pending_data, colWidths=[540])
        pend_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFFBEB')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E9A23B')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(pend_table)

    elements.append(Spacer(1, 15))

    # 7. Regulatory & Academic Decision-Support Disclaimer
    disclaimer_text = (
        "<b>ACADEMIC CLINICAL DECISION-SUPPORT PROTOTYPE DISCLAIMER:</b> "
        "This software application is an academic research prototype designed to assist healthcare professionals in clinical decision evaluation. "
        "It does NOT replace professional medical judgment, in-person clinical examination, or laboratory diagnostics. "
        "Predictions are statistical approximations and must never be interpreted as confirmed medical diagnoses or autonomous prescriptions."
    )
    elements.append(Paragraph(disclaimer_text, disclaimer_style))

    # Build document
    doc.build(elements)
    buffer.seek(0)
    return buffer
