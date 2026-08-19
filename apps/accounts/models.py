from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, verbose_name='رقم الهاتف')
    country = models.ForeignKey(
        'locations.Country', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='الدولة'
    )
    city = models.ForeignKey(
        'locations.City', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='المدينة'
    )

    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمون'

    def __str__(self):
        return self.get_full_name() or self.username
