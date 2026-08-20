from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import get_language


class Category(models.Model):
    name_ar = models.CharField(max_length=100, verbose_name='الاسم بالعربية')
    name_en = models.CharField(max_length=100, verbose_name='الاسم بالإنجليزية')
    icon = models.CharField(
        max_length=50, blank=True, verbose_name='الأيقونة',
        help_text='CSS icon class, e.g. bi-wallet2'
    )
    priority = models.PositiveSmallIntegerField(default=999, verbose_name='ترتيب')

    class Meta:
        ordering = ['priority', 'name_ar']
        verbose_name = 'تصنيف'
        verbose_name_plural = 'التصنيفات'

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

    type = models.CharField(max_length=5, choices=TYPE_CHOICES, verbose_name='نوع الإعلان')
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=OPEN, verbose_name='الحالة'
    )

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports',
        verbose_name='صاحب الإعلان'
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='reports', verbose_name='التصنيف'
    )
    country = models.ForeignKey(
        'locations.Country', on_delete=models.PROTECT, related_name='reports', verbose_name='الدولة'
    )
    city = models.ForeignKey(
        'locations.City', on_delete=models.SET_NULL, null=True, blank=True, related_name='reports',
        verbose_name='المدينة'
    )

    title = models.CharField(max_length=200, verbose_name='العنوان')
    description = models.TextField(verbose_name='الوصف')
    location_details = models.CharField(
        max_length=200, blank=True, verbose_name='تفاصيل المكان',
        help_text='مكان الفقدان/العثور بالتفصيل'
    )
    image = models.ImageField(upload_to='reports/%Y/%m/', blank=True, null=True, verbose_name='الصورة')
    event_date = models.DateField(verbose_name='تاريخ الفقدان أو العثور')

    verification_question = models.CharField(
        max_length=255, blank=True, verbose_name='سؤال التحقق',
        help_text='سؤال يُستخدم للتحقق من ملكية الغرض قبل التسليم (يظهر لصاحب الإعلان فقط)'
    )

    views = models.PositiveIntegerField(default=0, verbose_name='عدد المشاهدات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'إعلان'
        verbose_name_plural = 'الإعلانات'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('reports:detail', args=[self.pk])


class Match(models.Model):
    """An AI-suggested pairing between a lost report and a found report
    that plausibly describe the same item."""

    lost_report = models.ForeignKey(
        Report, on_delete=models.CASCADE, related_name='matches_as_lost',
        limit_choices_to={'type': Report.LOST}, verbose_name='الإعلان المفقود'
    )
    found_report = models.ForeignKey(
        Report, on_delete=models.CASCADE, related_name='matches_as_found',
        limit_choices_to={'type': Report.FOUND}, verbose_name='الإعلان المعثور عليه'
    )
    score = models.PositiveSmallIntegerField(verbose_name='نسبة التطابق')
    reason = models.CharField(max_length=300, blank=True, verbose_name='سبب التطابق')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الاكتشاف')

    class Meta:
        unique_together = ['lost_report', 'found_report']
        ordering = ['-score']
        verbose_name = 'تطابق محتمل'
        verbose_name_plural = 'التطابقات المحتملة'

    def __str__(self):
        return f'{self.lost_report} ↔ {self.found_report} ({self.score}%)'
