from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PatientProfile, DoctorProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_verified', 'is_staff')
    list_filter = ('role', 'is_verified', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Clinical Role & Credentials', {'fields': ('role', 'phone_number', 'is_verified')}),
    )


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'gender', 'blood_group', 'is_pregnant', 'created_at')
    list_filter = ('gender', 'blood_group', 'is_pregnant')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'emergency_contact_name')


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'specialization', 'years_of_experience', 'is_approved')
    list_filter = ('specialization', 'is_approved')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'license_number')
