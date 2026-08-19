from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import get_language


class Category(models.Model):
    name_ar = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, help_text='CSS icon class, e.g. bi-wallet2')

    class Meta:
        ordering = ['name_ar']
        verbose_name_plural = 'Categories'

    @property
    def name(self):
        return self.name_ar if get_language() == 'ar' else self.name_en

    def __str__(self):
        return self.name


class Report(models.Model):
    LOST = 'lost'
    FOUND = 'found'
    TYPE_CHOICES = [
        (LOST, 'مفقود'),
        (FOUND, 'معثور عليه'),
    ]

    OPEN = 'open'
    RESOLVED = 'resolved'
    STATUS_CHOICES = [
        (OPEN, 'قائم'),
        (RESOLVED, 'تم الاسترجاع'),
    ]

    type = models.CharField(max_length=5, choices=TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=OPEN)

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports'
    )
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='reports')
    country = models.ForeignKey('locations.Country', on_delete=models.PROTECT, related_name='reports')
    city = models.ForeignKey(
        'locations.City', on_delete=models.SET_NULL, null=True, blank=True, related_name='reports'
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    location_details = models.CharField(
        max_length=200, blank=True, help_text='مكان الفقدان/العثور بالتفصيل'
    )
    image = models.ImageField(upload_to='reports/%Y/%m/', blank=True, null=True)
    event_date = models.DateField(help_text='تاريخ الفقدان أو العثور')

    verification_question = models.CharField(
        max_length=255, blank=True,
        help_text='سؤال يستخدم للتأكد من ملكية الحاجة قبل التسليم (يظهر لصاحب البلاغ فقط)'
    )

    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('reports:detail', args=[self.pk])
