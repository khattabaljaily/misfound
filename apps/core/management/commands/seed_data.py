from django.core.management.base import BaseCommand

from apps.locations.models import City, Country
from apps.reports.models import Category

ARAB_COUNTRIES = [
    # code, name_ar, name_en, [major cities (ar, en)]
    ('EG', 'مصر', 'Egypt', [
        ('القاهرة', 'Cairo'), ('الإسكندرية', 'Alexandria'), ('الجيزة', 'Giza'),
        ('شرم الشيخ', 'Sharm El-Sheikh'), ('الأقصر', 'Luxor'), ('أسوان', 'Aswan'),
        ('بورسعيد', 'Port Said'), ('السويس', 'Suez'), ('المنصورة', 'Mansoura'),
        ('طنطا', 'Tanta'), ('الزقازيق', 'Zagazig'), ('أسيوط', 'Assiut'),
    ]),
    ('SA', 'السعودية', 'Saudi Arabia', [
        ('الرياض', 'Riyadh'), ('جدة', 'Jeddah'), ('مكة المكرمة', 'Mecca'),
        ('المدينة المنورة', 'Medina'), ('الدمام', 'Dammam'), ('الخبر', 'Khobar'),
        ('الطائف', 'Taif'), ('تبوك', 'Tabuk'), ('بريدة', 'Buraidah'),
        ('خميس مشيط', 'Khamis Mushait'), ('حائل', 'Hail'), ('نجران', 'Najran'),
        ('أبها', 'Abha'), ('الجبيل', 'Jubail'),
    ]),
    ('AE', 'الإمارات', 'United Arab Emirates', [
        ('دبي', 'Dubai'), ('أبوظبي', 'Abu Dhabi'), ('الشارقة', 'Sharjah'),
        ('عجمان', 'Ajman'), ('رأس الخيمة', 'Ras Al Khaimah'), ('الفجيرة', 'Fujairah'),
        ('أم القيوين', 'Umm Al Quwain'), ('العين', 'Al Ain'),
    ]),
    ('KW', 'الكويت', 'Kuwait', [
        ('مدينة الكويت', 'Kuwait City'), ('حولي', 'Hawalli'), ('السالمية', 'Salmiya'),
        ('الفروانية', 'Farwaniya'), ('الجهراء', 'Jahra'), ('الأحمدي', 'Ahmadi'),
        ('مبارك الكبير', 'Mubarak Al-Kabeer'),
    ]),
    ('QA', 'قطر', 'Qatar', [
        ('الدوحة', 'Doha'), ('الريان', 'Al Rayyan'), ('الوكرة', 'Al Wakrah'),
        ('الخور', 'Al Khor'), ('أم صلال', 'Umm Salal'), ('الشمال', 'Al Shamal'),
        ('دخان', 'Dukhan'),
    ]),
    ('BH', 'البحرين', 'Bahrain', [
        ('المنامة', 'Manama'), ('المحرق', 'Muharraq'), ('الرفاع', 'Riffa'),
        ('مدينة عيسى', 'Isa Town'), ('مدينة حمد', 'Hamad Town'), ('سترة', 'Sitra'),
        ('جدحفص', 'Jidhafs'),
    ]),
    ('OM', 'عُمان', 'Oman', [
        ('مسقط', 'Muscat'), ('صلالة', 'Salalah'), ('صحار', 'Sohar'),
        ('نزوى', 'Nizwa'), ('صور', 'Sur'), ('البريمي', 'Al Buraimi'),
        ('عبري', 'Ibri'), ('الرستاق', 'Rustaq'),
    ]),
    ('JO', 'الأردن', 'Jordan', [
        ('عمّان', 'Amman'), ('إربد', 'Irbid'), ('الزرقاء', 'Zarqa'),
        ('العقبة', 'Aqaba'), ('السلط', 'Salt'), ('مادبا', 'Madaba'),
        ('الكرك', 'Karak'), ('جرش', 'Jerash'), ('المفرق', 'Mafraq'),
    ]),
    ('LB', 'لبنان', 'Lebanon', [
        ('بيروت', 'Beirut'), ('طرابلس', 'Tripoli'), ('صيدا', 'Sidon'),
        ('صور', 'Tyre'), ('زحلة', 'Zahle'), ('جونية', 'Jounieh'),
        ('بعلبك', 'Baalbek'), ('النبطية', 'Nabatieh'),
    ]),
    ('SY', 'سوريا', 'Syria', [
        ('دمشق', 'Damascus'), ('حلب', 'Aleppo'), ('حمص', 'Homs'),
        ('حماة', 'Hama'), ('اللاذقية', 'Latakia'), ('دير الزور', 'Deir ez-Zor'),
        ('الرقة', 'Raqqa'), ('درعا', 'Daraa'), ('طرطوس', 'Tartus'), ('إدلب', 'Idlib'),
    ]),
    ('IQ', 'العراق', 'Iraq', [
        ('بغداد', 'Baghdad'), ('البصرة', 'Basra'), ('الموصل', 'Mosul'),
        ('أربيل', 'Erbil'), ('النجف', 'Najaf'), ('كربلاء', 'Karbala'),
        ('كركوك', 'Kirkuk'), ('الناصرية', 'Nasiriyah'), ('الرمادي', 'Ramadi'),
        ('تكريت', 'Tikrit'), ('السليمانية', 'Sulaymaniyah'), ('الديوانية', 'Diwaniyah'),
    ]),
    ('PS', 'فلسطين', 'Palestine', [
        ('رام الله', 'Ramallah'), ('غزة', 'Gaza'), ('القدس', 'Jerusalem'),
        ('الخليل', 'Hebron'), ('نابلس', 'Nablus'), ('بيت لحم', 'Bethlehem'),
        ('جنين', 'Jenin'), ('طولكرم', 'Tulkarm'), ('أريحا', 'Jericho'),
    ]),
    ('YE', 'اليمن', 'Yemen', [
        ('صنعاء', "Sana'a"), ('عدن', 'Aden'), ('تعز', 'Taiz'),
        ('الحديدة', 'Hodeidah'), ('إب', 'Ibb'), ('المكلا', 'Mukalla'),
        ('حضرموت', 'Hadhramaut'), ('ذمار', 'Dhamar'),
    ]),
    ('LY', 'ليبيا', 'Libya', [
        ('طرابلس', 'Tripoli'), ('بنغازي', 'Benghazi'), ('مصراتة', 'Misrata'),
        ('الزاوية', 'Zawiya'), ('سبها', 'Sabha'), ('البيضاء', 'Bayda'),
        ('درنة', 'Derna'), ('زليتن', 'Zliten'),
    ]),
    ('TN', 'تونس', 'Tunisia', [
        ('تونس العاصمة', 'Tunis'), ('صفاقس', 'Sfax'), ('سوسة', 'Sousse'),
        ('القيروان', 'Kairouan'), ('بنزرت', 'Bizerte'), ('قابس', 'Gabes'),
        ('قفصة', 'Gafsa'), ('نابل', 'Nabeul'),
    ]),
    ('DZ', 'الجزائر', 'Algeria', [
        ('الجزائر العاصمة', 'Algiers'), ('وهران', 'Oran'), ('قسنطينة', 'Constantine'),
        ('عنابة', 'Annaba'), ('باتنة', 'Batna'), ('سطيف', 'Setif'),
        ('بليدة', 'Blida'), ('تلمسان', 'Tlemcen'), ('بجاية', 'Bejaia'),
    ]),
    ('MA', 'المغرب', 'Morocco', [
        ('الرباط', 'Rabat'), ('الدار البيضاء', 'Casablanca'), ('فاس', 'Fez'),
        ('مراكش', 'Marrakesh'), ('طنجة', 'Tangier'), ('أكادير', 'Agadir'),
        ('مكناس', 'Meknes'), ('وجدة', 'Oujda'), ('تطوان', 'Tetouan'), ('القنيطرة', 'Kenitra'),
    ]),
    ('SD', 'السودان', 'Sudan', [
        ('الخرطوم', 'Khartoum'), ('أم درمان', 'Omdurman'), ('بورتسودان', 'Port Sudan'),
        ('كسلا', 'Kassala'), ('نيالا', 'Nyala'), ('الأبيض', 'El Obeid'),
        ('عطبرة', 'Atbara'), ('ود مدني', 'Wad Madani'),
    ]),
    ('SO', 'الصومال', 'Somalia', [
        ('مقديشو', 'Mogadishu'), ('هرجيسا', 'Hargeisa'), ('بوصاصو', 'Bosaso'),
        ('كيسمايو', 'Kismayo'), ('بربرة', 'Berbera'), ('غالكعيو', 'Galkayo'),
    ]),
    ('DJ', 'جيبوتي', 'Djibouti', [
        ('جيبوتي', 'Djibouti City'), ('علي صبيح', 'Ali Sabieh'),
        ('تاجورة', 'Tadjourah'), ('ديخيل', 'Dikhil'),
    ]),
    ('KM', 'جزر القمر', 'Comoros', [
        ('موروني', 'Moroni'), ('موتسامودو', 'Moutsamoudou'), ('فومبوني', 'Fomboni'),
    ]),
    ('MR', 'موريتانيا', 'Mauritania', [
        ('نواكشوط', 'Nouakchott'), ('نواذيبو', 'Nouadhibou'), ('كيفة', 'Kiffa'),
        ('روصو', 'Rosso'), ('ازويرات', 'Zouerate'),
    ]),
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
