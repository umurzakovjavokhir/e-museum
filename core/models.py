from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("Yaratilgan sana", auto_now_add=True)
    updated_at = models.DateTimeField("Yangilangan sana", auto_now=True)

    class Meta:
        abstract = True


class Region(models.Model):
    name = models.CharField("Nomi", max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    order = models.PositiveIntegerField("Tartib", default=0)
    is_other = models.BooleanField("Boshqa hududlar", default=False)

    class Meta:
        verbose_name = "Hudud"
        verbose_name_plural = "Hududlar"
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField("Nomi", max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    icon = models.CharField("Belgi (emoji/icon)", max_length=40, blank=True, default="📁")
    color = models.CharField("Rangi", max_length=20, default="#1d4ed8")
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField("Nomi", max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = "Teg"
        verbose_name_plural = "Teglar"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Department(TimeStampedModel):
    """Bo'linma — bo'linmalar tarixi bo'limi."""
    title = models.CharField("Bo'linma nomi", max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    summary = models.CharField("Qisqa tavsif", max_length=400, blank=True)
    description = models.TextField("Tavsif", blank=True)
    image = models.ImageField("Asosiy rasm", upload_to="departments/", blank=True)
    year_start = models.PositiveIntegerField("Boshlanish yili", default=2017)
    year_end = models.CharField("Tugash yili", max_length=20, default="hozirgacha")
    region = models.ForeignKey(
        Region, verbose_name="Hudud", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="departments",
    )
    category = models.ForeignKey(
        Category, verbose_name="Kategoriya", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="departments",
    )
    photo_count = models.PositiveIntegerField("Foto", default=0)
    video_count = models.PositiveIntegerField("Video", default=0)
    doc_count = models.PositiveIntegerField("Hujjat", default=0)
    views = models.PositiveIntegerField("Ko'rishlar", default=0)
    is_featured = models.BooleanField("Muhim", default=False)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        verbose_name = "Bo'linma"
        verbose_name_plural = "Bo'linmalar"
        ordering = ["order", "title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:280] or "bolinma"
            base = self.slug
            n = 2
            while Department.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base}-{n}"
                n += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:bolinma_detail", kwargs={"slug": self.slug})

    @property
    def year_range(self):
        return f"{self.year_start} - {self.year_end}"

    def __str__(self):
        return self.title


class Building(TimeStampedModel):
    """Yangi bino."""
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
    title = models.CharField("Bino nomi", max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    building_type = models.CharField("Turi", max_length=40, choices=BUILDING_TYPES, default="mamuriy")
    year = models.PositiveIntegerField("Topshirilgan yil", default=2023)
    handover_date = models.DateField("Topshirilgan sana", null=True, blank=True)
    address = models.CharField("Manzil", max_length=255, blank=True)
    region = models.ForeignKey(
        Region, verbose_name="Hudud", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="buildings",
    )
    department = models.ForeignKey(
        Department, verbose_name="Tegishli bo'linma", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="buildings",
    )
    area_m2 = models.PositiveIntegerField("Bino maydoni, m²", default=0)
    cost = models.DecimalField("Qurilish qiymati, mlrd so'm", max_digits=12, decimal_places=2, default=0)
    capacity = models.PositiveIntegerField("Xizmat o'rinlari", default=0)
    description = models.TextField("Tavsif", blank=True)
    image = models.ImageField("Asosiy rasm", upload_to="buildings/", blank=True)
    photo_count = models.PositiveIntegerField("Foto", default=0)
    video_count = models.PositiveIntegerField("Video", default=0)
    doc_count = models.PositiveIntegerField("Hujjat", default=0)
    views = models.PositiveIntegerField("Ko'rishlar", default=0)
    is_active = models.BooleanField("Foydalanishga topshirilgan", default=True)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        verbose_name = "Yangi bino"
        verbose_name_plural = "Yangi binolar"
        ordering = ["-year", "order", "title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:280] or "bino"
            base = self.slug
            n = 2
            while Building.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base}-{n}"
                n += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:bino_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class YearArchive(TimeStampedModel):
    """Yillar bo'yicha tarix yili."""
    year = models.PositiveIntegerField("Yil", unique=True)
    title = models.CharField("Yil nomi", max_length=255)
    subtitle = models.CharField("Shior", max_length=255, blank=True)
    description = models.TextField("Tavsif", blank=True)
    image = models.ImageField("Banner rasm", upload_to="years/", blank=True)
    video_url = models.URLField("Video havolasi", blank=True)
    new_buildings = models.PositiveIntegerField("Yangi bino va inshoot", default=0)
    new_departments = models.PositiveIntegerField("Yangi bo'linma", default=0)
    achievements = models.PositiveIntegerField("Erishilgan g'alaba", default=0)
    documents = models.PositiveIntegerField("Hujjat va material", default=0)
    is_featured = models.BooleanField("Muhim yil", default=False)

    class Meta:
        verbose_name = "Yil"
        verbose_name_plural = "Yillar"
        ordering = ["-year"]

    def get_absolute_url(self):
        return reverse("core:yil_detail", kwargs={"year": self.year})

    def __str__(self):
        return str(self.year)


class MaterialQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)


class AbstractMaterial(TimeStampedModel):
    MATERIAL_TYPES = [
        ("news", "Yangilik"),
        ("building", "Yangi bino"),
        ("bolinma", "Bo'linma"),
        ("tadbir", "Tadbir"),
        ("galaba", "Erishilgan g'alaba"),
        ("hujjat", "Hujjat"),
        ("foto", "Foto"),
        ("video", "Video"),
        ("malumot", "Ma'lumot"),
    ]
    title = models.CharField("Sarlavha", max_length=300)
    slug = models.SlugField(max_length=320, unique=True, blank=True)
    material_type = models.CharField("Material turi", max_length=20, choices=MATERIAL_TYPES, default="news")
    category = models.ForeignKey(
        Category, verbose_name="Kategoriya", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="%(class)ss",
    )
    date = models.DateField("Sana", null=True, blank=True)
    year = models.PositiveIntegerField("Yil", default=2023, db_index=True)
    region = models.ForeignKey(
        Region, verbose_name="Hudud", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="%(class)ss",
    )
    department = models.ForeignKey(
        Department, verbose_name="Tegishli bo'linma", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="%(class)ss",
    )
    summary = models.CharField("Qisqa tavsif", max_length=400, blank=True)
    description = models.TextField("Tavsif", blank=True)
    body = models.TextField("To'liq matn", blank=True)
    image = models.ImageField("Asosiy rasm", upload_to="%(class)ss/", blank=True)
    tags = models.ManyToManyField(Tag, verbose_name="Teglar", blank=True, related_name="%(class)ss")
    photo_count = models.PositiveIntegerField("Foto", default=0)
    video_count = models.PositiveIntegerField("Video", default=0)
    doc_count = models.PositiveIntegerField("Hujjat", default=0)
    views = models.PositiveIntegerField("Ko'rishlar", default=0)
    is_published = models.BooleanField("Chop etilgan", default=True)
    is_featured = models.BooleanField("Muhim", default=False)

    objects = MaterialQuerySet.as_manager()

    class Meta:
        abstract = True
        ordering = ["-date", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:320] or "material"
            base = self.slug
            n = 2
            model = type(self)
            while model.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base}-{n}"
                n += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Achievement(AbstractMaterial):
    """Erishilgan g'alaba."""
    ACHIEVEMENT_TYPES = [
        ("xalqaro", "Xalqaro musobaqalar"),
        ("respublika", "Respublika musobaqalar"),
        ("sport", "Sport yutuqlari"),
        ("kasbiy", "Kasbiy mahorat"),
        ("innovatsion", "Innovatsion loyihalar"),
        ("mukofot", "Mukofotlar"),
        ("taktik", "Taktik o'quvlar"),
        ("boshqa", "Boshqa"),
    ]
    achievement_type = models.CharField(
        "Yutuq turi", max_length=30, choices=ACHIEVEMENT_TYPES, default="xalqaro",
    )

    class Meta:
        verbose_name = "Erishilgan g'alaba"
        verbose_name_plural = "Erishilgan g'alabalar"
        ordering = ["-date", "-created_at"]

    def get_absolute_url(self):
        return reverse("core:galaba_detail", kwargs={"slug": self.slug})


class Event(AbstractMaterial):
    """Tadbir va marosim."""
    EVENT_TYPES = [
        ("marosim", "Marosim"),
        ("musobaqa", "Musobaqa"),
        ("tashrif", "Tashrif"),
        ("tanlov", "Tanlov"),
        ("trening", "Trening"),
        ("boshqa", "Boshqa"),
    ]
    event_type = models.CharField("Tadbir turi", max_length=30, choices=EVENT_TYPES, default="marosim")
    location = models.CharField("Joylashuv", max_length=255, blank=True)
    start_time = models.TimeField("Boshlanish vaqti", null=True, blank=True)

    class Meta:
        verbose_name = "Tadbir"
        verbose_name_plural = "Tadbirlar va marosimlar"
        ordering = ["-date", "-created_at"]

    def get_absolute_url(self):
        return reverse("core:tadbir_detail", kwargs={"slug": self.slug})


class Education(AbstractMaterial):
    """Ta'lim va o'quv mashg'uloti."""
    EDU_TYPES = [
        ("kurs", "Kurs"),
        ("seminar", "Seminar"),
        ("malaka", "Malaka oshirish"),
        ("oquv_markaz", "O'quv markazi"),
        ("amaliyot", "Amaliyot"),
        ("boshqa", "Boshqa"),
    ]
    edu_type = models.CharField("Mashg'ulot turi", max_length=30, choices=EDU_TYPES, default="kurs")
    duration = models.CharField("Davomiyligi", max_length=100, blank=True)
    students_count = models.PositiveIntegerField("Talabalar soni", default=0)

    class Meta:
        verbose_name = "Ta'lim mashg'uloti"
        verbose_name_plural = "Ta'lim va o'quv mashg'ulotlari"
        ordering = ["-date", "-created_at"]

    def get_absolute_url(self):
        return reverse("core:talim_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class Document(AbstractMaterial):
    """Hujjat va relikiya."""
    DOC_TYPES = [
        ("hujjat", "Rasmiy hujjat"),
        ("relikiya", "Relikiya"),
        ("tarixiy", "Tarixiy hujjat"),
        ("buyruq", "Buyruq"),
        ("farmoyish", "Farmoyish"),
        ("shartnoma", "Shartnoma"),
        ("boshqa", "Boshqa"),
    ]
    doc_type = models.CharField("Hujjat turi", max_length=30, choices=DOC_TYPES, default="hujjat")
    doc_number = models.CharField("Hujjat raqami", max_length=100, blank=True)
    file = models.FileField("Fayl", upload_to="documents/files/", blank=True)
    pages = models.PositiveIntegerField("Sahifalar soni", default=0)

    class Meta:
        verbose_name = "Hujjat"
        verbose_name_plural = "Hujjatlar va relikiyalar"
        ordering = ["-date", "-created_at"]

    def get_absolute_url(self):
        return reverse("core:hujjat_detail", kwargs={"slug": self.slug})


class Person(TimeStampedModel):
    """Rahbar va shaxslar."""
    PERSON_TYPES = [
        ("rahbar", "Rahbarlar"),
        ("shaxs", "Shaxsiyatlar"),
        ("qahramon", "Qahramonlar"),
        ("tarixiy", "Tarixiy shaxs"),
    ]
    full_name = models.CharField("F.I.Sh.", max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    position = models.CharField("Lavozim", max_length=255, blank=True)
    person_type = models.CharField("Turi", max_length=30, choices=PERSON_TYPES, default="rahbar")
    birth_date = models.DateField("Tug'ilgan sana", null=True, blank=True)
    service_period = models.CharField("Xizmat davri", max_length=100, blank=True)
    bio = models.TextField("Biografiya", blank=True)
    photo = models.ImageField("Surat", upload_to="persons/", blank=True)
    department = models.ForeignKey(
        Department, verbose_name="Bo'linma", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="persons",
    )
    awards = models.TextField("Mukofotlar", blank=True)
    views = models.PositiveIntegerField("Ko'rishlar", default=0)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        verbose_name = "Shaxs"
        verbose_name_plural = "Rahbarlar va shaxslar"
        ordering = ["order", "full_name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.full_name)[:280] or "shaxs"
            base = self.slug
            n = 2
            while Person.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base}-{n}"
                n += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:shaxs_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.full_name


class ImportantDate(TimeStampedModel):
    """Muhim sana."""
    title = models.CharField("Sarlavha", max_length=300)
    slug = models.SlugField(max_length=320, unique=True, blank=True)
    date = models.DateField("Sana", db_index=True)
    description = models.TextField("Tavsif", blank=True)
    image = models.ImageField("Rasm", upload_to="dates/", blank=True)
    event = models.ForeignKey(
        Event, verbose_name="Tadbir", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="important_dates",
    )
    is_featured = models.BooleanField("Muhim", default=False)

    class Meta:
        verbose_name = "Muhim sana"
        verbose_name_plural = "Muhim sanalar"
        ordering = ["-date"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:320] or "sana"
            base = self.slug
            n = 2
            while ImportantDate.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base}-{n}"
                n += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:sana_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class MediaItem(TimeStampedModel):
    """Foto va videoarxiv."""
    MEDIA_TYPES = [("photo", "Foto"), ("video", "Video")]
    title = models.CharField("Sarlavha", max_length=300)
    slug = models.SlugField(max_length=320, unique=True, blank=True)
    media_type = models.CharField("Turi", max_length=10, choices=MEDIA_TYPES, default="photo")
    image = models.ImageField("Rasm", upload_to="gallery/", blank=True)
    video_url = models.URLField("Video havola", blank=True)
    date = models.DateField("Sana", null=True, blank=True)
    year = models.PositiveIntegerField("Yil", default=2023, db_index=True)
    description = models.TextField("Tavsif", blank=True)
    department = models.ForeignKey(
        Department, verbose_name="Bo'linma", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="gallery",
    )
    event = models.ForeignKey(
        Event, verbose_name="Tadbir", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="gallery",
    )
    views = models.PositiveIntegerField("Ko'rishlar", default=0)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        verbose_name = "Media material"
        verbose_name_plural = "Foto va videoarxiv"
        ordering = ["-date", "order"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:320] or "media"
            base = self.slug
            n = 2
            while MediaItem.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base}-{n}"
                n += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:media_detail", kwargs={"slug": self.slug})

    @property
    def duration(self):
        return "04:32"

    def __str__(self):
        return self.title


class Direction(TimeStampedModel):
    """10 ta asosiy y'onalish."""
    number = models.PositiveIntegerField("Raqam", unique=True)
    title = models.CharField("Nomi", max_length=255)
    description = models.TextField("Tavsif", blank=True)
    icon = models.CharField("Belgi (svg nomi)", max_length=40, default="star")
    url = models.CharField(
        "Havola (URL nomi)", max_length=100, blank=True, default="core:yonalishlar",
    )

    class Meta:
        verbose_name = "Yo'nalish"
        verbose_name_plural = "Yo'nalishlar"
        ordering = ["number"]

    def __str__(self):
        return f"{self.number}. {self.title}"


class Highlight(TimeStampedModel):
    """Detail sahifadagi "Asosiy natijalar va imkoniyatlar" bloki."""
    title = models.CharField("Sarlavha", max_length=255)
    text = models.TextField("Matn", blank=True)
    icon = models.CharField("Belgi", max_length=40, default="🏛️")
    building = models.ForeignKey(
        Building, verbose_name="Bino", on_delete=models.CASCADE, null=True, blank=True,
        related_name="highlights",
    )
    department = models.ForeignKey(
        Department, verbose_name="Bo'linma", on_delete=models.CASCADE, null=True, blank=True,
        related_name="highlights",
    )
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        verbose_name = "Asosiy natija"
        verbose_name_plural = "Asosiy natijalar"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class StatCard(TimeStampedModel):
    """Statistika kartochkalari."""
    value = models.CharField("Qiymat", max_length=50)
    label = models.CharField("Yorliq", max_length=200)
    icon = models.CharField("Belgi", max_length=40, default="📊")
    color = models.CharField("Rangi", max_length=20, default="#1d4ed8")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        verbose_name = "Statistika kartasi"
        verbose_name_plural = "Statistika kartalari"
        ordering = ["order", "id"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.label)[:100] or "stat"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.value} — {self.label}"


class Bookmark(models.Model):
    """Saqlanganlar (session asosida)."""
    session_key = models.CharField(max_length=64, db_index=True)
    content_type = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Saqlangan"
        verbose_name_plural = "Saqlanganlar"
        unique_together = ("session_key", "content_type", "object_id")

    def __str__(self):
        return f"{self.content_type}#{self.object_id}"
