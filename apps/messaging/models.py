from django.conf import settings
from django.db import models


class Conversation(models.Model):
    report = models.ForeignKey(
        'reports.Report', on_delete=models.CASCADE, related_name='conversations'
    )
    claimant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='claimed_conversations',
        help_text='المستخدم الذي يدّعي ملكية الغرض'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['report', 'claimant']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.claimant} ↔ {self.report}'


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender}: {self.body[:30]}'
