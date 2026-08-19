from django.db import migrations, models


def set_priorities(apps, schema_editor):
    Category = apps.get_model('reports', 'Category')
    priority_map = {
        'الهواتف والإلكترونيات': 1,
        'الوثائق والبطاقات': 2,
        'المركبات وملحقاتها': 3,
        'الحقائب والأمتعة': 4,
        'المفاتيح': 5,
        'الملابس والإكسسوارات': 6,
        'الحيوانات الأليفة': 7,
        'أغراض الأطفال': 8,
        'النقود والمقتنيات الثمينة': 9,
        'أخرى': 999,
    }
    for name, pr in priority_map.items():
        try:
            obj = Category.objects.filter(name_ar=name).first()
            if obj:
                obj.priority = pr
                obj.save(update_fields=['priority'])
        except Exception:
            continue


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0004_load_default_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='priority',
            field=models.PositiveSmallIntegerField(default=999, verbose_name='ترتيب'),
        ),
        migrations.RunPython(set_priorities, lambda apps, schema_editor: None),
    ]
