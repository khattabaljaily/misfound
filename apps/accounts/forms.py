from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from apps.locations.models import City
from .models import User

USERNAME_VALIDATOR = RegexValidator(
    regex=r'^[A-Za-z0-9]+$',
    message=_('اسم المستخدم يجب أن يتكون من حروف إنجليزية وأرقام فقط، بدون مسافات أو رموز.'),
)


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'country', 'city']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].validators = [USERNAME_VALIDATOR]
        self.fields['username'].help_text = _('حروف إنجليزية وأرقام فقط، بدون مسافات أو رموز.')
        for field in self.fields.values():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = _('اختر %(field)s') % {'field': field.label}

        country_id = self.data.get('country') or self.initial.get('country')
        self.fields['city'].queryset = (
            City.objects.filter(country_id=country_id) if country_id else City.objects.none()
        )
