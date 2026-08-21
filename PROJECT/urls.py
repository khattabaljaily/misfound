from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path
from django.views.static import serve as serve_static

from apps.core.sitemaps import ReportSitemap, StaticViewSitemap
from apps.core.views import robots_txt

sitemaps = {
    'static': StaticViewSitemap,
    'reports': ReportSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('reports/', include('apps.reports.urls')),
    path('messages/', include('apps.messaging.urls')),
    path('notifications/', include('apps.notifications.urls')),
    re_path(
        r'^media/(?P<path>.*)$',
        serve_static,
        {'document_root': settings.MEDIA_ROOT},
    ),
]
