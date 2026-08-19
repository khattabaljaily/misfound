from django.db import migrations


def create_categories(apps, schema_editor):
    Category = apps.get_model('reports', 'Category')
    categories = [
        {'name_ar': 'الهواتف والإلكترونيات', 'name_en': 'Phones & Electronics', 'icon': 'bi-phone'},
        {'name_ar': 'الوثائق والبطاقات', 'name_en': 'Documents & Cards', 'icon': 'bi-file-earmark-text'},
        {'name_ar': 'المفاتيح', 'name_en': 'Keys', 'icon': 'bi-key'},
        {'name_ar': 'الحقائب والأمتعة', 'name_en': 'Bags & Luggage', 'icon': 'bi-handbag'},
        {'name_ar': 'الملابس والإكسسوارات', 'name_en': 'Clothing & Accessories', 'icon': 'bi-shirt'},
        {'name_ar': 'المركبات وملحقاتها', 'name_en': 'Vehicles & Accessories', 'icon': 'bi-car-front'},
        {'name_ar': 'الحيوانات الأليفة', 'name_en': 'Pets', 'icon': 'bi-paw'},
        {'name_ar': 'أغراض الأطفال', 'name_en': 'Kids & Baby Items', 'icon': 'bi-baby'},
        {'name_ar': 'النقود والمقتنيات الثمينة', 'name_en': 'Money & Valuables', 'icon': 'bi-wallet2'},
        {'name_ar': 'أخرى', 'name_en': 'Other', 'icon': 'bi-box-seam'},
    ]

    for cat in categories:
        Category.objects.update_or_create(
            name_ar=cat['name_ar'],
            defaults={'name_en': cat['name_en'], 'icon': cat['icon']}
        )


def remove_categories(apps, schema_editor):
    Category = apps.get_model('reports', 'Category')
    names = [
        'الهواتف والإلكترونيات',
        'الوثائق والبطاقات',
        'المفاتيح',
        'الحقائب والأمتعة',
        'الملابس والإكسسوارات',
        'المركبات وملحقاتها',
        'الحيوانات الأليفة',
        'أغراض الأطفال',
        'النقود والمقتنيات الثمينة',
        'أخرى',
    ]
    Category.objects.filter(name_ar__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_alter_category_options_alter_report_options_and_more'),
    ]

    operations = [
        migrations.RunPython(create_categories, remove_categories),
    ]
