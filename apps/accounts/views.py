from django.contrib.auth import login
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy

from .forms import RegisterForm


def _is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if _is_ajax(request):
                return JsonResponse({'success': True, 'redirect': reverse('core:home')})
            return redirect('core:home')
        if _is_ajax(request):
            return render(request, 'accounts/_register_form.html', {'form': form}, status=400)
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


class MisfoundLoginView(LoginView):
    template_name = 'accounts/login.html'

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
