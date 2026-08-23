from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class PageVisit(models.Model):
    DESKTOP = 'desktop'
    MOBILE = 'mobile'
    TABLET = 'tablet'
    OTHER = 'other'
    DEVICE_CHOICES = [
        (DESKTOP, _('كمبيوتر')),
        (MOBILE, _('جوال')),
        (TABLET, _('تابلت')),
        (OTHER, _('أخرى')),
    ]

    path = models.CharField(max_length=255)
    visitor_id = models.CharField(max_length=32, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    country_code = models.CharField(max_length=2, blank=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    referer = models.CharField(max_length=255, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    device_type = models.CharField(max_length=10, choices=DEVICE_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f'{self.path} @ {self.created_at:%Y-%m-%d %H:%M}'
