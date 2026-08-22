from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0010_copy_report_image_to_reportimage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='image',
        ),
    ]
