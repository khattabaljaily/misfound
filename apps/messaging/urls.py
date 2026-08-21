from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('start/<int:report_pk>/', views.start_conversation, name='start'),
    path('<int:pk>/', views.conversation_detail, name='conversation'),
    path('<int:pk>/verify/', views.mark_verified, name='verify'),
]
