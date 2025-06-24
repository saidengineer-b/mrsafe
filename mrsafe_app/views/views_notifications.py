from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.timezone import localtime
from mrsafe_app.models import Notification

def serialize_notification(n):
    return {
        "id": n.id,
        "message": n.message,
        "type": n.notification_type,
        "is_read": n.is_read,
        "created_at": localtime(n.created_at).strftime("%Y-%m-%d %H:%M"),
    }

@login_required
def get_notifications(request):
    """Fetch unread notifications for the logged-in user."""
    limit = int(request.GET.get("limit", 20))  # Optional: ?limit=10

    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by("-created_at")[:limit]

    data = [serialize_notification(n) for n in notifications]
    return JsonResponse({
        "success": True,
        "notifications": data,
        "unread_count": notifications.count(),
    })


@login_required
def mark_notification_as_read(request, notification_id):
    """Mark a single notification as read."""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    if not notification.is_read:
        notification.is_read = True
        notification.save()
    return JsonResponse({"success": True})


@login_required
def mark_all_as_read(request):
    """Mark all unread notifications as read for the user."""
    updated_count = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({"success": True, "updated": updated_count})


@login_required
def clear_notifications(request):
    """Delete all notifications for the user."""
    count, _ = Notification.objects.filter(user=request.user).delete()
    return JsonResponse({"success": True, "deleted": count})

from django.core.management.base import BaseCommand
from mrsafe_app.models import Notification
from datetime import timedelta
from django.utils.timezone import now

class Command(BaseCommand):
    help = "Deletes notifications older than 7 days"

    def handle(self, *args, **kwargs):
        cutoff = now() - timedelta(days=7)
        deleted_count, _ = Notification.objects.filter(created_at__lt=cutoff).delete()
        self.stdout.write(self.style.SUCCESS(f"✅ Deleted {deleted_count} old notifications."))


###################################################################################################

