from django.conf import settings
from django.db import models


class PageVisit(models.Model):
    path = models.CharField(max_length=255)
    visitor_id = models.CharField(max_length=32, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    referer = models.CharField(max_length=255, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f'{self.path} @ {self.created_at:%Y-%m-%d %H:%M}'
