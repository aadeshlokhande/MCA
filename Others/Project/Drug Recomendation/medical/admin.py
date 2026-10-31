from django.contrib import admin
from .models import (
    Symptom,
    Disease,
    Medicine,
    DrugInteraction,
    Allergy,
    PatientAllergy,
    PatientMedication,
    PatientMedicalHistory,
)


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name', 'category', 'is_emergency')
    list_filter = ('category', 'is_emergency')
    search_fields = ('name', 'display_name', 'synonyms', 'description')


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'urgency_level', 'specialist_type')
    list_filter = ('urgency_level', 'specialist_type')
    search_fields = ('name', 'code', 'description')
    filter_horizontal = ('symptoms',)


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'generic_name', 'category', 'is_prescription_only', 'pregnancy_category', 'age_minimum')
    list_filter = ('is_prescription_only', 'pregnancy_category', 'category')
    search_fields = ('name', 'generic_name', 'active_ingredient', 'approved_indications')
    filter_horizontal = ('indicated_diseases',)


@admin.register(DrugInteraction)
class DrugInteractionAdmin(admin.ModelAdmin):
    list_display = ('medicine_a', 'medicine_b', 'severity')
    list_filter = ('severity',)
    search_fields = ('medicine_a__name', 'medicine_b__name', 'description')


@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ('name', 'allergy_type')
    list_filter = ('allergy_type',)
    search_fields = ('name', 'affected_active_ingredients')


@admin.register(PatientAllergy)
class PatientAllergyAdmin(admin.ModelAdmin):
    list_display = ('patient', 'allergy', 'reaction_severity')
    list_filter = ('reaction_severity',)
    search_fields = ('patient__user__username', 'allergy__name')


@admin.register(PatientMedication)
class PatientMedicationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'medicine_name', 'dosage', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('patient__user__username', 'medicine_name')


@admin.register(PatientMedicalHistory)
class PatientMedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ('patient', 'condition_name', 'status')
    list_filter = ('status',)
    search_fields = ('patient__user__username', 'condition_name')
