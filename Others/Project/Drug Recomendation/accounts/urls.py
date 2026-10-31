from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/patient/', views.register_patient, name='register_patient'),
    path('register/doctor/', views.register_doctor, name='register_doctor'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('redirect/', views.role_redirect, name='role_redirect'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/allergy/add/', views.add_allergy, name='add_allergy'),
    path('profile/allergy/<int:pk>/delete/', views.delete_allergy, name='delete_allergy'),
    path('profile/medication/add/', views.add_medication, name='add_medication'),
    path('profile/medication/<int:pk>/delete/', views.delete_medication, name='delete_medication'),
    path('profile/history/add/', views.add_medical_history, name='add_medical_history'),
    path('profile/history/<int:pk>/delete/', views.delete_medical_history, name='delete_medical_history'),
]
