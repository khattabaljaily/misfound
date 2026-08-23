from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('DDQ9RKHA/', views.admin_stats, name='admin_stats'),
    path('DDQ9RKHA/visits/', views.admin_visits, name='admin_visits'),
    path('DDQ9RKHA/flags/', views.admin_flags, name='admin_flags'),
    path('DDQ9RKHA/flags/<int:pk>/resolve/', views.admin_flag_resolve, name='admin_flag_resolve'),
]
