from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from apps.notifications.services import notify
from apps.reports.models import Report

STALE_AFTER_DAYS = 14
REPEAT_EVERY_DAYS = 14


class Command(BaseCommand):
    help = 'يرسل تذكيرًا داخل المنصة لأصحاب الإعلانات القائمة منذ فترة طويلة دون حل'

    def handle(self, *args, **options):
        now = timezone.now()
        stale_cutoff = now - timezone.timedelta(days=STALE_AFTER_DAYS)
        repeat_cutoff = now - timezone.timedelta(days=REPEAT_EVERY_DAYS)

        reports = Report.objects.filter(
            status=Report.OPEN, created_at__lte=stale_cutoff,
        ).filter(
            Q(last_reminder_sent_at__isnull=True) | Q(last_reminder_sent_at__lte=repeat_cutoff)
        )

        sent = 0
        for report in reports:
            notify(
                report.reporter, 'resolved_reminder',
                f'هل ما زال إعلانك قائمًا؟ {report.title}',
                'مضى وقت على نشر هذا الإعلان. يرجى تحديث حالته إلى «تم الاسترجاع» إذا انتهى الأمر، أو تركه كما هو إذا كان لا يزال قائمًا.',
                report.get_absolute_url(),
            )
            report.last_reminder_sent_at = now
            report.save(update_fields=['last_reminder_sent_at'])
            sent += 1

        self.stdout.write(self.style.SUCCESS(f'تم إرسال {sent} تذكير(ات).'))
