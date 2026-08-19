from django.conf import settings
from django.db import models


class Conversation(models.Model):
    report = models.ForeignKey(
        'reports.Report', on_delete=models.CASCADE, related_name='conversations',
        verbose_name='الإعلان'
    )
    claimant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='claimed_conversations',
        verbose_name='المدّعي', help_text='المستخدم الذي يدّعي ملكية الغرض'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ البدء')

    class Meta:
        unique_together = ['report', 'claimant']
        ordering = ['-created_at']
        verbose_name = 'محادثة'
        verbose_name_plural = 'المحادثات'

    def __str__(self):
        return f'{self.claimant} ↔ {self.report}'


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages', verbose_name='المحادثة'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='المرسل'
    )
    body = models.TextField(verbose_name='نص الرسالة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإرسال')
    read = models.BooleanField(default=False, verbose_name='تمت القراءة')

    class Meta:
        ordering = ['created_at']
        verbose_name = 'رسالة'
        verbose_name_plural = 'الرسائل'

    def __str__(self):
        return f'{self.sender}: {self.body[:30]}'
