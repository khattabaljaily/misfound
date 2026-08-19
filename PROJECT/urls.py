from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve as serve_static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('reports/', include('apps.reports.urls')),
    path('messages/', include('apps.messaging.urls')),
    re_path(
        r'^media/(?P<path>.*)$',
        serve_static,
        {'document_root': settings.MEDIA_ROOT},
    ),
]
