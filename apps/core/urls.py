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
    path('DDQ9RKHA/users/', views.admin_users, name='admin_users'),
    path('DDQ9RKHA/users/<int:pk>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('DDQ9RKHA/users/<int:pk>/toggle-active/', views.admin_user_toggle_active, name='admin_user_toggle_active'),
    path('DDQ9RKHA/users/<int:pk>/delete/', views.admin_user_delete, name='admin_user_delete'),
]
