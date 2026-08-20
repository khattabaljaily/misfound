from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    MATCH = 'match'
    MESSAGE = 'message'
    RESOLVED_REMINDER = 'resolved_reminder'
    TYPE_CHOICES = [
        (MATCH, _('تطابق محتمل')),
        (MESSAGE, _('رسالة جديدة')),
        (RESOLVED_REMINDER, _('تذكير بالاسترجاع')),
    ]

    ICONS = {
        MATCH: 'bi-stars',
        MESSAGE: 'bi-chat-dots',
        RESOLVED_REMINDER: 'bi-check-circle',
    }

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications',
        verbose_name=_('المستخدم')
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name=_('النوع'))
    title = models.CharField(max_length=200, verbose_name=_('العنوان'))
    body = models.CharField(max_length=300, blank=True, verbose_name=_('التفاصيل'))
    url = models.CharField(max_length=300, verbose_name=_('الرابط'))
    is_read = models.BooleanField(default=False, verbose_name=_('تمت القراءة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('إشعار')
        verbose_name_plural = _('الإشعارات')

    def __str__(self):
        return f'{self.user}: {self.title}'

    @property
    def icon(self):
        return self.ICONS.get(self.type, 'bi-bell')
