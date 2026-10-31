from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('assessment/<int:pk>/pdf/', views.download_assessment_pdf, name='download_assessment_pdf'),
]
