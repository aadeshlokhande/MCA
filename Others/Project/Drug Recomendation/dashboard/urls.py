from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('patient/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/review/<int:pk>/', views.doctor_review_assessment, name='doctor_review_assessment'),
    path('admin-metrics/', views.admin_dashboard, name='admin_dashboard'),
    path('notification/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
]
