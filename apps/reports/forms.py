from django import forms

from apps.locations.models import City
from .models import Report


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = [
            'category', 'country', 'city', 'title', 'description',
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
                field.empty_label = f'اختر {field.label}'

        country_id = self.data.get('country') or self.initial.get('country')
        self.fields['city'].queryset = (
            City.objects.filter(country_id=country_id) if country_id else City.objects.none()
        )

        self.report_type = report_type
        if report_type == Report.FOUND:
            self.fields['verification_question'].widget = forms.HiddenInput()
            self.fields['verification_question'].required = False
        else:
            self.fields['verification_question'].help_text = (
                'سؤال يُستخدم للتحقق من أن المتواصل معك هو صاحب الغرض فعلاً (لن يظهر للعامة)'
            )
