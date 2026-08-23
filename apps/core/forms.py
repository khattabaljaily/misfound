from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from apps.accounts.forms import USERNAME_VALIDATOR
from apps.locations.models import City


class AdminUserEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'phone', 'country', 'city']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].validators = [USERNAME_VALIDATOR]
        self.fields['username'].help_text = _('حروف إنجليزية وأرقام فقط، بدون مسافات أو رموز.')
        self.fields['email'].required = True
        for field in self.fields.values():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = _('اختر %(field)s') % {'field': field.label}

        country_id = self.data.get('country') or self.instance.country_id
        self.fields['city'].queryset = (
            City.objects.filter(country_id=country_id) if country_id else City.objects.none()
        )
