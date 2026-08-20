from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

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
