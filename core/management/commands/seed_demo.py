import random
from datetime import date

from django.core.management.base import BaseCommand

from core.models import (
    Achievement,
    Building,
    Category,
    Department,
    Direction,
    Document,
    Education,
    Event,
    Highlight,
    ImportantDate,
    MediaItem,
    Person,
    Region,
    StatCard,
    Tag,
    YearArchive,
)

YEARS = list(range(2017, 2027))

REGIONS = [
    ("Toshkent shahri", 1, False),
    ("Toshkent viloyati", 2, False),
    ("Samarqand viloyati", 3, False),
    ("Buxoro viloyati", 4, False),
    ("Farg'ona viloyati", 5, False),
    ("Namangan viloyati", 6, False),
    ("Qashqadaryo viloyati", 7, False),
    ("Navoiy viloyati", 8, False),
    ("Andijon viloyati", 9, False),
    ("Jizzax viloyati", 10, False),
    ("Surxondaryo viloyati", 11, False),
    ("Sirdaryo viloyati", 12, False),
    ("Xorazm viloyati", 13, False),
    ("Buxoro shahri", 14, False),
    ("Qoraqalpog'iston Respublikasi", 15, False),
    ("Boshqa hududlar", 99, True),
]

CATEGORIES = [
    ("Hududiy bo'linmalar", "🛡️", "#1d4ed8", 1),
    ("Maxsus bo'linmalar", "🏃", "#16a34a", 2),
    ("Ta'lim muassasalari", "🎓", "#8b5cf6", 3),
    ("Qo'shimcha xizmat bo'linmalari", "➕", "#ef4444", 4),
    ("Tibbiy bo'linmalar", "➕", "#dc2626", 5),
    ("Logistika va ta'minot", "🚚", "#eab308", 6),
    ("Aloqa va axborot", "📡", "#0ea5e9", 7),
    ("Qo'riqlash va konvoy", "🚨", "#f97316", 8),
]

DEPARTMENTS = [
    ("Bosh boshqarma", 2017, "Bosh boshqarma", "Toshkent shahri"),
    ("Qo'riqlash bo'linmalari", 2017, "Qo'riqlash va konvoy", "Toshkent shahri"),
    ("Maxsus vazifalar bo'linmasi", 2018, "Maxsus bo'linmalar", "Toshkent viloyati"),
    ("Jamoat tartibini ta'minlash bo'linmasi", 2017, "Hududiy bo'linmalar", "Toshkent shahri"),
    ("Hududiy boshqarmalar", 2017, "Hududiy bo'linmalar", "Samarqand viloyati"),
    ("Ta'lim va o'quv muassasalari", 2018, "Ta'lim muassasalari", "Toshkent shahri"),
    ("Tibbiy ta'minot bo'linmasi", 2019, "Tibbiy bo'linmalar", "Toshkent shahri"),
    ("Logistika va ta'minot bo'linmasi", 2017, "Logistika va ta'minot", "Toshkent viloyati"),
    ("Aloqa va axborot tizimlari", 2018, "Aloqa va axborot", "Toshkent shahri"),
    ("Muhandislik va texnik ta'minot", 2018, "Logistika va ta'minot", "Buxoro viloyati"),
    ("Aviatsiya ta'minot bo'linmalari", 2019, "Maxsus bo'linmalar", "Farg'ona viloyati"),
    ("Kino va axborot xizmati", 2020, "Aloqa va axborot", "Toshkent shahri"),
    ("Samarqand hududiy boshqarmasi", 2018, "Hududiy bo'linmalar", "Samarqand viloyati"),
    ("Buxoro hududiy boshqarmasi", 2019, "Hududiy bo'linmalar", "Buxoro viloyati"),
    ("Farg'ona hududiy boshqarmasi", 2019, "Hududiy bo'linmalar", "Farg'ona viloyati"),
    ("Namangan hududiy boshqarmasi", 2020, "Hududiy bo'linmalar", "Namangan viloyati"),
    ("Qashqadaryo hududiy boshqarmasi", 2020, "Hududiy bo'linmalar", "Qashqadaryo viloyati"),
    ("Navoiy hududiy boshqarmasi", 2021, "Hududiy bo'linmalar", "Navoiy viloyati"),
    ("Andijon hududiy boshqarmasi", 2021, "Hududiy bo'linmalar", "Andijon viloyati"),
    ("Jizzax hududiy boshqarmasi", 2022, "Hududiy bo'linmalar", "Jizzax viloyati"),
    ("Surxondaryo hududiy boshqarmasi", 2022, "Hududiy bo'linmalar", "Surxondaryo viloyati"),
    ("Sirdaryo hududiy boshqarmasi", 2023, "Hududiy bo'linmalar", "Sirdaryo viloyati"),
    ("Xorazm hududiy boshqarmasi", 2023, "Hududiy bo'linmalar", "Xorazm viloyati"),
    ("Qoraqalpog'iston hududiy boshqarmasi", 2024, "Hududiy bo'linmalar", "Qoraqalpog'iston Respublikasi"),
]

BUILDING_TYPES = [
    ("mamuriy", "Ma'muriy bino"),
    ("quv_markaz", "O'quv markazi"),
    ("yashash", "Yashash majmuasi"),
    ("tibbiy", "Tibbiy inshoot"),
    ("bolinma", "Bo'linma binosi"),
    ("logistika", "Logistika markazi"),
    ("aloqa", "Aloqa markazi"),
    ("sport", "Sport majmuasi"),
    ("safarbarlik", "Safarbarlik inshooti"),
    ("nazorat", "Nazorat punkti"),
    ("texnik", "Texnik xizmat"),
]

BUILDINGS = [
    ("Milliy gvardiya Bosh boshqarmasi ma'muriy binosi", "mamuriy", 2023, "Toshkent shahri", 12500, 125, 300),
    ("Maxsus tayyorgarlik o'quv markazi", "quv_markaz", 2023, "Toshkent viloyati", 12500, 125, 300),
    ("Xodimlar uchun xizmat uylari", "yashash", 2023, "Toshkent shahri", 8400, 96, 240),
    ("Harbiy poliklinika", "tibbiy", 2023, "Toshkent shahri", 5200, 64, 120),
    ("Maxsus vazifalar bo'linmasi binosi", "bolinma", 2023, "Samarqand viloyati", 6100, 58, 140),
    ("Ta'minot va texnik baza markazi", "logistika", 2023, "Toshkent viloyati", 9300, 87, 90),
    ("Aloqa markazi", "aloqa", 2023, "Toshkent shahri", 4700, 41, 70),
    ("Harbiy sport majmuasi", "sport", 2023, "Buxoro viloyati", 7600, 72, 180),
    ("Zaxira boshqarmasi binosi", "bolinma", 2023, "Farg'ona viloyati", 5400, 48, 95),
    ("Ko'p funksiyali nazorat punkti", "nazorat", 2023, "Namangan viloyati", 2300, 18, 40),
    ("Avtotexnika xizmat ko'rsatish markazi", "texnik", 2023, "Qashqadaryo viloyati", 3800, 27, 55),
    ("Hududiy boshqarma binosi", "mamuriy", 2023, "Navoiy viloyati", 4900, 44, 85),
    ("Safarbarlik inshooti", "safarbarlik", 2024, "Andijon viloyati", 6800, 61, 130),
    ("Yangi o'quv sinflari majmuasi", "quv_markaz", 2024, "Toshkent shahri", 7200, 68, 210),
    ("Tibbiy-ekologik markaz", "tibbiy", 2024, "Samarqand viloyati", 4100, 36, 75),
    ("Markaziy ombor bazasi", "logistika", 2024, "Toshkent viloyati", 11200, 104, 110),
    ("Sport va jismoniy tayyorgarlik majmuasi", "sport", 2025, "Toshkent shahri", 8900, 81, 260),
    ("Yangi ma'muriy bino", "mamuriy", 2025, "Buxoro viloyati", 5600, 52, 100),
    ("Axborot-kommunikatsiya markazi", "aloqa", 2025, "Farg'ona viloyati", 4400, 39, 65),
    ("Yashash majmuasi — 2-uy", "yashash", 2025, "Namangan viloyati", 9700, 89, 280),
    ("Qo'shimcha o'quv korpusi", "quv_markaz", 2026, "Toshkent viloyati", 6300, 57, 160),
    ("Hududiy tibbiy punkt", "tibbiy", 2026, "Qashqadaryo viloyati", 2700, 21, 45),
    ("Texnik xizmat bazasi", "texnik", 2026, "Sirdaryo viloyati", 3500, 26, 50),
    ("Yangi nazorat punkti", "nazorat", 2026, "Xorazm viloyati", 1900, 15, 35),
]

ACHIEVEMENTS = [
    ("Xalqaro maxsus bo'linmalar musobaqasida 1-o'rin", "xalqaro", date(2024, 11, 15), "Toshkent shahri"),
    ("Jamoat tartibini ta'minlash yo'nalishida eng yaxshi natija", "respublika", date(2023, 9, 21), "Toshkent shahri"),
    ("Harbiy ko'pkurash musobaqasida g'alaba", "sport", date(2023, 5, 10), "Buxoro viloyati"),
    ("Snayperlarning musobaqasida 1-o'rin", "kasbiy", date(2022, 10, 3), "Farg'ona viloyati"),
    ("Zamonaviy kuzatuv tizimi bo'yicha eng yaxshi loyiha", "innovatsion", date(2022, 6, 18), "Toshkent viloyati"),
    ("Davlat mukofoti bilan taqdirlash", "mukofot", date(2021, 12, 28), "Toshkent shahri"),
    ("Xalqaro «SWAT Challenge» musobaqasida muvaffaqiyatli ishtirok", "xalqaro", date(2020, 2, 17), "Toshkent shahri"),
    ("Respublika ko'rik-tanlovida g'oliblik", "respublika", date(2019, 9, 12), "Samarqand viloyati"),
    ("Dzyudo bo'yicha chempionlik", "sport", date(2018, 4, 25), "Namangan viloyati"),
    ("Xalqaro qo'riqlash bo'linmalari bellashuvida 2-o'rin", "xalqaro", date(2024, 6, 8), "Toshkent shahri"),
    ("Respublika taktik tayyorgarlik tanlovi g'olibi", "taktik", date(2023, 3, 17), "Qashqadaryo viloyati"),
    ("Yilning eng yaxshi mutaxassisi deb tanlandi", "respublika", date(2025, 2, 11), "Toshkent shahri"),
    ("Xalqaro avtomobil haydash chempionatida 3-o'rin", "xalqaro", date(2025, 7, 4), "Samarqand viloyati"),
    ("Zamonaviy dron texnologiyalari joriy etilgani uchun mukofot", "innovatsion", date(2024, 4, 22), "Toshkent viloyati"),
    ("Respublika sport o'yinlarida 1-o'rin", "sport", date(2022, 8, 14), "Andijon viloyati"),
    ("Harbiy tibbiyot xizmati bo'yicha malaka oshirish kursini muvaffaqiyatli tugatganlik", "kasbiy", date(2021, 5, 26), "Toshkent shahri"),
    ("Xalqaro treningda eng yaxshi jamoa", "xalqaro", date(2023, 11, 2), "Toshkent shahri"),
    ("Davlat raqobat dasturi doirasida mukofotlanish", "mukofot", date(2020, 10, 5), "Buxoro viloyati"),
]

EVENTS = [
    ("Yangi ma'muriy bino foydalanishga topshirildi", "marosim", date(2023, 3, 14), "Toshkent shahri", "Yangi bino"),
    ("Yangi bo'linma tashkil etildi", "marosim", date(2023, 3, 14), "Toshkent shahri", "Bo'linma"),
    ("Xalqaro musobaqada g'alaba qozonildi", "musobaqa", date(2023, 4, 27), "Toshkent shahri", "G'alaba"),
    ("Tantana marosimi o'tkazildi", "marosim", date(2023, 11, 11), "Samarqand viloyati", "Tadbir"),
    ("Maxsus o'quv mashg'ulotlari", "trening", date(2023, 6, 3), "Toshkent viloyati", "Mashg'ulot"),
    ("Mukofotlar va yutuqlar tantanasi", "marosim", date(2023, 8, 18), "Toshkent shahri", "Mukofot"),
    ("Zamonaviy texnikalar bilan ta'minlash tadbiri", "tashrif", date(2023, 9, 21), "Toshkent viloyati", "Texnika"),
    ("Tarixiy hujjatlarni taqdim etish marosimi", "marosim", date(2023, 12, 24), "Toshkent shahri", "Hujjat"),
    ("Yoshlar o'rtasida tanlov", "tanlov", date(2024, 5, 19), "Buxoro viloyati", "Tanlov"),
    ("Qo'shimcha tayyorgarlik mashg'ulotlari", "trening", date(2024, 7, 2), "Farg'ona viloyati", "Mashg'ulot"),
    ("Vazifaviy vazifalarni bajarish bo'yicha amaliyot", "trening", date(2025, 3, 8), "Toshkent shahri", "Amaliyot"),
    ("Xizmat sohasidagi eng yaxshi mutaxassislar tanlovi", "tanlov", date(2025, 9, 14), "Namangan viloyati", "Tanlov"),
]

EDUCATIONS = [
    ("Maxsus tayyorgarlik kurslari", "malaka", date(2023, 6, 20), 120, "6 oy"),
    ("Ofitserlar malaka oshirish seminari", "seminar", date(2023, 9, 12), 64, "2 hafta"),
    ("Qo'riqlash bo'linmalari uchun o'quv kursi", "kurs", date(2024, 2, 19), 85, "3 oy"),
    ("Taktik va amaliy mashg'ulotlar", "amaliyot", date(2024, 6, 4), 140, "1 oy"),
    ("Axborot xavfsizligi bo'yicha trening", "seminar", date(2024, 10, 8), 48, "5 kun"),
    ("Tibbiy yordam ko'rsatish kursi", "kurs", date(2025, 1, 27), 76, "4 oy"),
    ("O'quv markazi bitiruvchilari diplom topshirish", "oquv_markaz", date(2025, 5, 30), 210, "2 kun"),
    ("Kasbiy sport tayyorgarligi", "amaliyot", date(2025, 8, 11), 95, "2 oy"),
]

DOCUMENTS = [
    ("Milliy gvardiya tashkil etilishi to'g'risidagi qaror", "tarixiy", date(2017, 1, 14), "01-04", 12),
    ("Vazirlar Mahkamasining qarori", "farmoyish", date(2017, 4, 6), "174", 8),
    ("Tashkiliy tuzilma va nizomi", "hujjat", date(2018, 2, 20), "MG-113", 24),
    ("Xodimlarni rag'batlantirish bo'yicha buyruq", "buyruq", date(2019, 6, 12), "MG-452", 6),
    ("Jamoat tartibini ta'minlash bo'yicha yo'riqnoma", "hujjat", date(2020, 3, 9), "MG-781", 32),
    ("Zamonaviy texnikalarini qabul qilish dalolatnomasi", "hujjat", date(2021, 11, 25), "MG-1204", 15),
    ("Yangi bino foydalanishga topshirilishi to'g'risida akt", "hujjat", date(2023, 3, 14), "MG-317", 7),
    ("Milliy gvardiya bayrog'i va gerbi to'g'risidagi nizom", "relikiya", date(2018, 5, 9), "05-12", 18),
    ("Birinchi qabul qilingan shartnoma nusxasi", "relikiya", date(2017, 2, 1), "ARX-001", 4),
    ("Tarixiy fotodokumentlar to'plami", "tarixiy", date(2022, 7, 19), "ARX-448", 96),
]

PERSONS = [
    ("Bosh qo'mondon", "rahbar", date(1975, 5, 12), "2017–2021", "Toshkent shahri"),
    ("Bosh qo'mondon o'rinbosari", "rahbar", date(1978, 9, 3), "2021–hozirgacha", "Toshkent shahri"),
    ("Tashkiliy-shtab boshqarmasi boshlig'i", "rahbar", date(1980, 12, 24), "2019–hozirgacha", "Toshkent shahri"),
    ("Qo'riqlash bo'linmasi qo'mondoni", "rahbar", date(1983, 4, 17), "2020–hozirgacha", "Toshkent viloyati"),
    ("Maxsus vazifalar bo'linmasi qo'mondoni", "rahbar", date(1981, 8, 8), "2022–hozirgacha", "Toshkent viloyati"),
    ("Vatanparvarlikda xizmat qilgan fidoyi xodim", "qahramon", date(1972, 3, 29), "1995–2015", "Samarqand viloyati"),
    ("Jasorat ko'rsatgan harbiy xizmatchi", "qahramon", date(1990, 11, 5), "2012–2020", "Farg'ona viloyati"),
    ("Milliy gvardiya tashkil etish ishtirokchisi", "tarixiy", date(1968, 6, 18), "2017–2019", "Toshkent shahri"),
    ("Birinchi o'quv markazi rahbari", "tarixiy", date(1971, 10, 2), "2018–2023", "Toshkent shahri"),
    ("Muzey arxivining asoschisi", "shaxs", date(1985, 2, 14), "2019–hozirgacha", "Toshkent shahri"),
]

IMPORTANT_DATES = [
    ("Milliy gvardiya tashkil etilgan kun", date(2017, 1, 14), "O'zbekiston Respublikasi Milliy gvardiyasi rasman tashkil etildi."),
    ("Birinchi boshqarma shay qilinganligi", date(2017, 4, 6), "Vazirlar Mahkamasi qarori bilan tuzilma shakllantirildi."),
    ("Yangi ma'muriy bino foydalanishga topshirildi", date(2023, 3, 14), "Milliy gvardiyaning yangi ma'muriy binosi tantanali ravishda foydalanishga topshirildi."),
    ("Yangi bo'linma tashkil etildi", date(2023, 3, 14), "Tuzilmada yangi hududiy bo'linma tashkil etildi."),
    ("Xalqaro musobaqada g'alaba kiritildi", date(2023, 4, 27), "Xalqaro musobaqada jamoamiz 1-o'rinni egalladi."),
    ("Tantana marosimi o'tkazildi", date(2023, 11, 11), "Vatanparvarlik tantanasi keng nishonlandi."),
    ("O'quv markazi ochilishi", date(2023, 6, 20), "Maxsus tayyorgarlik o'quv markazi ishga tushdi."),
    ("Zamonaviy texnikalar qabul qilindi", date(2021, 11, 25), "Yangi texnikalar xizmatga kiritildi."),
    ("Aloqa va axborot tizimlari shakllantirildi", date(2019, 5, 3), "Aloqa va axborot tizimlari bo'linmasi tashkil etildi."),
    ("Harbiy sport majmuasi ochildi", date(2023, 9, 18), "Yangi sport inshoati foydalanishga topshirildi."),
]

STATS = [
    ("24", "Yangi bino<br>2011–2026 yillarda", "🏛️", "#1d4ed8", 1),
    ("12", "Viloyat va shahar", "📍", "#16a34a", 2),
    ("8 460", "Qo'shimcha xizmat o'rinlari", "👥", "#eab308", 3),
    ("1,2 trln so'm", "Umumiy qurilish qiymati", "💰", "#8b5cf6", 4),
    ("156", "Jami g'alabalar", "🏆", "#ef4444", 5),
    ("124", "Arxiv materiallari", "📄", "#0ea5e9", 6),
]

DIRECTIONS = [
    ("Milliy gvardiya tizimining shakllanishi",
     "2017-yildan buyon tashkil etilish tarixi, shakllanish bosqichlari, markaziy va hududiy tuzilmalar, vazifalar hamda tashkiliy rivojlanish. Ekspozitsiya: tashkiliy hujjatlar, dastlabki faoliyat, muhim sanalar, tarixiy fotosuratlar va yillik kronika.",
     "core:yillar", "calendar"),
    ("Milliy gvardiya qo'mondonligi",
     "Milliy gvardiya qo'mondonligi tarixi, rahbarlar faoliyati va xizmat yo'li, nishonga tayinlashga oid rasmiy hujjatlar, yo'riqnomalar va ustuvor vazifalar. Biografik ma'lumotlar faqat rasmiy tasdiqlangan ochiq manbalar asosida joylashtiriladi.",
     "core:shaxslar", "user"),
    ("Normativ-huquqiy hujjatlar",
     "Milliy gvardiyaning huquqiy maxosi, asosiy vazifalari va vakolatlarini belgilagan qonunlar, Prezident farmon va qarorlari, Vazirlar Mahkamasi hujjatlari hamda idora normativ hujjatlari. Har bir hujjatda raqami, sanasi, amaldagi tahriri va LexUZ havolasi beriladi.",
     "core:hujjatlar", "file"),
    ("Xalqaro hamkorlik",
     "Xorijiy davlatlar va xalqaro tashkilotlar bilan rasmiy uchrashuvlar, delegatsiya tashriflari, tajriba almashinishi, memorandumlarni imzolash va qo'shma tadbirlar. Har bir e'zovda ishtirokchilar, sana, maqsad va erishilgan kelishuvlar rasmiy xabar doirasida eritiladi.",
     "core:tadbirlar", "users"),
    ("Jamoat tartibini saqlash",
     "Jamoat tartibini saqlash, fuqarolar gavjum joylarida xavfsizlik, ommaviy tadbirlarda xizmat, huquqbuzarliklarning oldini olish va qurilish faoliyati va konchilikka oid boshqa vazifalar. Amaliy misollar faqat ochiq va tarqatilishi mumkin bo'lgan rasmiy materiallardan olinadi.",
     "core:bolinmalar", "shield"),
    ("Milliy gvardiya tizimidagi o'zgarishlar",
     "Milliy gvardiya tizimidagi huquqiy, tashkiliy va funksional islohotlar, yangi vazifalar, boshqaruvni takomillashtirish va xavfsizlik tizimi bilan hamkorlik. Har bir islohot tegishli normativ hujjat va amalga oshirish sanasi bilan bog'lanadi.",
     "core:binolar", "building"),
    ("Ta'minot yo'nalishlari",
     "Xizmat faoliyati ta'minotiga xizmat ko'rsatish transport, aloqa, maxsus texnika, kiyim-bosh, jihozlar va moddiy-texnik ta'minotning ochiq tarixi. Texnik tavsiflar va tavsiflar faqat omma e'lon qilinishiga ruxsat etilgan ma'lumotlardan shakllantiriladi.",
     "core:talim", "cap"),
    ("Milliy gvardiya va e'shlar",
     "Vatanparvarlik tarixi, ma'naviy-ma'rifiy ishlar, kutubxonachilik, e'shlar bilan uchrashuvlar, ta'lim muassasalari, qurbonlar xayriyasi va tarbiyaviy tadbirlar. Kasbiy, bitiruv, ko'rik-tanlov va ma'naviy po'xatlar fotoxronikasi bilan boyitiladi.",
     "core:galereya", "image"),
    ("Federatsiyalar faoliyati",
     "Milliy gvardiya tizimidagi sport yo'nalishlari, federatsiya va sport maktablari, respublika hamda xalqaro musobaqalar, g'oliblar, murabbiylar va ommaviy sport tadbirlari. Natijalar musobaqa nomi, sana va rasmiy baynoma bilan tasdiqlanadi.",
     "core:galabalar", "trophy"),
    ("Bizning qahramonlar",
     "Xizmat vazifasi davomida jasorat ko'rsatgan xodimlar, xalq bo'lgan qahramonlar xotirasi, xizmat faoliyati va avlodlar vorisligi. Shaxsiy tarixlar oilasi va vakolatli tuzilma roziligi, rasmiy tasdiq va axborot xavfsizligi talablariga mos muvofiqlashtiriladi.",
     "core:sanalar", "star"),
]


class Command(BaseCommand):
    help = "Muzey uchun namoyish ma'lumotlarini yaratadi"

    def handle(self, *args, **options):
        if Department.objects.exists():
            self.stdout.write(self.style.WARNING("Ma'lumotlar allaqachon mavjud — seed o'tkazib yuborildi."))
            return

        regions = {}
        for name, order, is_other in REGIONS:
            regions[name] = Region.objects.create(name=name, order=order, is_other=is_other)
        self.stdout.write(f"  + {len(regions)} hudud")

        cats = {}
        for name, icon, color, order in CATEGORIES:
            cats[name] = Category.objects.create(name=name, icon=icon, color=color, order=order)
        self.stdout.write(f"  + {len(cats)} kategoriya")

        for i in range(1, 11):
            title, description, url, icon = DIRECTIONS[i - 1]
            Direction.objects.create(
                number=i, title=title, description=description, url=url, icon=icon,
            )

        for value, label, icon, color, order in STATS:
            StatCard.objects.create(value=value, label=label, icon=icon, color=color, order=order)

        for y in YEARS:
            YearArchive.objects.create(
                year=y,
                title={
                    2017: "Tashkil etilish va shakllanish yili",
                    2018: "Institutsional rivojlanish yili",
                    2019: "Tuzilish va infratuzilma yili",
                    2020: "Barqarorlik va modernizatsiya yili",
                    2021: "Texnik ta'minot va yangilanish yili",
                    2022: "Transformatsiya yili",
                    2023: "Rivojlanish va yangi imkoniyatlar yili",
                    2024: "Sifatli boshqaruv yili",
                    2025: "Raqqamli transformatsiya yili",
                    2026: "Yangi bosqich yili",
                }.get(y, f"{y}-yil"),
                subtitle="Rivojlanish yili",
                description=f"{y}-yil Milliy gvardiya uchun muhim ishlar, yangi binolar ochilishi, zamonaviy texnikalar bilan ta'minlash, aholi xavfsizligini ta'minlash yo'nalishida muhim natijalarga erishgan yildir.",
                new_buildings=random.randint(4, 12),
                new_departments=random.randint(2, 8),
                achievements=random.randint(12, 30),
                documents=random.randint(80, 340),
                is_featured=(y == 2023),
            )
        self.stdout.write(f"  + {len(YEARS)} yil arxivi")

        tag_names = ["yangi bino", "ma'muriy bino", "rivojlanish", "infratuzilima", "Toshkent", "musobaqa", "mukofot", "tarix", "o'quv markazi", "tantana", "texnika", "hujjat"]
        tags = {}
        for t in tag_names:
            tags[t] = Tag.objects.create(name=t)

        deps = []
        for title, year_start, cat_name, region_name in DEPARTMENTS:
            d = Department.objects.create(
                title=title,
                year_start=year_start,
                year_end="hozirgacha" if year_start < 2024 else "2026",
                summary=f"{title} — Milliy gvardiyaning {year_start}-yildan buyon faoliyat yurituvchi tuzilmasi.",
                description=(
                    f"{title} {year_start}-yilda tashkil etilgan bo'lib, Milliy gvardiyaning asosiy yo'nalishlari bo'yicha vazifalarni amalga oshiradi.\n"
                    f"Bo'linma huquqiy asoslar, tashkiliy-huquqiy hujjatlar va buyruqlar asosida o'z faoliyatini yuritadi. Tarixi, shakllanish bosqichlari, rahbarlar faoliyati va erishilgan natijalar muzey arxivida saqlanadi.\n"
                    f"Bo'linma hududi: {region_name}. Bo'linma raqamli arxivda 2017-yildan buyon to'plangan materiallar jamlangan."
                ),
                region=regions.get(region_name),
                category=cats.get(cat_name),
                photo_count=random.randint(30, 130),
                video_count=random.randint(5, 30),
                doc_count=random.randint(5, 20),
                views=random.randint(40, 400),
                order=len(deps) + 1,
            )
            deps.append(d)
        self.stdout.write(f"  + {len(deps)} bo'linma")

        for i, (title, btype, year, region_name, area, cost, cap) in enumerate(BUILDINGS, 1):
            b = Building.objects.create(
                title=title,
                building_type=btype,
                year=year,
                handover_date=date(year, (i % 12) + 1, min(28, (i * 3) % 27 + 1)),
                address=f"{region_name}, {random.randint(1, 40)}-kvartal",
                region=regions.get(region_name),
                department=deps[i % len(deps)],
                area_m2=area,
                cost=cost,
                capacity=cap,
                description=(
                    f"{title} {year}-yilda Milliy gvardiyaning moddiy-texnik bazasini mustahkamlash, zamonaviy infratuzilmani rivojlantirish va xizmat sharoitlarini yaxshilash maqsadida foydalanishga topshirilgan.\n"
                    f"Mazkur inshot zamonaviy talablar asosida qurilgan bo'lib, boshqaruv faoliyatini samarali tashkil etish, xodimlar uchun qulay sharoit yaratish hamda xizmat sifatini yana oshirishga xizmat qiladi.\n"
                    f"Qurilish maydoni {area} m², qurilish qiymati {cost} mlrd so'm, xizmat o'rinlari soni {cap} nafarni tashkil etadi."
                ),
                photo_count=random.randint(8, 32),
                video_count=random.randint(1, 8),
                doc_count=random.randint(2, 8),
                views=random.randint(30, 300),
                order=i,
            )
            for j in range(1, 5):
                Highlight.objects.create(
                    title=["Zamonaviy infratuzilma", "Xodimlar uchun sharoit", "Zamonaviy texnologiyalar", "Xizmat sifati"][j - 1],
                    text=[
                        "Barcha bo'limlar uchun qulay va samarali muhit",
                        "Ish va dam olish uchun zamonaviy imkoniyatlar",
                        "Axborot tizimlari va boshqaruv texnikasi bilan jihozlangan",
                        "Operativ boshqaruv va faoliyat samaradorligi oshadi",
                    ][j - 1],
                    icon=["🏛️", "👥", "🖼️", "🛡️"][j - 1],
                    building=b,
                    order=j,
                )
        self.stdout.write(f"  + {len(BUILDINGS)} bino")

        type_list = list(Achievement.ACHIEVEMENT_TYPES)
        for i, (title, atype, dt, region_name) in enumerate(ACHIEVEMENTS, 1):
            Achievement.objects.create(
                title=title,
                achievement_type=atype,
                material_type="galaba",
                date=dt,
                year=dt.year,
                region=regions.get(region_name),
                department=deps[i % len(deps)],
                category=cats.get("Maxsus bo'linmalar"),
                summary=f"{title} — {dt.year}-yilda erishilgan muhim natija.",
                description=(
                    f"{dt.year}-yil {dt.strftime('%d-%m')} kuni {region_name} hududida o'tkazilgan musobaqada "
                    f"Milliy gvardiya jamoasi «{title}» natijasini qayd etdi.\n"
                    f"Musobaqada maxsus vazifalar bo'linmalari, qo'riqlash va jamoat tartibini ta'minlash xizmatchilari ishtirok etdi. "
                    f"Natijalar hakamlar hay'ati tomonidan rasmiy baynoma bilan tasdiqlandi.\n"
                    f"Yutuq jamoaning kasbiy mahorati, jismoniy tayyorgarligi va o'zaro hamkorligining mahsuli bo'lib, xizmat faoliyatini yangi bosqichga olib chiqdi."
                ),
                photo_count=random.randint(4, 30),
                video_count=random.randint(1, 10),
                doc_count=random.randint(1, 10),
                views=random.randint(20, 300),
                is_featured=(i <= 6),
            )
        self.stdout.write(f"  + {len(ACHIEVEMENTS)} g'alaba")

        etypes = list(Event.EVENT_TYPES)
        for i, (title, etype, dt, region_name, tag) in enumerate(EVENTS, 1):
            e = Event.objects.create(
                title=title,
                event_type=etype,
                material_type="tadbir",
                date=dt,
                year=dt.year,
                region=regions.get(region_name),
                department=deps[i % len(deps)],
                location=f"{region_name}, Milliy gvardiya majmuasi",
                start_time="10:00",
                summary=f"{title} — {dt.strftime('%d.%m.%Y')} kuni {region_name}da o'tkazildi.",
                description=(
                    f"{dt.strftime('%d-%m-%Y')} kuni {region_name}da «{title}» tadbiri bo'lib o'tdi.\n"
                    f"Tadbirda Milliy gvardiya rahbariyati, hududiy tuzilmalar xizmatchilari, mehmonlar va ommaviy axborot vositalari ishtirok etdi.\n"
                    f"Tadbir davomida so'zga chiqishlar, taqdimotlar va rasmiy marosimlar bo'lib o'tdi. Materiallar muzey arxivida saqlanmoqda."
                ),
                photo_count=random.randint(6, 40),
                video_count=random.randint(1, 8),
                doc_count=random.randint(1, 8),
                views=random.randint(20, 250),
            )
            for tn in random.sample(tag_names, 3):
                e.tags.add(tags[tn])
        self.stdout.write(f"  + {len(EVENTS)} tadbir")

        for i, (title, etype, dt, count, dur) in enumerate(EDUCATIONS, 1):
            Education.objects.create(
                title=title,
                edu_type=etype,
                material_type="malumot",
                date=dt,
                year=dt.year,
                department=deps[i % len(deps)],
                duration=dur,
                students_count=count,
                summary=f"{title} — {count} nafar xodim qatnashdi.",
                description=(
                    f"«{title}» {dt.strftime('%d-%m-%Y')} sanasida tashkil etildi.\n"
                    f"Mashg'ulot davomiyligi {dur}, qatnashchilar soni {count} nafar. "
                    f"O'quv dasturi nazariy va amaliy qismlardan iborat bo'lib, zamonaviy talablarga mos ravishda tuzilgan.\n"
                    f"Barcha qatnashchilarga tegishli hujjat va sertifikatlar topshirildi."
                ),
                photo_count=random.randint(5, 25),
                video_count=random.randint(1, 6),
                doc_count=random.randint(1, 6),
            )
        self.stdout.write(f"  + {len(EDUCATIONS)} ta'lim mashg'uloti")

        for i, (title, dtype, dt, number, pages) in enumerate(DOCUMENTS, 1):
            Document.objects.create(
                title=title,
                doc_type=dtype,
                material_type="hujjat",
                doc_number=number,
                date=dt,
                year=dt.year,
                department=deps[i % len(deps)],
                pages=pages,
                summary=f"{title} (№ {number})",
                description=(
                    f"«{title}» hujjati {dt.strftime('%d-%m-%Y')} sanasida qabul qilingan.\n"
                    f"Hujjat raqami: {number}. Sahifalar soni: {pages}.\n"
                    f"Ushbu hujjat Milliy gvardiyaning tashkiliy-huquqiy bazasini shakllantirishda muhim ahamiyatga ega bo'lib, arxiv nusxasi sifatida saqlanadi."
                ),
                photo_count=1,
                video_count=0,
                doc_count=1,
            )
        self.stdout.write(f"  + {len(DOCUMENTS)} hujjat")

        for i, (name, ptype, bdate, period, region_name) in enumerate(PERSONS, 1):
            Person.objects.create(
                full_name=name,
                position=name,
                person_type=ptype,
                birth_date=bdate,
                service_period=period,
                department=deps[i % len(deps)],
                bio=(
                    f"{name} — Milliy gvardiya tizimida {period} davrida xizmat qilgan.\n"
                    f"Xizmat davri davomida tashkiliy, huquqiy va amaliy vazifalarni bajarish, "
                    f"yoshlar bilan ishlash va professional tayyorgarlikni kuchaytirish bo'yicha ishlar olib borildi.\n"
                    f"Faqat rasmiy tasdiqlangan ochiq manbalar asosidagi ma'lumotlar joylashtirilgan."
                ),
                awards="Davlat mukofotlari, idoraviy nishonlar va faxriy yorliqlar bilan taqdirlangan" if i % 3 == 0 else "",
                views=random.randint(10, 120),
                order=i,
            )
        self.stdout.write(f"  + {len(PERSONS)} shaxs")

        for i, (title, dt, desc) in enumerate(IMPORTANT_DATES, 1):
            ImportantDate.objects.create(
                title=title,
                date=dt,
                description=desc,
                is_featured=(i <= 4),
            )
        self.stdout.write(f"  + {len(IMPORTANT_DATES)} muhim sana")

        media_titles = [
            "Yangi bino ochilish marosimi", "Ichki ko'rinish va sharoitlar", "Rahbariyat nutqi",
            "Loyiha hujjatlari", "Qurilish jarayoni", "Maxsus mashg'ulot", "Tantana marosimi",
            "O'quv mashg'uloti", "Otish poligoni", "Sport musobaqasi", "Texnik jihozlar",
            "Bo'linma shayligi", "Hududiy tadbir", "Arxiv materiallari", "Mukofotlash marosimi",
        ]
        for i in range(1, 41):
            dt = date(random.choice(YEARS), random.randint(1, 12), random.randint(1, 28))
            title = media_titles[i % len(media_titles)]
            MediaItem.objects.create(
                title=f"{title} — {dt.strftime('%d.%m.%Y')}",
                media_type="photo" if i % 4 else "video",
                date=dt,
                year=dt.year,
                department=deps[i % len(deps)],
                event=Event.objects.order_by("?").first() if i % 5 == 0 else None,
                description=f"{title} — {dt.year}-yilda olingan foto va video materiallar to'plami.",
                views=random.randint(5, 150),
                order=i,
            )
        self.stdout.write("  + 40 ta media material")

        self.stdout.write(self.style.SUCCESS("\nSeed muvaffaqiyatli yakunlandi!"))
        self.stdout.write("Admin panel: /admin/ (admin / admin123)")
