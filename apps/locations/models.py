from django.db import models
from django.utils.translation import get_language


class Country(models.Model):
    name_ar = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    code = models.CharField(max_length=2, unique=True)  # ISO 3166-1 alpha-2

    class Meta:
        ordering = ['name_ar']
        verbose_name_plural = 'Countries'

    @property
    def name(self):
        return self.name_ar if get_language() == 'ar' else self.name_en

    def __str__(self):
        return self.name


class City(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities')
    name_ar = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)

    class Meta:
        ordering = ['name_ar']
        verbose_name_plural = 'Cities'

    @property
    def name(self):
        return self.name_ar if get_language() == 'ar' else self.name_en

    def __str__(self):
        return f'{self.name}, {self.country.name}'
