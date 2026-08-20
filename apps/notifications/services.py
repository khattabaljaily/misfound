from django.utils import timezone

from .models import Notification


def notify(user, type, title, body, url):
    """Creates a notification, or if an unread one already exists for this
    user/type/url (e.g. several new messages in the same conversation before
    it's read), refreshes it in place instead of piling up duplicates."""
    existing = Notification.objects.filter(user=user, type=type, url=url, is_read=False).first()
    if existing:
        existing.title = title
        existing.body = body
        existing.created_at = timezone.now()
        existing.save(update_fields=['title', 'body', 'created_at'])
        return existing
    return Notification.objects.create(user=user, type=type, title=title, body=body, url=url)
