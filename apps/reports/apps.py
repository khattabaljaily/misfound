from django.apps import AppConfig


class ReportsConfig(AppConfig):
    name = 'apps.reports'
    verbose_name = 'الإعلانات'

    def ready(self):
        from . import signals  # noqa: F401
