from django import forms
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
        self.report_type = report_type
        if report_type == Report.FOUND:
            self.fields['verification_question'].widget = forms.HiddenInput()
            self.fields['verification_question'].required = False
        else:
            self.fields['verification_question'].help_text = (
                'سؤال بيتأكد بيه إن اللي بيتواصل معاك هو صاحب الحاجة فعلاً (مش هيظهر للعموم)'
            )
