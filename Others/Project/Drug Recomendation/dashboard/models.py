from django.db import models
from django.conf import settings


class Notification(models.Model):
    LEVEL_CHOICES = (
        ('INFO', 'Information'),
        ('SUCCESS', 'Success'),
        ('WARNING', 'Warning / Precaution'),
        ('DANGER', 'Urgent / Red-Flag'),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='INFO')
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username} - {self.title} ({self.level})"
