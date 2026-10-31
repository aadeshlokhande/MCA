from django.contrib import admin
from .models import RecommendationRecord, SafetyIssue, DoctorReview


class SafetyIssueInline(admin.TabularInline):
    model = SafetyIssue
    extra = 0
    readonly_fields = ('issue_type', 'severity', 'title', 'description', 'clinical_action_needed')


@admin.register(RecommendationRecord)
class RecommendationRecordAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'disease', 'assessment', 'is_suppressed', 'doctor_approval_status', 'created_at')
    list_filter = ('is_suppressed', 'doctor_approval_status')
    search_fields = ('medicine__name', 'disease__name', 'assessment__patient__user__username')
    inlines = [SafetyIssueInline]


@admin.register(DoctorReview)
class DoctorReviewAdmin(admin.ModelAdmin):
    list_display = ('assessment', 'doctor', 'status', 'reviewed_at')
    list_filter = ('status',)
    search_fields = ('doctor__user__username', 'clinical_diagnosis_notes')
