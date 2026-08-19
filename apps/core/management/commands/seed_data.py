from django.core.management.base import BaseCommand

from apps.locations.models import City, Country
from apps.reports.models import Category

ARAB_COUNTRIES = [
    # code, name_ar, name_en, [cities (ar, en)] — sourced from the GeoNames-based
    # dr5hn/countries-states-cities-database, cross-checked for correct Arabic spelling.
    ('EG', 'مصر', 'Egypt', [
        ('القاهرة', 'Cairo'), ('الإسكندرية', 'Alexandria'), ('الجيزة', 'Giza'),
        ('شرم الشيخ', 'Sharm El-Sheikh'), ('الأقصر', 'Luxor'), ('أسوان', 'Aswan'),
        ('بورسعيد', 'Port Said'), ('السويس', 'Suez'), ('المنصورة', 'Mansoura'),
        ('طنطا', 'Tanta'), ('الزقازيق', 'Zagazig'), ('أسيوط', 'Assiut'),
        ('الفيوم', 'Fayoum'), ('دمياط', 'Damietta'), ('الإسماعيلية', 'Ismailia'),
        ('بني سويف', 'Beni Suef'), ('المنيا', 'Minya'), ('سوهاج', 'Sohag'),
        ('قنا', 'Qena'), ('كفر الشيخ', 'Kafr El Sheikh'), ('دمنهور', 'Damanhur'),
        ('مرسى مطروح', 'Mersa Matruh'), ('العريش', 'Arish'), ('الغردقة', 'Hurghada'),
        ('دهب', 'Dahab'), ('حلوان', 'Helwan'), ('مدينة نصر', 'Nasr City'),
        ('السادس من أكتوبر', '6th of October City'), ('العاشر من رمضان', '10th of Ramadan City'),
        ('بلبيس', 'Bilbeis'), ('ملوي', 'Mallawi'), ('إدفو', 'Edfu'),
        ('إسنا', 'Esna'), ('كوم أمبو', 'Kom Ombo'), ('سفاجا', 'Safaga'),
        ('مرسى علم', 'Marsa Alam'), ('واحة سيوة', 'Siwa Oasis'), ('أبو سمبل', 'Abu Simbel'),
    ]),
    ('SA', 'السعودية', 'Saudi Arabia', [
        ('الرياض', 'Riyadh'), ('جدة', 'Jeddah'), ('مكة المكرمة', 'Mecca'),
        ('المدينة المنورة', 'Medina'), ('الدمام', 'Dammam'), ('الخبر', 'Khobar'),
        ('الظهران', 'Dhahran'), ('الطائف', 'Taif'), ('تبوك', 'Tabuk'),
        ('بريدة', 'Buraidah'), ('عنيزة', 'Unaizah'), ('حائل', 'Hail'),
        ('نجران', 'Najran'), ('جازان', 'Jazan'), ('أبها', 'Abha'),
        ('خميس مشيط', 'Khamis Mushait'), ('الجبيل', 'Jubail'), ('ينبع', 'Yanbu'),
        ('الأحساء', 'Al-Hofuf'), ('القطيف', 'Qatif'), ('حفر الباطن', 'Hafar Al-Batin'),
        ('عرعر', 'Arar'), ('سكاكا', 'Sakakah'), ('القريات', 'Qurayyat'),
        ('الباحة', 'Al Baha'), ('رابغ', 'Rabigh'), ('الرس', 'Ar Rass'),
        ('الخرج', 'Al Kharj'), ('الدوادمي', 'Dawadmi'), ('وادي الدواسر', 'Wadi ad-Dawasir'),
        ('بيشة', 'Bisha'), ('شرورة', 'Sharurah'), ('الزلفي', 'Az Zulfi'),
        ('رفحاء', 'Rafha'), ('القنفذة', 'Al Qunfudhah'), ('ضباء', 'Duba'),
    ]),
    ('AE', 'الإمارات', 'United Arab Emirates', [
        ('دبي', 'Dubai'), ('أبوظبي', 'Abu Dhabi'), ('الشارقة', 'Sharjah'),
        ('عجمان', 'Ajman'), ('رأس الخيمة', 'Ras Al Khaimah'), ('الفجيرة', 'Fujairah'),
        ('أم القيوين', 'Umm Al Quwain'), ('العين', 'Al Ain'), ('خورفكان', 'Khor Fakkan'),
        ('دبا الفجيرة', 'Dibba Al Fujairah'), ('كلباء', 'Kalba'), ('مصفح', 'Mussafah'),
        ('مدينة خليفة', 'Khalifa City'), ('مدينة زايد', 'Zayed City'), ('غياثي', 'Ghayathi'),
        ('الذيد', 'Al Dhaid'), ('الرويس', 'Ruwais'), ('واحة ليوا', 'Liwa Oasis'),
    ]),
    ('KW', 'الكويت', 'Kuwait', [
        ('مدينة الكويت', 'Kuwait City'), ('حولي', 'Hawalli'), ('السالمية', 'Salmiya'),
        ('الفروانية', 'Farwaniya'), ('الجهراء', 'Jahra'), ('الأحمدي', 'Ahmadi'),
        ('الفنطاس', 'Fintas'), ('الفحيحيل', 'Fahaheel'), ('الرقة', 'Riqqa'),
        ('الرميثية', 'Rumaithiya'), ('بيان', 'Bayan'), ('صباح السالم', 'Sabah Al-Salem'),
        ('الشامية', 'Shamiya'), ('الوفرة', 'Wafra'),
    ]),
    ('QA', 'قطر', 'Qatar', [
        ('الدوحة', 'Doha'), ('الريان', 'Al Rayyan'), ('الوكرة', 'Al Wakrah'),
        ('الخور', 'Al Khor'), ('الغويرية', 'Al Ghuwayriyah'), ('الجميلية', 'Al Jumayliyah'),
        ('الرويس', 'Ar Ruways'), ('الشحانية', 'Ash Shahaniyah'), ('دخان', 'Dukhan'),
        ('مسيعيد', "Musay'id"), ('أم صلال', 'Umm Salal'), ('أم باب', 'Umm Bab'),
        ('مدينة الشمال', 'Madinat ash Shamal'), ('الوكير', 'Al Wukair'),
    ]),
    ('BH', 'البحرين', 'Bahrain', [
        ('المنامة', 'Manama'), ('المحرق', 'Muharraq'), ('الرفاع', 'Riffa'),
        ('مدينة عيسى', 'Isa Town'), ('مدينة حمد', 'Hamad Town'), ('سترة', 'Sitra'),
        ('الحد', 'Al Hadd'), ('جدحفص', 'Jidhafs'), ('دار كليب', 'Dar Kulaib'),
    ]),
    ('OM', 'عُمان', 'Oman', [
        ('مسقط', 'Muscat'), ('صلالة', 'Salalah'), ('صحار', 'Sohar'),
        ('نزوى', 'Nizwa'), ('صور', 'Sur'), ('البريمي', 'Al Buraimi'),
        ('عبري', 'Ibri'), ('الرستاق', 'Rustaq'), ('بهلاء', 'Bahla'),
        ('بركاء', 'Barka'), ('السيب', 'Seeb'), ('بوشر', 'Bawshar'),
        ('خصب', 'Khasab'), ('إزكي', 'Izki'), ('أدم', 'Adam'),
        ('السويق', 'As Suwayq'), ('ينقل', 'Yanqul'), ('شناص', 'Shinas'),
    ]),
    ('JO', 'الأردن', 'Jordan', [
        ('عمّان', 'Amman'), ('إربد', 'Irbid'), ('الزرقاء', 'Zarqa'),
        ('العقبة', 'Aqaba'), ('السلط', 'Salt'), ('مادبا', 'Madaba'),
        ('الكرك', 'Karak'), ('جرش', 'Jerash'), ('المفرق', 'Mafraq'),
        ('الطفيلة', 'Tafilah'), ('عجلون', 'Ajloun'), ('معان', "Ma'an"),
        ('الرصيفة', 'Russeifa'), ('الرمثا', 'Ramtha'), ('البتراء', 'Petra'),
        ('الشوبك', 'Shawbak'), ('الأزرق', 'Azraq'),
    ]),
    ('LB', 'لبنان', 'Lebanon', [
        ('بيروت', 'Beirut'), ('طرابلس', 'Tripoli'), ('صيدا', 'Sidon'),
        ('صور', 'Tyre'), ('زحلة', 'Zahle'), ('جونية', 'Jounieh'),
        ('بعلبك', 'Baalbek'), ('النبطية', 'Nabatieh'), ('بترون', 'Batroun'),
        ('بشري', 'Bcharre'), ('جبيل', 'Jbeil'), ('بحمدون', 'Bhamdoun'),
        ('عانجر', 'Aanjar'), ('الغازية', 'Ghazieh'),
    ]),
    ('SY', 'سوريا', 'Syria', [
        ('دمشق', 'Damascus'), ('حلب', 'Aleppo'), ('حمص', 'Homs'),
        ('حماة', 'Hama'), ('اللاذقية', 'Latakia'), ('دير الزور', 'Deir ez-Zor'),
        ('الرقة', 'Raqqa'), ('درعا', 'Daraa'), ('طرطوس', 'Tartus'),
        ('إدلب', 'Idlib'), ('السويداء', 'As-Suwayda'), ('الحسكة', 'Al-Hasakah'),
        ('القامشلي', 'Al-Qamishli'), ('عفرين', 'Afrin'), ('منبج', 'Manbij'),
        ('أعزاز', 'Azaz'), ('دوما', 'Douma'), ('جبلة', 'Jableh'),
        ('بانياس', 'Baniyas'), ('الزبداني', 'Az-Zabadani'), ('تدمر', 'Tadmur'),
        ('تل أبيض', 'Tell Abyad'), ('عين العرب', 'Ayn al-Arab'), ('معرة النعمان', "Ma'arrat al-Nu'man"),
        ('صافيتا', 'Safita'),
    ]),
    ('IQ', 'العراق', 'Iraq', [
        ('بغداد', 'Baghdad'), ('البصرة', 'Basra'), ('الموصل', 'Mosul'),
        ('أربيل', 'Erbil'), ('النجف', 'Najaf'), ('كربلاء', 'Karbala'),
        ('كركوك', 'Kirkuk'), ('السليمانية', 'Sulaymaniyah'), ('الناصرية', 'Nasiriyah'),
        ('الرمادي', 'Ramadi'), ('الفلوجة', 'Fallujah'), ('تكريت', 'Tikrit'),
        ('الديوانية', 'Diwaniyah'), ('الكوت', 'Kut'), ('العمارة', 'Amarah'),
        ('الحلة', 'Hillah'), ('بعقوبة', 'Baqubah'), ('دهوك', 'Dohuk'),
        ('زاخو', 'Zakho'), ('سنجار', 'Sinjar'), ('الفاو', 'Fao'),
        ('الزبير', 'Zubair'), ('سامراء', 'Samarra'), ('بلد', 'Balad'),
        ('الرطبة', 'Rutba'), ('هيت', 'Hit'), ('راوة', 'Rawa'),
        ('خانقين', 'Khanaqin'), ('كفري', 'Kifri'), ('حلبجة', 'Halabja'),
    ]),
    ('PS', 'فلسطين', 'Palestine', [
        ('القدس', 'Jerusalem'), ('غزة', 'Gaza City'), ('رام الله', 'Ramallah'),
        ('الخليل', 'Hebron'), ('نابلس', 'Nablus'), ('بيت لحم', 'Bethlehem'),
        ('جنين', 'Jenin'), ('طولكرم', 'Tulkarm'), ('أريحا', 'Jericho'),
        ('قلقيلية', 'Qalqilya'), ('طوباس', 'Tubas'), ('البيرة', 'Al-Bireh'),
        ('خان يونس', 'Khan Yunis'), ('رفح', 'Rafah'), ('دير البلح', 'Deir al-Balah'),
        ('جباليا', 'Jabalia'), ('بيت ساحور', 'Beit Sahour'), ('بيت جالا', 'Beit Jala'),
        ('دورا', 'Dura'), ('يطا', 'Yatta'),
    ]),
    ('YE', 'اليمن', 'Yemen', [
        ('صنعاء', "Sana'a"), ('عدن', 'Aden'), ('تعز', 'Taiz'),
        ('الحديدة', 'Al Hudaydah'), ('إب', 'Ibb'), ('المكلا', 'Al Mukalla'),
        ('ذمار', 'Dhamar'), ('صعدة', "Sa'dah"), ('مأرب', 'Marib'),
        ('حجة', 'Hajjah'), ('البيضاء', 'Al Bayda'), ('لحج', 'Lahij'),
        ('زنجبار', 'Zinjibar'), ('سيئون', 'Sayun'), ('شبام', 'Shibam'),
        ('الغيضة', 'Al Ghaydah'), ('رداع', "Rada'a"), ('يريم', 'Yarim'),
        ('جبلة', 'Jiblah'), ('باجل', 'Bajil'), ('المخا', 'Al Mukha'),
        ('عتق', 'Ataq'), ('حبان', 'Habban'),
    ]),
    ('LY', 'ليبيا', 'Libya', [
        ('طرابلس', 'Tripoli'), ('بنغازي', 'Benghazi'), ('مصراتة', 'Misrata'),
        ('الزاوية', 'Zawiya'), ('سبها', 'Sabha'), ('البيضاء', 'Bayda'),
        ('درنة', 'Derna'), ('زليتن', 'Zliten'), ('أجدابيا', 'Ajdabiya'),
        ('الخمس', 'Al Khums'), ('غريان', 'Gharyan'), ('صبراتة', 'Sabratah'),
        ('توكرة', 'Tukrah'), ('طبرق', 'Tobruk'), ('نالوت', 'Nalut'),
        ('غدامس', 'Ghadames'), ('مرزق', 'Murzuq'), ('هون', 'Hun'),
        ('بني وليد', 'Bani Walid'),
    ]),
    ('TN', 'تونس', 'Tunisia', [
        ('تونس العاصمة', 'Tunis'), ('صفاقس', 'Sfax'), ('سوسة', 'Sousse'),
        ('القيروان', 'Kairouan'), ('بنزرت', 'Bizerte'), ('قابس', 'Gabes'),
        ('قفصة', 'Gafsa'), ('نابل', 'Nabeul'), ('أريانة', 'Ariana'),
        ('بن عروس', 'Ben Arous'), ('المنستير', 'Monastir'), ('مدنين', 'Medenine'),
        ('توزر', 'Tozeur'), ('قبلي', 'Kebili'), ('سيدي بوزيد', 'Sidi Bouzid'),
        ('جندوبة', 'Jendouba'), ('الكاف', 'El Kef'), ('باجة', 'Béja'),
        ('زغوان', 'Zaghouan'), ('سليانة', 'Siliana'), ('تطاوين', 'Tataouine'),
        ('قرمبالية', 'Grombalia'), ('حمام سوسة', 'Hammam Sousse'), ('حمامات', 'Hammamet'),
        ('المهدية', 'Mahdia'),
    ]),
    ('DZ', 'الجزائر', 'Algeria', [
        ('الجزائر العاصمة', 'Algiers'), ('وهران', 'Oran'), ('قسنطينة', 'Constantine'),
        ('عنابة', 'Annaba'), ('باتنة', 'Batna'), ('سطيف', 'Setif'),
        ('بليدة', 'Blida'), ('تلمسان', 'Tlemcen'), ('بجاية', 'Bejaia'),
        ('بسكرة', 'Biskra'), ('غرداية', 'Ghardaia'), ('ورقلة', 'Ouargla'),
        ('تبسة', 'Tebessa'), ('الشلف', 'Chlef'), ('جيجل', 'Jijel'),
        ('سكيكدة', 'Skikda'), ('مستغانم', 'Mostaganem'), ('معسكر', 'Mascara'),
        ('سعيدة', 'Saida'), ('سيدي بلعباس', 'Sidi Bel Abbès'), ('البويرة', 'Bouira'),
        ('تيارت', 'Tiaret'), ('المسيلة', "M'Sila"), ('الأغواط', 'Laghouat'),
        ('أدرار', 'Adrar'), ('تمنراست', 'Tamanrasset'), ('إليزي', 'Illizi'),
        ('تندوف', 'Tindouf'), ('الوادي', 'El Oued'), ('برج بوعريريج', 'Bordj Bou Arreridj'),
        ('خنشلة', 'Khenchela'), ('قالمة', 'Guelma'), ('تيزي وزو', 'Tizi Ouzou'),
        ('الطارف', 'El Tarf'), ('غليزان', 'Relizane'), ('ميلة', 'Mila'),
        ('تيبازة', 'Tipaza'), ('النعامة', 'Naama'), ('البيض', 'El Bayadh'),
    ]),
    ('MA', 'المغرب', 'Morocco', [
        ('الرباط', 'Rabat'), ('الدار البيضاء', 'Casablanca'), ('فاس', 'Fez'),
        ('مراكش', 'Marrakesh'), ('طنجة', 'Tangier'), ('أكادير', 'Agadir'),
        ('مكناس', 'Meknes'), ('وجدة', 'Oujda'), ('تطوان', 'Tetouan'),
        ('القنيطرة', 'Kenitra'), ('آسفي', 'Safi'), ('الجديدة', 'El Jadida'),
        ('بني ملال', 'Beni Mellal'), ('تازة', 'Taza'), ('خريبكة', 'Khouribga'),
        ('سطات', 'Settat'), ('الناظور', 'Nador'), ('العيون', 'Laayoune'),
        ('الحسيمة', 'Al Hoceima'), ('ورزازات', 'Ouarzazate'), ('الصويرة', 'Essaouira'),
        ('تارودانت', 'Taroudant'), ('الرشيدية', 'Errachidia'), ('خنيفرة', 'Khenifra'),
        ('سيدي قاسم', 'Sidi Kacem'), ('سيدي إفني', 'Sidi Ifni'), ('أزيلال', 'Azilal'),
        ('بركان', 'Berkane'), ('وزان', 'Ouezzane'), ('شفشاون', 'Chefchaouen'),
        ('تزنيت', 'Tiznit'), ('تمارة', 'Temara'), ('سلا', 'Sale'),
        ('برشيد', 'Berrechid'), ('كلميم', 'Guelmim'), ('زاكورة', 'Zagora'),
        ('ميدلت', 'Midelt'),
    ]),
    ('SD', 'السودان', 'Sudan', [
        ('الخرطوم', 'Khartoum'), ('أم درمان', 'Omdurman'), ('بورتسودان', 'Port Sudan'),
        ('كسلا', 'Kassala'), ('نيالا', 'Nyala'), ('الأبيض', 'El Obeid'),
        ('عطبرة', 'Atbara'), ('ود مدني', 'Wad Madani'), ('القضارف', 'Al Qadarif'),
        ('الفاشر', 'El Fasher'), ('دنقلا', 'Dongola'), ('بربر', 'Berber'),
        ('سنار', 'Sinnar'), ('كوستي', 'Kosti'), ('شندي', 'Shendi'),
        ('زالنجي', 'Zalingei'), ('كادقلي', 'Kadugli'), ('الدلنج', 'Dilling'),
        ('مروي', 'Merowe'), ('الرصيرص', 'Ar Ruseris'),
    ]),
    ('SO', 'الصومال', 'Somalia', [
        ('مقديشو', 'Mogadishu'), ('هرجيسا', 'Hargeisa'), ('بوصاصو', 'Bosaso'),
        ('كيسمايو', 'Kismayo'), ('بربرة', 'Berbera'), ('غالكعيو', 'Gaalkacyo'),
        ('بيدوا', 'Baidoa'), ('بيليتوين', 'Beledweyne'), ('بوراو', 'Burao'),
        ('غاروي', 'Garoowe'), ('جوهر', 'Jowhar'), ('مركا', 'Marka'),
        ('عيل', 'Eyl'), ('لاس عانود', 'Las Anod'), ('جيليب', 'Jilib'),
        ('واجد', 'Waajid'), ('غاربهاري', 'Garbahaarrey'),
    ]),
    ('DJ', 'جيبوتي', 'Djibouti', [
        ('جيبوتي', 'Djibouti City'), ('علي صبيح', 'Ali Sabieh'), ('أرتا', 'Arta'),
        ('ديخيل', 'Dikhil'), ('أوبوك', 'Obock'), ('تاجورة', 'Tadjourah'),
        ('هلهل', 'Holhol'), ('دورا', 'Dorra'),
    ]),
    ('KM', 'جزر القمر', 'Comoros', [
        ('موروني', 'Moroni'), ('موتسامودو', 'Moutsamoudou'), ('فومبوني', 'Fomboni'),
        ('ميتسامیولي', 'Mitsamiouli'), ('دومبيني', 'Dembeni'), ('دوموني', 'Domoni'),
        ('مبيني', 'Mbeni'), ('واني', 'Ouani'), ('إيتسندرا', 'Itsandra'),
        ('فومبوني الغربية', 'Foumbouni'),
    ]),
    ('MR', 'موريتانيا', 'Mauritania', [
        ('نواكشوط', 'Nouakchott'), ('نواذيبو', 'Nouadhibou'), ('كيفة', 'Kiffa'),
        ('روصو', 'Rosso'), ('ازويرات', 'Zouerate'), ('العيون', 'Aioun'),
        ('أطار', 'Atar'), ('كيهيدي', 'Kaédi'), ('ألاك', 'Aleg'),
        ('سيلبابي', 'Sélibaby'), ('نعمة', 'Néma'), ('تجكجة', 'Tijigja'),
        ('تمبدرة', 'Timbedra'), ('أكجوجت', 'Akjoujt'), ('شنقيط', 'Chinguetti'),
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
