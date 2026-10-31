from django.contrib import admin
from .models import MLModelRecord, DatasetRecord, PredictionResult


@admin.register(MLModelRecord)
class MLModelRecordAdmin(admin.ModelAdmin):
    list_display = ('name', 'algorithm', 'version', 'accuracy', 'precision_score', 'recall_score', 'f1_score', 'is_active', 'trained_at')
    list_filter = ('algorithm', 'is_active')
    search_fields = ('name', 'version')


@admin.register(DatasetRecord)
class DatasetRecordAdmin(admin.ModelAdmin):
    list_display = ('name', 'num_records', 'num_symptoms', 'num_diseases', 'is_validated', 'created_at')


@admin.register(PredictionResult)
class PredictionResultAdmin(admin.ModelAdmin):
    list_display = ('assessment', 'predicted_disease', 'confidence_score', 'rank', 'is_primary', 'algorithm_used')
    list_filter = ('is_primary', 'algorithm_used')
    search_fields = ('predicted_disease__name', 'assessment__patient__user__username')
