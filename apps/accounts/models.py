import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

OTP_VALIDITY_MINUTES = 10
OTP_MAX_ATTEMPTS = 5


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('رقم الهاتف'))
    country = models.ForeignKey(
        'locations.Country', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_('الدولة')
    )
    city = models.ForeignKey(
        'locations.City', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_('المدينة')
    )

    class Meta:
        verbose_name = _('مستخدم')
        verbose_name_plural = _('المستخدمون')

    def __str__(self):
        return self.get_full_name() or self.username


class EmailOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = _('رمز التحقق')
        verbose_name_plural = _('رموز التحقق')

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=OTP_VALIDITY_MINUTES)

    @staticmethod
    def generate_code():
        return f'{secrets.randbelow(1000000):06d}'
