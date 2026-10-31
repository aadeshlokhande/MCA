from django.contrib import admin
from .models import SymptomAssessment


@admin.register(SymptomAssessment)
class SymptomAssessmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'duration_days', 'severity', 'has_emergency_symptoms', 'status', 'created_at')
    list_filter = ('severity', 'has_emergency_symptoms', 'status')
    search_fields = ('patient__user__username', 'raw_symptom_text')
    filter_horizontal = ('selected_symptoms',)
