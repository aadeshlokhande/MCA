"""
Clinical Medicine Information & Drug Safety Screening Engine.
Applies multi-layered safety screening:
1. Patient allergy cross-reactivity check
2. Drug-Drug interaction check with current medications
3. Patient medical history contraindications check
4. Age-related restriction check
5. Pregnancy & lactation safety check
6. Duplicate active ingredient check
7. Incomplete medical history precaution
Suppresses candidate recommendations when serious hazards are detected.
"""

from typing import List, Dict, Any, Tuple
from django.utils import timezone
from medical.models import (
    Medicine,
    DrugInteraction,
    PatientAllergy,
    PatientMedication,
    PatientMedicalHistory,
)
from symptoms.models import SymptomAssessment
from .models import RecommendationRecord, SafetyIssue


class DrugSafetyEngine:
    """
    Evaluates candidate medicines against patient clinical profile
    to detect safety hazards and determine suppression.
    """

    def screen_assessment_recommendations(self, assessment: SymptomAssessment) -> List[RecommendationRecord]:
        """
        Executes end-to-end recommendation mapping and safety screening
        for an assessed patient.
        """
        patient_profile = assessment.patient
        predictions = assessment.predictions.select_related('predicted_disease').order_by('rank')

        # Clear previously generated recommendations for this assessment
        assessment.recommendations.all().delete()

        # Gather patient context
        allergies = list(patient_profile.allergies.select_related('allergy').all())
        current_meds = list(patient_profile.current_medications.filter(is_active=True).select_related('medicine_reference').all())
        medical_hist = list(patient_profile.medical_history.all())
        patient_age = patient_profile.age
        is_pregnant = patient_profile.is_pregnant

        created_recommendations = []

        # Iterate through predicted differential conditions (primary + secondary)
        for pred in predictions:
            disease = pred.predicted_disease
            candidate_medicines = disease.medicines.all()

            for med in candidate_medicines:
                # Avoid duplicate recommendations for the same medicine in this assessment
                if any(r.medicine_id == med.id for r in created_recommendations):
                    continue

                rec_record = RecommendationRecord.objects.create(
                    assessment=assessment,
                    medicine=med,
                    disease=disease,
                    is_suppressed=False,
                    educational_notes=f"Approved Indication: {med.approved_indications}\nCategory: {med.category}\nSource: {med.source_reference}",
                    doctor_review_required=True,
                    doctor_approval_status='PENDING'
                )

                # Execute safety rules
                detected_issues = self._evaluate_medicine_safety(
                    rec_record=rec_record,
                    medicine=med,
                    allergies=allergies,
                    current_meds=current_meds,
                    medical_hist=medical_hist,
                    patient_age=patient_age,
                    is_pregnant=is_pregnant
                )

                # Check if any issue requires suppression
                severe_issues = [iss for iss in detected_issues if iss.severity in ('SEVERE', 'CONTRAINDICATED')]
                if severe_issues:
                    rec_record.is_suppressed = True
                    rec_record.suppression_reason = " | ".join(f"[{iss.get_issue_type_display()}]: {iss.title}" for iss in severe_issues)
                    rec_record.save(update_fields=['is_suppressed', 'suppression_reason'])

                created_recommendations.append(rec_record)

        return created_recommendations

    def _evaluate_medicine_safety(
        self,
        rec_record: RecommendationRecord,
        medicine: Medicine,
        allergies: List[PatientAllergy],
        current_meds: List[PatientMedication],
        medical_hist: List[PatientMedicalHistory],
        patient_age: int,
        is_pregnant: bool
    ) -> List[SafetyIssue]:
        issues = []

        # -------------------------------------------------------------
        # 1. Known Patient Allergy Check
        # -------------------------------------------------------------
        med_active = medicine.active_ingredient.strip().lower()
        med_generic = medicine.generic_name.strip().lower()

        for pa in allergies:
            allergy_obj = pa.allergy
            allergy_name = allergy_obj.name.lower()
            affected_ingrs = [x.strip().lower() for x in allergy_obj.affected_active_ingredients.split(',') if x.strip()]

            # Direct match or cross-reactivity match
            is_match = (
                med_active in allergy_name or
                allergy_name in med_active or
                med_active in affected_ingrs or
                med_generic in affected_ingrs or
                any(aff in med_active for aff in affected_ingrs)
            )

            if is_match:
                issue = SafetyIssue.objects.create(
                    recommendation=rec_record,
                    issue_type='ALLERGY',
                    severity='CONTRAINDICATED' if pa.reaction_severity in ('SEVERE', 'ANAPHYLAXIS') else 'SEVERE',
                    title=f"Allergy Hazard: Patient has documented allergy to {allergy_obj.name}",
                    description=f"Patient recorded a {pa.get_reaction_severity_display()} allergic reaction to {allergy_obj.name}. The candidate medicine contains active ingredient '{medicine.active_ingredient}', presenting high risk of acute hypersensitivity.",
                    clinical_action_needed="SUPPRESS RECOMMENDATION. Strictly do not administer. Require clinician to select non-cross-reactive pharmacological class."
                )
                issues.append(issue)

        # -------------------------------------------------------------
        # 2. Drug-Drug Interactions with Existing Medications
        # -------------------------------------------------------------
        for cur_med in current_meds:
            cur_med_ref = cur_med.medicine_reference
            cur_name = cur_med.medicine_name.strip().lower()

            # Search in DrugInteraction table (both directions A->B and B->A)
            if cur_med_ref:
                interaction = DrugInteraction.objects.filter(
                    medicine_a=medicine, medicine_b=cur_med_ref
                ).first() or DrugInteraction.objects.filter(
                    medicine_a=cur_med_ref, medicine_b=medicine
                ).first()

                if interaction:
                    sev = 'SEVERE' if interaction.severity in ('SEVERE', 'CONTRAINDICATED') else 'WARNING'
                    issue = SafetyIssue.objects.create(
                        recommendation=rec_record,
                        issue_type='DRUG_INTERACTION',
                        severity=sev,
                        title=f"Drug Interaction: {medicine.generic_name} with ongoing {cur_med_ref.generic_name}",
                        description=f"Interaction Mechanism: {interaction.description}. (Severity: {interaction.get_severity_display()})",
                        clinical_action_needed=interaction.action_required or "Consult qualified clinician for risk-benefit appraisal."
                    )
                    issues.append(issue)

        # -------------------------------------------------------------
        # 3. Patient Medical History Contraindications
        # -------------------------------------------------------------
        med_contraindications = medicine.contraindications.lower()

        for hist in medical_hist:
            cond_name = hist.condition_name.lower()
            # E.g. NSAIDs in Peptic Ulcer, Beta Blockers in Asthma
            if cond_name and (cond_name in med_contraindications or any(word in med_contraindications for word in cond_name.split() if len(word) > 4)):
                issue = SafetyIssue.objects.create(
                    recommendation=rec_record,
                    issue_type='CONTRAINDICATION',
                    severity='SEVERE',
                    title=f"Medical Condition Contraindication: Patient has history of {hist.condition_name}",
                    description=f"The candidate medicine '{medicine.name}' has documented contraindications: '{medicine.contraindications}', which conflicts with patient's active or historical '{hist.condition_name}'.",
                    clinical_action_needed="SUPPRESS RECOMMENDATION. Requires independent physician review and alternative treatment pathway."
                )
                issues.append(issue)

        # -------------------------------------------------------------
        # 4. Age-Related Restrictions
        # -------------------------------------------------------------
        if patient_age is not None:
            if patient_age < medicine.age_minimum:
                issue = SafetyIssue.objects.create(
                    recommendation=rec_record,
                    issue_type='AGE_RESTRICTION',
                    severity='SEVERE',
                    title=f"Age Restriction: Patient is {patient_age} years old (Minimum approved: {medicine.age_minimum} years)",
                    description=f"Administration of {medicine.name} is not clinically approved for patients under {medicine.age_minimum} years of age.",
                    clinical_action_needed="SUPPRESS RECOMMENDATION. Pediatric safety guidelines require age-appropriate alternatives."
                )
                issues.append(issue)
            elif medicine.age_maximum and patient_age > medicine.age_maximum:
                issue = SafetyIssue.objects.create(
                    recommendation=rec_record,
                    issue_type='AGE_RESTRICTION',
                    severity='WARNING',
                    title=f"Geriatric Precaution: Patient is {patient_age} years old (Maximum caution threshold: {medicine.age_maximum} years)",
                    description=f"Age caution applies for patients over {medicine.age_maximum} years with {medicine.name}. Altered pharmacokinetics in elderly patients require dose monitoring.",
                    clinical_action_needed="Requires physician dosage adjustment and monitoring."
                )
                issues.append(issue)

        # -------------------------------------------------------------
        # 5. Pregnancy-Related Precautions
        # -------------------------------------------------------------
        if is_pregnant:
            if medicine.pregnancy_category in ('X', 'D'):
                issue = SafetyIssue.objects.create(
                    recommendation=rec_record,
                    issue_type='PREGNANCY',
                    severity='CONTRAINDICATED' if medicine.pregnancy_category == 'X' else 'SEVERE',
                    title=f"Pregnancy Hazard: Category {medicine.pregnancy_category} Medication",
                    description=f"{medicine.name} is classified under FDA Pregnancy Category {medicine.pregnancy_category}. Warning: {medicine.pregnancy_warning or 'Demonstrated fetal abnormalities or high teratogenic risk'}.",
                    clinical_action_needed="SUPPRESS RECOMMENDATION. Strictly contraindicated in pregnant patients."
                )
                issues.append(issue)
            elif medicine.pregnancy_category == 'C':
                issue = SafetyIssue.objects.create(
                    recommendation=rec_record,
                    issue_type='PREGNANCY',
                    severity='WARNING',
                    title="Pregnancy Precaution: Category C Medication",
                    description=f"{medicine.name} has FDA Pregnancy Category C classification. Use only if clinical potential benefit clearly justifies risk to fetus.",
                    clinical_action_needed="Mandatory obstetrician / physician evaluation before consideration."
                )
                issues.append(issue)

        # -------------------------------------------------------------
        # 6. Duplicate Active Ingredient Exposure
        # -------------------------------------------------------------
        for cur_med in current_meds:
            cur_med_active = cur_med.medicine_reference.active_ingredient.lower() if cur_med.medicine_reference else cur_med.medicine_name.lower()
            if med_active and (med_active in cur_med_active or cur_med_active in med_active):
                issue = SafetyIssue.objects.create(
                    recommendation=rec_record,
                    issue_type='DUPLICATE_INGREDIENT',
                    severity='SEVERE',
                    title=f"Duplicate Ingredient Hazard: Patient already taking '{cur_med.medicine_name}'",
                    description=f"Patient profile indicates active intake of '{cur_med.medicine_name}'. Both preparations share active ingredient '{medicine.active_ingredient}', risking accidental cumulative overdose.",
                    clinical_action_needed="SUPPRESS RECOMMENDATION to prevent toxicity from duplicate ingredient accumulation."
                )
                issues.append(issue)

        # -------------------------------------------------------------
        # 7. Incomplete Medical History Precaution
        # -------------------------------------------------------------
        if not allergies and not current_meds and not medical_hist:
            issue = SafetyIssue.objects.create(
                recommendation=rec_record,
                issue_type='MISSING_DATA',
                severity='WARNING',
                title="Incomplete Medical History Notice",
                description="Patient profile contains no recorded allergies, current medications, or previous history. Safety screening cannot verify unrecorded clinical interactions.",
                clinical_action_needed="Ensure patient updates their complete medical history before confirming recommendations."
            )
            issues.append(issue)

        return issues


# Singleton safety engine instance
safety_engine = DrugSafetyEngine()
