from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Conversation(models.Model):
    report = models.ForeignKey(
        'reports.Report', on_delete=models.CASCADE, related_name='conversations',
        verbose_name=_('الإعلان')
    )
    claimant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='claimed_conversations',
        verbose_name=_('المدّعي'), help_text=_('المستخدم الذي يدّعي ملكية الغرض')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ البدء'))

    class Meta:
        unique_together = ['report', 'claimant']
        ordering = ['-created_at']
        verbose_name = _('محادثة')
        verbose_name_plural = _('المحادثات')

    def __str__(self):
        return f'{self.claimant} ↔ {self.report}'


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages', verbose_name=_('المحادثة')
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('المرسل')
    )
    body = models.TextField(verbose_name=_('نص الرسالة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإرسال'))
    read = models.BooleanField(default=False, verbose_name=_('تمت القراءة'))

    class Meta:
        ordering = ['created_at']
        verbose_name = _('رسالة')
        verbose_name_plural = _('الرسائل')

    def __str__(self):
        return f'{self.sender}: {self.body[:30]}'
