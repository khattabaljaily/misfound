from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.reports.models import Report


class StaticViewSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return ['core:home', 'core:about', 'core:privacy', 'core:terms', 'reports:list']

    def location(self, item):
        return reverse(item)


class ReportSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return Report.objects.filter(status=Report.OPEN).only('id', 'updated_at')

    def lastmod(self, obj):
        return obj.updated_at
