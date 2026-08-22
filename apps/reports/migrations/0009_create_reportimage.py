import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0008_report_last_reminder_sent_at_reportflag'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='reports/%Y/%m/', verbose_name='الصورة')),
                ('order', models.PositiveSmallIntegerField(default=0, verbose_name='الترتيب')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الرفع')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='reports.report', verbose_name='الإعلان')),
            ],
            options={
                'verbose_name': 'صورة الإعلان',
                'verbose_name_plural': 'صور الإعلان',
                'ordering': ['order', 'created_at'],
            },
        ),
    ]
