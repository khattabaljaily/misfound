from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from apps.locations.models import City
from .models import OTP_MAX_ATTEMPTS, User

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
        self.fields['email'].required = True
        for field in self.fields.values():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = _('اختر %(field)s') % {'field': field.label}

        country_id = self.data.get('country') or self.initial.get('country')
        self.fields['city'].queryset = (
            City.objects.filter(country_id=country_id) if country_id else City.objects.none()
        )


class LoginForm(AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        'inactive': _('حسابك غير مُفعّل بعد. تحقق من بريدك الإلكتروني لإكمال عملية التفعيل.'),
    }


class OTPVerifyForm(forms.Form):
    code = forms.CharField(
        label=_('رمز التحقق'),
        min_length=6,
        max_length=6,
        widget=forms.TextInput(attrs={'inputmode': 'numeric', 'autocomplete': 'one-time-code'}),
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data['code'].strip()
        otp = self.user.otps.filter(is_used=False).order_by('-created_at').first()
        if not otp or otp.is_expired():
            raise forms.ValidationError(_('انتهت صلاحية الرمز، اطلب رمزاً جديداً.'))
        if otp.attempts >= OTP_MAX_ATTEMPTS:
            raise forms.ValidationError(_('تجاوزت عدد المحاولات المسموحة، اطلب رمزاً جديداً.'))
        if code != otp.code:
            otp.attempts += 1
            otp.save(update_fields=['attempts'])
            raise forms.ValidationError(_('الرمز غير صحيح.'))
        self.otp = otp
        return code
