from .models import Notification


def notification_context(request):
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).order_by('-created_at')[:5]
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        return {
            'unread_notifications': unread_notifications,
            'unread_count': unread_count,
        }
    return {
        'unread_notifications': [],
        'unread_count': 0,
    }
