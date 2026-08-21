from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Message, Rating


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 2, 'placeholder': _('اكتب رسالتك...')}),
        }


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['stars', 'comment']
        widgets = {
            'stars': forms.RadioSelect(),
            'comment': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': _('تعليق اختياري عن تجربتك...'),
                'maxlength': 300,
            }),
        }
