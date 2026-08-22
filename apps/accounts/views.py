from django.contrib.auth import login
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _

from .forms import LoginForm, OTPVerifyForm, RegisterForm
from .models import EmailOTP, User

OTP_RESEND_COOLDOWN_SECONDS = 60


def _is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def _send_otp_email(user):
    otp = EmailOTP.objects.create(user=user, code=EmailOTP.generate_code())
    context = {'user': user, 'code': otp.code}
    subject = render_to_string('accounts/otp_email_subject.txt', context).strip()
    body = render_to_string('accounts/otp_email.html', context)
    send_mail(subject, body, None, [user.email])
    return otp


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            _send_otp_email(user)
            request.session['pending_verification_user_id'] = user.pk
            if _is_ajax(request):
                return JsonResponse({'success': True, 'redirect': reverse('accounts:verify_otp')})
            return redirect('accounts:verify_otp')
        if _is_ajax(request):
            return render(request, 'accounts/_register_form.html', {'form': form}, status=400)
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def _pending_verification_user(request):
    user_id = request.session.get('pending_verification_user_id')
    if not user_id:
        return None
    return User.objects.filter(pk=user_id, is_active=False).first()


def verify_otp(request):
    user = _pending_verification_user(request)
    if not user:
        return redirect('accounts:register')

    if request.method == 'POST':
        form = OTPVerifyForm(request.POST, user=user)
        if form.is_valid():
            form.otp.is_used = True
            form.otp.save(update_fields=['is_used'])
            user.is_active = True
            user.save(update_fields=['is_active'])
            del request.session['pending_verification_user_id']
            login(request, user)
            if _is_ajax(request):
                return JsonResponse({'success': True, 'redirect': reverse('core:home')})
            return redirect('core:home')
        if _is_ajax(request):
            return render(request, 'accounts/_verify_otp_form.html', {'form': form}, status=400)
    else:
        form = OTPVerifyForm(user=user)
    return render(request, 'accounts/verify_otp.html', {'form': form, 'email': user.email})


def resend_otp(request):
    user = _pending_verification_user(request)
    if not user:
        return redirect('accounts:register')

    last_otp = user.otps.order_by('-created_at').first()
    if last_otp and (timezone.now() - last_otp.created_at).total_seconds() < OTP_RESEND_COOLDOWN_SECONDS:
        message = _('انتظر قليلاً قبل طلب رمز جديد.')
        status = 429
        success = False
    else:
        _send_otp_email(user)
        message = _('تم إرسال رمز جديد إلى بريدك الإلكتروني.')
        status = 200
        success = True

    if _is_ajax(request):
        return JsonResponse({'success': success, 'message': message}, status=status)
    return redirect('accounts:verify_otp')


class MisfoundLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = LoginForm

    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse('core:admin_stats')
        return super().get_success_url()

    def form_valid(self, form):
        response = super().form_valid(form)
        if _is_ajax(self.request):
            return JsonResponse({'success': True, 'redirect': self.get_success_url()})
        return response

    def form_invalid(self, form):
        if _is_ajax(self.request):
            return render(self.request, 'accounts/_login_form.html', {'form': form}, status=400)
        return super().form_invalid(form)


class MisfoundLogoutView(LogoutView):
    next_page = 'core:home'


class MisfoundPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')

    def form_valid(self, form):
        response = super().form_valid(form)
        if _is_ajax(self.request):
            return JsonResponse({'success': True, 'redirect': str(self.success_url)})
        return response

    def form_invalid(self, form):
        if _is_ajax(self.request):
            return render(self.request, 'accounts/_password_reset_form.html', {'form': form}, status=400)
        return super().form_invalid(form)


class MisfoundPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class MisfoundPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')

    def form_valid(self, form):
        response = super().form_valid(form)
        if _is_ajax(self.request):
            return JsonResponse({'success': True, 'redirect': str(self.success_url)})
        return response

    def form_invalid(self, form):
        if _is_ajax(self.request):
            return render(
                self.request, 'accounts/_password_reset_confirm_form.html', {'form': form}, status=400
            )
        return super().form_invalid(form)


class MisfoundPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
