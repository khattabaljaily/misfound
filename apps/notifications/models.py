from django.conf import settings
from django.db import models


class Notification(models.Model):
    MATCH = 'match'
    MESSAGE = 'message'
    RESOLVED_REMINDER = 'resolved_reminder'
    TYPE_CHOICES = [
        (MATCH, 'تطابق محتمل'),
        (MESSAGE, 'رسالة جديدة'),
        (RESOLVED_REMINDER, 'تذكير بالاسترجاع'),
    ]

    ICONS = {
        MATCH: 'bi-stars',
        MESSAGE: 'bi-chat-dots',
        RESOLVED_REMINDER: 'bi-check-circle',
    }

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications',
        verbose_name='المستخدم'
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='النوع')
    title = models.CharField(max_length=200, verbose_name='العنوان')
    body = models.CharField(max_length=300, blank=True, verbose_name='التفاصيل')
    url = models.CharField(max_length=300, verbose_name='الرابط')
    is_read = models.BooleanField(default=False, verbose_name='تمت القراءة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'إشعار'
        verbose_name_plural = 'الإشعارات'

    def __str__(self):
        return f'{self.user}: {self.title}'

    @property
    def icon(self):
        return self.ICONS.get(self.type, 'bi-bell')
