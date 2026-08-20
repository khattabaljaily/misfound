from django.core.management.base import BaseCommand

from apps.reports.matching import find_and_save_matches
from apps.reports.models import Report


class Command(BaseCommand):
    help = 'يبحث عن تطابقات محتملة بين كل الإعلانات القائمة (المفقود مقابل المعثور عليه) باستخدام DeepSeek'

    def handle(self, *args, **options):
        reports = Report.objects.filter(status=Report.OPEN).select_related('category', 'country', 'city')
        total_new = 0
        for report in reports:
            new_matches = find_and_save_matches(report)
            if new_matches:
                total_new += len(new_matches)
                self.stdout.write(f'{report} → {len(new_matches)} تطابق جديد')
        self.stdout.write(self.style.SUCCESS(f'تم الانتهاء. إجمالي التطابقات الجديدة: {total_new}'))
