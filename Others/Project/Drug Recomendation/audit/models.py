from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    class Action(models.TextChoices):
        LOGIN = 'LOGIN', 'User Login'
        LOGOUT = 'LOGOUT', 'User Logout'
        REGISTRATION = 'REGISTRATION', 'User Registration'
        ASSESSMENT_CREATED = 'ASSESSMENT_CREATED', 'Symptom Assessment Created'
        PREDICTION_RUN = 'PREDICTION_RUN', 'AI Prediction Pipeline Executed'
        RECOMMENDATION_SCREENED = 'RECOMMENDATION_SCREENED', 'Drug Safety Screening Executed'
        DOCTOR_REVIEW = 'DOCTOR_REVIEW', 'Doctor Clinical Review Submitted'
        DATASET_SEEDED = 'DATASET_SEEDED', 'Medical Dataset Seeded/Updated'
        MODEL_TRAINED = 'MODEL_TRAINED', 'ML Model Trained and Evaluated'
        ACCESS_DENIED = 'ACCESS_DENIED', 'Unauthorized Access Attempt Denied'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=40, choices=Action.choices)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]

    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous"
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.action} by {user_str}"


def log_audit_event(request, action, details="", user=None):
    """Helper utility to safely capture and log audit trails without exposing passwords."""
    try:
        ip = None
        user_agent = ""
        current_user = user

        if request:
            x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded:
                ip = x_forwarded.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            if not current_user and request.user.is_authenticated:
                current_user = request.user

        AuditLog.objects.create(
            user=current_user,
            action=action,
            ip_address=ip,
            user_agent=user_agent,
            details=details
        )
    except Exception:
        # Never break application flow if audit logging encounters non-fatal DB errors
        pass
