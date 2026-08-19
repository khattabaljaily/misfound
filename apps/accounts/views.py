from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from .forms import RegisterForm


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('core:home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


class MisfoundLoginView(LoginView):
    template_name = 'accounts/login.html'


class MisfoundLogoutView(LogoutView):
    next_page = 'core:home'
