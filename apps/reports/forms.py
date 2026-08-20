from django import forms
from django.utils.translation import gettext_lazy as _

from apps.locations.models import City
from django.db.models import Case, When, Value, IntegerField
from .models import Report, Category


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = [
            'category', 'country', 'city', 'title', 'description', 'identifier',
            'location_details', 'event_date', 'image', 'verification_question',
        ]
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, report_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = _('اختر %(field)s') % {'field': field.label}

        country_id = self.data.get('country') or self.initial.get('country')
        self.fields['city'].queryset = (
            City.objects.filter(country_id=country_id) if country_id else City.objects.none()
        )

        # Order categories using a custom priority list so default dropdown
        # shows the preferred sequence (Arabic names). 'أخرى' will be last.
        preferred = [
            'الهواتف والإلكترونيات',
            'الوثائق والبطاقات',
            'المركبات وملحقاتها',
            'الحقائب والأمتعة',
            'المفاتيح',
            'الملابس والإكسسوارات',
            'الحيوانات الأليفة',
            'أغراض الأطفال',
            'النقود والمقتنيات الثمينة',
            'أخرى',
        ]

        # Rely on the model-level `priority` ordering; ensure fallback ordering by name
        self.fields['category'].queryset = Category.objects.order_by('priority', 'name_ar')

        self.report_type = report_type
        if report_type == Report.FOUND:
            self.fields['verification_question'].widget = forms.HiddenInput()
            self.fields['verification_question'].required = False
        else:
            self.fields['verification_question'].help_text = _(
                'سؤال يُستخدم للتحقق من أن المتواصل معك هو صاحب الغرض فعلاً (لن يظهر للعامة)'
            )
