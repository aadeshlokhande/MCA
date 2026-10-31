from django.urls import path
from . import views

app_name = 'symptoms'

urlpatterns = [
    path('checker/', views.symptom_checker, name='symptom_checker'),
    path('api/nlp-extract/', views.nlp_extract_api, name='nlp_extract_api'),
    path('assessment/<int:pk>/', views.assessment_detail, name='assessment_detail'),
    path('history/', views.assessment_history, name='assessment_history'),
]
