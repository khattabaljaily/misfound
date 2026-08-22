from django.db import migrations


def copy_images_forward(apps, schema_editor):
    Report = apps.get_model('reports', 'Report')
    ReportImage = apps.get_model('reports', 'ReportImage')
    for report in Report.objects.exclude(image='').exclude(image__isnull=True):
        ReportImage.objects.create(report=report, image=report.image, order=0)


def copy_images_backward(apps, schema_editor):
    Report = apps.get_model('reports', 'Report')
    ReportImage = apps.get_model('reports', 'ReportImage')
    for image in ReportImage.objects.order_by('report_id', 'order', 'created_at'):
        report = image.report
        if not report.image:
            report.image = image.image
            report.save(update_fields=['image'])


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0009_create_reportimage'),
    ]

    operations = [
        migrations.RunPython(copy_images_forward, copy_images_backward),
    ]
