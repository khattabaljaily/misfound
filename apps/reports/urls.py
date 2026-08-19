from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name='list'),
    path('cities/', views.cities_for_country, name='cities_for_country'),
    path('mine/', views.my_reports, name='mine'),
    path('new/<str:report_type>/', views.report_create, name='create'),
    path('<int:pk>/', views.report_detail, name='detail'),
    path('<int:pk>/resolve/', views.report_resolve, name='resolve'),
]
