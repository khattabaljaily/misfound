from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import get_language, gettext_lazy as _


class Category(models.Model):
    name_ar = models.CharField(max_length=100, verbose_name=_('الاسم بالعربية'))
    name_en = models.CharField(max_length=100, verbose_name=_('الاسم بالإنجليزية'))
    icon = models.CharField(
        max_length=50, blank=True, verbose_name=_('الأيقونة'),
        help_text='CSS icon class, e.g. bi-wallet2'
    )
    priority = models.PositiveSmallIntegerField(default=999, verbose_name=_('ترتيب'))

    class Meta:
        ordering = ['priority', 'name_ar']
        verbose_name = _('تصنيف')
        verbose_name_plural = _('التصنيفات')

    @property
    def name(self):
        return self.name_ar if get_language() == 'ar' else self.name_en

    def __str__(self):
        return self.name


class Report(models.Model):
    LOST = 'lost'
    FOUND = 'found'
    TYPE_CHOICES = [
        (LOST, _('مفقود')),
        (FOUND, _('معثور عليه')),
    ]

    OPEN = 'open'
    RESOLVED = 'resolved'
    STATUS_CHOICES = [
        (OPEN, _('قائم')),
        (RESOLVED, _('تم الاسترجاع')),
    ]

    type = models.CharField(max_length=5, choices=TYPE_CHOICES, verbose_name=_('نوع الإعلان'))
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=OPEN, verbose_name=_('الحالة')
    )

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports',
        verbose_name=_('صاحب الإعلان')
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='reports', verbose_name=_('التصنيف')
    )
    country = models.ForeignKey(
        'locations.Country', on_delete=models.PROTECT, related_name='reports', verbose_name=_('الدولة')
    )
    city = models.ForeignKey(
        'locations.City', on_delete=models.SET_NULL, null=True, blank=True, related_name='reports',
        verbose_name=_('المدينة')
    )

    title = models.CharField(max_length=200, verbose_name=_('العنوان'))
    description = models.TextField(verbose_name=_('الوصف'))
    identifier = models.CharField(
        max_length=100, blank=True, verbose_name=_('رقم المعرف'),
        help_text=_('رقم مميز للغرض إن وجد، مثل الرقم التسلسلي للإلكترونيات أو رقم المستند للوثائق. غير إجباري، لكنه يسهّل البحث والتأكد من الملكية.')
    )
    location_details = models.CharField(
        max_length=200, blank=True, verbose_name=_('تفاصيل المكان'),
        help_text=_('مكان الفقدان/العثور بالتفصيل')
    )
    image = models.ImageField(upload_to='reports/%Y/%m/', blank=True, null=True, verbose_name=_('الصورة'))
    event_date = models.DateField(verbose_name=_('تاريخ الفقدان أو العثور'))

    verification_question = models.CharField(
        max_length=255, blank=True, verbose_name=_('سؤال التحقق'),
        help_text=_('سؤال يُستخدم للتحقق من ملكية الغرض قبل التسليم (يظهر لصاحب الإعلان فقط)')
    )

    views = models.PositiveIntegerField(default=0, verbose_name=_('عدد المشاهدات'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    last_reminder_sent_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_('تاريخ آخر تذكير')
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('إعلان')
        verbose_name_plural = _('الإعلانات')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('reports:detail', args=[self.pk])


class ReportFlag(models.Model):
    """A user-submitted flag asking staff to review a report (abuse, spam,
    misleading info, etc.)."""

    OFFENSIVE = 'offensive'
    MISLEADING = 'misleading'
    DUPLICATE = 'duplicate'
    OTHER = 'other'
    REASON_CHOICES = [
        (OFFENSIVE, _('محتوى مسيء أو غير لائق')),
        (MISLEADING, _('معلومات مضللة أو غير صحيحة')),
        (DUPLICATE, _('إعلان مكرر')),
        (OTHER, _('سبب آخر')),
    ]

    report = models.ForeignKey(
        Report, on_delete=models.CASCADE, related_name='flags', verbose_name=_('الإعلان')
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='report_flags',
        verbose_name=_('مقدّم البلاغ')
    )
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, verbose_name=_('السبب'))
    note = models.CharField(max_length=300, blank=True, verbose_name=_('ملاحظة إضافية'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإبلاغ'))
    resolved = models.BooleanField(default=False, verbose_name=_('تمت المراجعة'))

    class Meta:
        unique_together = ['report', 'reporter']
        ordering = ['-created_at']
        verbose_name = _('إبلاغ عن إعلان')
        verbose_name_plural = _('بلاغات الإعلانات')

    def __str__(self):
        return f'{self.report} — {self.get_reason_display()}'


class Match(models.Model):
    """An AI-suggested pairing between a lost report and a found report
    that plausibly describe the same item."""

    lost_report = models.ForeignKey(
        Report, on_delete=models.CASCADE, related_name='matches_as_lost',
        limit_choices_to={'type': Report.LOST}, verbose_name=_('الإعلان المفقود')
    )
    found_report = models.ForeignKey(
        Report, on_delete=models.CASCADE, related_name='matches_as_found',
        limit_choices_to={'type': Report.FOUND}, verbose_name=_('الإعلان المعثور عليه')
    )
    score = models.PositiveSmallIntegerField(verbose_name=_('نسبة التطابق'))
    reason = models.CharField(max_length=300, blank=True, verbose_name=_('سبب التطابق'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الاكتشاف'))

    class Meta:
        unique_together = ['lost_report', 'found_report']
        ordering = ['-score']
        verbose_name = _('تطابق محتمل')
        verbose_name_plural = _('التطابقات المحتملة')

    def __str__(self):
        return f'{self.lost_report} ↔ {self.found_report} ({self.score}%)'
