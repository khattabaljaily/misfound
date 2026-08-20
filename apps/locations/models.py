from django.db import models
from django.utils.translation import get_language, gettext_lazy as _


class Country(models.Model):
    name_ar = models.CharField(max_length=100, verbose_name=_('الاسم بالعربية'))
    name_en = models.CharField(max_length=100, verbose_name=_('الاسم بالإنجليزية'))
    code = models.CharField(max_length=2, unique=True, verbose_name=_('رمز الدولة'))  # ISO 3166-1 alpha-2

    class Meta:
        ordering = ['name_ar']
        verbose_name = _('دولة')
        verbose_name_plural = _('الدول')

    @property
    def name(self):
        return self.name_ar if get_language() == 'ar' else self.name_en

    def __str__(self):
        return self.name


class City(models.Model):
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name='cities', verbose_name=_('الدولة')
    )
    name_ar = models.CharField(max_length=100, verbose_name=_('الاسم بالعربية'))
    name_en = models.CharField(max_length=100, verbose_name=_('الاسم بالإنجليزية'))

    class Meta:
        ordering = ['name_ar']
        verbose_name = _('مدينة')
        verbose_name_plural = _('المدن')

    @property
    def name(self):
        return self.name_ar if get_language() == 'ar' else self.name_en

    def __str__(self):
        return f'{self.name}, {self.country.name}'
