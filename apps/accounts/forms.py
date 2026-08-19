from django import forms
from django.contrib.auth.forms import UserCreationForm

from apps.locations.models import City
from .models import User


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'country', 'city']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = f'اختر {field.label}'

        country_id = self.data.get('country') or self.initial.get('country')
        self.fields['city'].queryset = (
            City.objects.filter(country_id=country_id) if country_id else City.objects.none()
        )
