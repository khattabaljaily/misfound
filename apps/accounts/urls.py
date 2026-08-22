from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify/', views.verify_otp, name='verify_otp'),
    path('verify/resend/', views.resend_otp, name='resend_otp'),
    path('login/', views.MisfoundLoginView.as_view(), name='login'),
    path('logout/', views.MisfoundLogoutView.as_view(), name='logout'),
    path('password-reset/', views.MisfoundPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.MisfoundPasswordResetDoneView.as_view(), name='password_reset_done'),
    path(
        'reset/<uidb64>/<token>/',
        views.MisfoundPasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
    path('reset/done/', views.MisfoundPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
