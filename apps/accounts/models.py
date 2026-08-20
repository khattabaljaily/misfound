from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


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
