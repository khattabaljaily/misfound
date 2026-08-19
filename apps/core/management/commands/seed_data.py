from django.core.management.base import BaseCommand

from apps.locations.models import City, Country
from apps.reports.models import Category

ARAB_COUNTRIES = [
    # code, name_ar, name_en, [major cities (ar, en)]
    ('EG', 'مصر', 'Egypt', [('القاهرة', 'Cairo'), ('الإسكندرية', 'Alexandria'), ('الجيزة', 'Giza')]),
    ('SA', 'السعودية', 'Saudi Arabia', [('الرياض', 'Riyadh'), ('جدة', 'Jeddah'), ('مكة المكرمة', 'Mecca')]),
    ('AE', 'الإمارات', 'United Arab Emirates', [('دبي', 'Dubai'), ('أبوظبي', 'Abu Dhabi'), ('الشارقة', 'Sharjah')]),
    ('KW', 'الكويت', 'Kuwait', [('مدينة الكويت', 'Kuwait City')]),
    ('QA', 'قطر', 'Qatar', [('الدوحة', 'Doha')]),
    ('BH', 'البحرين', 'Bahrain', [('المنامة', 'Manama')]),
    ('OM', 'عُمان', 'Oman', [('مسقط', 'Muscat')]),
    ('JO', 'الأردن', 'Jordan', [('عمّان', 'Amman'), ('إربد', 'Irbid')]),
    ('LB', 'لبنان', 'Lebanon', [('بيروت', 'Beirut'), ('طرابلس', 'Tripoli')]),
    ('SY', 'سوريا', 'Syria', [('دمشق', 'Damascus'), ('حلب', 'Aleppo')]),
    ('IQ', 'العراق', 'Iraq', [('بغداد', 'Baghdad'), ('البصرة', 'Basra')]),
    ('PS', 'فلسطين', 'Palestine', [('رام الله', 'Ramallah'), ('غزة', 'Gaza')]),
    ('YE', 'اليمن', 'Yemen', [('صنعاء', "Sana'a"), ('عدن', 'Aden')]),
    ('LY', 'ليبيا', 'Libya', [('طرابلس', 'Tripoli'), ('بنغازي', 'Benghazi')]),
    ('TN', 'تونس', 'Tunisia', [('تونس العاصمة', 'Tunis')]),
    ('DZ', 'الجزائر', 'Algeria', [('الجزائر العاصمة', 'Algiers')]),
    ('MA', 'المغرب', 'Morocco', [('الرباط', 'Rabat'), ('الدار البيضاء', 'Casablanca')]),
    ('SD', 'السودان', 'Sudan', [('الخرطوم', 'Khartoum')]),
    ('SO', 'الصومال', 'Somalia', [('مقديشو', 'Mogadishu')]),
    ('DJ', 'جيبوتي', 'Djibouti', [('جيبوتي', 'Djibouti City')]),
    ('KM', 'جزر القمر', 'Comoros', [('موروني', 'Moroni')]),
    ('MR', 'موريتانيا', 'Mauritania', [('نواكشوط', 'Nouakchott')]),
]

CATEGORIES = [
    ('محافظ وأوراق ثبوتية', 'Wallets & IDs', 'bi-wallet2'),
    ('هواتف وإلكترونيات', 'Phones & Electronics', 'bi-phone'),
    ('مفاتيح', 'Keys', 'bi-key'),
    ('حقائب وشنط', 'Bags', 'bi-bag'),
    ('مجوهرات', 'Jewelry', 'bi-gem'),
    ('حيوانات أليفة', 'Pets', 'bi-heart'),
    ('ملابس وإكسسوارات', 'Clothing & Accessories', 'bi-bookmark'),
    ('أخرى', 'Other', 'bi-three-dots'),
]


class Command(BaseCommand):
    help = 'تعبئة البيانات الأساسية: الدول والمدن العربية وتصنيفات الإعلانات'

    def handle(self, *args, **options):
        for code, name_ar, name_en, cities in ARAB_COUNTRIES:
            country, _ = Country.objects.update_or_create(
                code=code, defaults={'name_ar': name_ar, 'name_en': name_en}
            )
            for city_ar, city_en in cities:
                City.objects.get_or_create(
                    country=country, name_ar=city_ar, defaults={'name_en': city_en}
                )
        self.stdout.write(self.style.SUCCESS(f'تم تجهيز {len(ARAB_COUNTRIES)} دولة.'))

        for name_ar, name_en, icon in CATEGORIES:
            Category.objects.update_or_create(
                name_ar=name_ar, defaults={'name_en': name_en, 'icon': icon}
            )
        self.stdout.write(self.style.SUCCESS(f'تم تجهيز {len(CATEGORIES)} تصنيف.'))
