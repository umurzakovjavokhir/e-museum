from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.models import (
    Achievement,
    Bookmark,
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
    YearArchive,
)

PER_PAGE = 12


def _years():
    return sorted(
        YearArchive.objects.values_list("year", flat=True), reverse=True
    ) or list(range(2017, 2027))


def _page(request, qs, per_page=PER_PAGE):
    paginator = Paginator(qs, per_page)
    page_number = request.GET.get("page") or 1
    return paginator.get_page(page_number)


def _regions_with_counts(model):
    regions = Region.objects.all()
    rows = []
    for r in regions:
        rows.append({"name": r.name, "count": model.objects.filter(region=r).count(), "is_other": r.is_other})
    return rows


def _latest_news(limit=5):
    items = []
    for m in Achievement.objects.filter(is_published=True).order_by("-date")[:limit]:
        items.append(
            {
                "date": m.date, "title": m.summary or m.title, "image": m.image,
                "url": m.get_absolute_url(), "type": "galaba",
            }
        )
    for e in Event.objects.filter(is_published=True).order_by("-date")[:limit]:
        items.append(
            {
                "date": e.date, "title": e.summary or e.title, "image": e.image,
                "url": e.get_absolute_url(), "type": "tadbir",
            }
        )
    items.sort(key=lambda x: x["date"] or __import__("datetime").date.min, reverse=True)
    return items[:limit]


def _all_materials(year=None):
    """Yil sahifasidagi barcha materiallarni birlashtirish."""
    out = []

    def add(items, kind):
        for o in items:
            dt = getattr(o, "date", None) or getattr(o, "handover_date", None)
            out.append(
                {
                    "kind": kind,
                    "kind_label": dict(Achievement.MATERIAL_TYPES).get(kind, kind),
                    "title": o.title,
                    "date": dt,
                    "url": o.get_absolute_url(),
                    "image": getattr(o, "image", None),
                    "photos": getattr(o, "photo_count", 0),
                    "videos": getattr(o, "video_count", 0),
                    "docs": getattr(o, "doc_count", 0),
                    "views": getattr(o, "views", 0),
                }
            )

    f = {"is_published": True}
    if year:
        f["year"] = year

    add(Building.objects.filter(**({"year": year} if year else {}))[:200], "building")
    add(Department.objects.all()[:100], "bolinma")
    add(Event.objects.filter(**f)[:200], "tadbir")
    add(Achievement.objects.filter(**f)[:200], "galaba")
    add(Document.objects.filter(**f)[:200], "hujjat")
    for m in MediaItem.objects.filter(**({"year": year} if year else {}))[:200]:
        kind = "foto" if m.media_type == "photo" else "video"
        out.append(
            {
                "kind": kind,
                "kind_label": "Foto" if kind == "foto" else "Video",
                "title": m.title,
                "date": m.date,
                "url": m.get_absolute_url(),
                "image": m.image,
                "photos": 1 if kind == "foto" else 0,
                "videos": 1 if kind == "video" else 0,
                "docs": 0,
                "views": m.views,
            }
        )
    out.sort(key=lambda x: x["date"] or __import__("datetime").date.min, reverse=True)
    return out


# ---------------------------------------------------------------- Bosh sahifa
def home(request):
    ctx = {
        "active": "home",
        "stats": StatCard.objects.all()[:6],
        "buildings": Building.objects.all()[:8],
        "departments": Department.objects.all()[:8],
        "achievements": Achievement.objects.filter(is_published=True)[:6],
        "events": Event.objects.filter(is_published=True)[:6],
        "latest": _latest_news(5),
        "popular_departments": Department.objects.order_by("-views")[:4],
        "regions": _regions_with_counts(Building),
        "years": _years(),
        "directions": Direction.objects.all()[:6],
    }
    return render(request, "core/home.html", ctx)


def landing(request):
    ctx = {"active": "landing", "directions": Direction.objects.all(), "years": _years()}
    return render(request, "core/landing.html", ctx)


# ------------------------------------------------------------ Yillar bo'yicha
def yillar(request):
    year = request.GET.get("yil")
    active_year = int(year) if year and year.isdigit() else 2023
    archive = get_object_or_404(YearArchive, year=active_year)
    materials = _all_materials(active_year)

    kind = request.GET.get("tur")
    if kind:
        materials = [m for m in materials if m["kind"] == kind]

    search = request.GET.get("q", "").strip()
    if search:
        materials = [m for m in materials if search.lower() in m["title"].lower()]

    sort = request.GET.get("sort", "date")
    if sort == "views":
        materials.sort(key=lambda x: x["views"], reverse=True)

    counts = {}
    for m in _all_materials(active_year):
        counts[m["kind"]] = counts.get(m["kind"], 0) + 1
    counts["barcha"] = len(_all_materials(active_year))

    years = _years()
    prev_year = next((y for y in years if y < active_year), None)
    next_year = next((y for y in years if y > active_year), None)

    ctx = {
        "active": "yillar",
        "active_year": active_year,
        "archive": archive,
        "materials": materials[:PER_PAGE],
        "counts": counts,
        "years": years,
        "prev_year": prev_year,
        "next_year": next_year,
        "dates": ImportantDate.objects.filter(date__year=active_year)[:5],
        "search": search,
        "kind": kind,
        "sort": sort,
        "total": len(materials),
    }
    return render(request, "core/yillar.html", ctx)


def yil_detail(request, year):
    qs = YearArchive.objects.filter(year=year).first()
    if not qs:
        messages.info(request, "Bu yil uchun arxiv ma'lumoti topilmadi.")
        return redirect("core:yillar")
    request.GET = request.GET.copy()
    request.GET["yil"] = str(year)
    return yillar(request)


# ------------------------------------------------------------------ Binolar
def binolar(request):
    qs = Building.objects.all()
    year = request.GET.get("yil")
    years = list(Building.objects.values_list("year", flat=True).distinct().order_by("-year"))
    active_year = int(year) if year and str(year).isdigit() else None

    if active_year:
        qs = qs.filter(year=active_year)
    turi = request.GET.get("tur")
    if turi:
        qs = qs.filter(building_type=turi)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(address__icontains=q))

    ctx = {
        "active": "binolar",
        "page": _page(request, qs),
        "years": years,
        "active_year": active_year,
        "buildings_total": Building.objects.count(),
        "regions_count": Building.objects.values("region").distinct().count(),
        "capacity_total": sum(b.capacity for b in Building.objects.all()),
        "cost_total": sum(b.cost for b in Building.objects.all()),
        "regions": _regions_with_counts(Building),
        "latest": Building.objects.order_by("-handover_date")[:4],
        "types": Building.BUILDING_TYPES,
        "q": q,
        "turi": turi,
    }
    return render(request, "core/binolar.html", ctx)


def bino_detail(request, slug):
    bino = get_object_or_404(Building, slug=slug)
    bino.views += 1
    bino.save(update_fields=["views"])

    related = []
    if bino.department:
        related += list(bino.department.gallery.all()[:5])
    related += list(MediaItem.objects.filter(event__isnull=False)[:5])

    ctx = {
        "active": "binolar",
        "bino": bino,
        "highlights": Highlight.objects.filter(building=bino),
        "gallery": list(MediaItem.objects.filter(year=bino.year)[:8]) or list(MediaItem.objects.all()[:8]),
        "related": related[:5],
    }
    return render(request, "core/bino_detail.html", ctx)


# -------------------------------------------------------------- Bo'linmalar
def bolinmalar(request):
    qs = Department.objects.all()
    cat = request.GET.get("kategoriya")
    categories = Category.objects.all()
    active_cat = None
    if cat:
        active_cat = get_object_or_404(Category, slug=cat)
        qs = qs.filter(category=active_cat)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(summary__icontains=q))

    ctx = {
        "active": "bolinmalar",
        "page": _page(request, qs, 16),
        "categories": categories,
        "active_cat": active_cat,
        "total": Department.objects.count(),
        "hududiy": Department.objects.filter(category__slug__icontains="hududiy").count() or 12,
        "maxsus": 4,
        "talim_count": Category.objects.filter(name__icontains="Ta'lim").count() or 2,
        "qoshimcha": 5,
        "latest": _latest_news(5),
        "popular": Department.objects.order_by("-views")[:4],
        "regions": _regions_with_counts(Department),
        "q": q,
    }
    return render(request, "core/bolinmalar.html", ctx)


def bolinma_detail(request, slug):
    bolinma = get_object_or_404(Department, slug=slug)
    bolinma.views += 1
    bolinma.save(update_fields=["views"])
    ctx = {
        "active": "bolinmalar",
        "bolinma": bolinma,
        "highlights": Highlight.objects.filter(department=bolinma),
        "gallery": list(bolinma.gallery.all()[:8]) or list(MediaItem.objects.all()[:8]),
        "buildings": bolinma.buildings.all()[:4],
        "related": list(Event.objects.filter(department=bolinma)[:5])
        + list(Achievement.objects.filter(department=bolinma)[:5]),
    }
    return render(request, "core/bolinma_detail.html", ctx)


# ------------------------------------------------------------- G'alabalar
TYPE_LABELS = {
    "xalqaro": "Xalqaro",
    "respublika": "Respublika",
    "sport": "Sport",
    "kasbiy": "Kasbiy mahorat",
    "innovatsion": "Innovatsion loyiha",
    "mukofot": "Mukofot",
    "taktik": "Taktik o'quvlar",
    "boshqa": "Boshqa",
}


def galabalar(request):
    qs = Achievement.objects.filter(is_published=True)
    turlar = list(Achievement.ACHIEVEMENT_TYPES)
    turi = request.GET.get("tur")
    active_type = None
    if turi:
        qs = qs.filter(achievement_type=turi)
        active_type = TYPE_LABELS.get(turi, turi)

    year = request.GET.get("yil")
    years = sorted(
        Achievement.objects.values_list("year", flat=True).distinct(), reverse=True
    )
    active_year = int(year) if year and str(year).isdigit() else None
    if active_year:
        qs = qs.filter(year=active_year)

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(summary__icontains=q))

    distribution = []
    total = Achievement.objects.count() or 1
    for key, label in Achievement.ACHIEVEMENT_TYPES:
        c = Achievement.objects.filter(achievement_type=key).count()
        if c:
            distribution.append(
                {"label": label, "count": c, "percent": round(c * 100 / total), "key": key}
            )

    ctx = {
        "active": "galabalar",
        "page": _page(request, qs, 9),
        "types": turlar,
        "type_labels": TYPE_LABELS,
        "active_type": active_type,
        "turi": turi,
        "years": years,
        "active_year": active_year,
        "q": q,
        "total": Achievement.objects.count(),
        "xalqaro": Achievement.objects.filter(achievement_type="xalqaro").count(),
        "respublika": Achievement.objects.filter(achievement_type="respublika").count(),
        "jamoaviy": Event.objects.count(),
        "eng_muhim": Achievement.objects.filter(is_featured=True).count() or 28,
        "latest": Achievement.objects.order_by("-date")[:5],
        "distribution": distribution,
        "regions": _regions_with_counts(Achievement),
    }
    return render(request, "core/galabalar.html", ctx)


def galaba_detail(request, slug):
    obj = get_object_or_404(Achievement, slug=slug)
    obj.views += 1
    obj.save(update_fields=["views"])
    ctx = _detail_ctx(
        request, obj, active="galabalar",
        badge=TYPE_LABELS.get(obj.achievement_type, obj.achievement_type), badge_color="#b45309",
        breadcrumbs=[{"title": "Erishilgan g'alabalar", "url": "/galabalar/"}, {"title": obj.title}],
        meta=[
            {"icon": "calendar", "value": obj.date},
            {"icon": "pin", "value": obj.region or "O'zbekiston"},
            {"icon": "trophy", "value": obj.get_achievement_type_display},
        ],
        info=[
            {"icon": "calendar", "label": "Sana", "value": obj.date},
            {"icon": "pin", "label": "Hudud", "value": obj.region or "—"},
            {"icon": "trophy", "label": "Yutuq turi", "value": obj.get_achievement_type_display},
            {"icon": "users", "label": "Tegishli bo'linma", "value": obj.department or "—"},
            {"icon": "camera", "label": "Materiallar soni", "value": f"{obj.photo_count + obj.video_count + obj.doc_count} ta (foto {obj.photo_count}, video {obj.video_count}, hujjat {obj.doc_count})"},
        ],
        tags=[t.name for t in obj.tags.all()] + ([str(obj.year)] if obj.year else []),
        related=_related_materials(Achievement.objects.filter(achievement_type=obj.achievement_type).exclude(pk=obj.pk)[:5]),
        related_url="/galabalar/",
        bookmark="galaba",
        gallery=list(MediaItem.objects.all()[:8]),
    )
    return render(request, "core/material_detail.html", ctx)


def _related_materials(qs):
    return [
        {"title": o.title, "url": o.get_absolute_url(), "image": o.image, "date": o.date, "meta": ""}
        for o in qs
    ]


def _detail_ctx(request, obj, **kwargs):
    ctx = {"obj": obj, "active": kwargs.pop("active")}
    ctx.update(kwargs)
    return ctx


# ----------------------------------------------------------------- Tadbirlar
def tadbirlar(request):
    qs = Event.objects.filter(is_published=True)
    tur = request.GET.get("tur")
    if tur:
        qs = qs.filter(event_type=tur)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(location__icontains=q))
    year = request.GET.get("yil")
    years = sorted(Event.objects.values_list("year", flat=True).distinct(), reverse=True)
    active_year = int(year) if year and str(year).isdigit() else None
    if active_year:
        qs = qs.filter(year=active_year)
    return render(request, "core/list.html", {
        "active": "tadbirlar",
        "title": "Tadbirlar va marosimlar",
        "subtitle": "Milliy gvardiyaning tantanali marosimlari, musobaqalari, tashriflari, treninglari va boshqa tadbirlari arxivi.",
        "page": _page(request, qs),
        "types": Event.EVENT_TYPES,
        "tur": tur,
        "q": q,
        "years": years,
        "active_year": active_year,
        "type_key": "event_type",
        "card_color": "#0f766e",
        "empty_icon": "🎉",
        "stats": [
            {"value": Event.objects.count(), "label": "Jami tadbirlar", "icon": "👥", "color": "#0f766e"},
            {"value": Event.objects.filter(event_type="marosim").count(), "label": "Marosimlar", "icon": "🎗️", "color": "#1d4ed8"},
            {"value": Event.objects.filter(event_type="musobaqa").count(), "label": "Musobaqalar", "icon": "🏆", "color": "#eab308"},
            {"value": len(years), "label": "Arxiv yillari", "icon": "📅", "color": "#8b5cf6"},
        ],
        "panel_title": "Hududlar bo'yicha tadbirlar",
        "regions": _regions_with_counts(Event),
        "map": True,
        "mini_items": [
            {"title": e.title, "url": e.get_absolute_url(), "image": e.image, "meta": e.date}
            for e in Event.objects.order_by("-date")[:5]
        ],
        "mini_title": "So'nggi tadbirlar",
    })


def tadbir_detail(request, slug):
    obj = get_object_or_404(Event, slug=slug)
    obj.views += 1
    obj.save(update_fields=["views"])
    return render(request, "core/material_detail.html", _detail_ctx(
        request, obj, active="tadbirlar",
        badge=obj.get_event_type_display(), badge_color="#0f766e",
        breadcrumbs=[{"title": "Tadbirlar va marosimlar", "url": "/tadbirlar/"}, {"title": obj.title}],
        meta=[
            {"icon": "calendar", "value": obj.date},
            {"icon": "pin", "value": obj.location or obj.region or "—"},
            {"icon": "users", "value": obj.department or "Milliy gvardiya"},
        ],
        info=[
            {"icon": "calendar", "label": "Sana", "value": obj.date},
            {"icon": "pin", "label": "Joylashuv", "value": obj.location or "—"},
            {"icon": "users", "label": "Tadbir turi", "value": obj.get_event_type_display},
            {"icon": "shield", "label": "Tegishli bo'linma", "value": obj.department or "—"},
            {"icon": "camera", "label": "Materiallar soni", "value": f"{obj.photo_count + obj.video_count + obj.doc_count} ta"},
        ],
        tags=[t.name for t in obj.tags.all()] + [str(obj.year)],
        related=_related_materials(Event.objects.filter(event_type=obj.event_type).exclude(pk=obj.pk)[:5]),
        related_url="/tadbirlar/",
        bookmark="tadbir",
        gallery=list(obj.gallery.all()[:8]) or list(MediaItem.objects.all()[:8]),
    ))


# -------------------------------------------------------------------- Ta'lim
def talim(request):
    qs = Education.objects.filter(is_published=True)
    tur = request.GET.get("tur")
    if tur:
        qs = qs.filter(edu_type=tur)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(summary__icontains=q))
    year = request.GET.get("yil")
    years = sorted(Education.objects.values_list("year", flat=True).distinct(), reverse=True)
    active_year = int(year) if year and str(year).isdigit() else None
    if active_year:
        qs = qs.filter(year=active_year)
    return render(request, "core/list.html", {
        "active": "talim",
        "title": "Ta'lim va o'quv mashg'ulotlari",
        "subtitle": "Milliy gvardiya xodimlarining kasbiy mahorati, malaka oshirish kurslari, seminarlar va o'quv mashg'ulotlari arxivi.",
        "page": _page(request, qs),
        "types": Education.EDU_TYPES,
        "tur": tur,
        "q": q,
        "years": years,
        "active_year": active_year,
        "type_key": "edu_type",
        "card_color": "#7c3aed",
        "empty_icon": "🎓",
        "stats": [
            {"value": Education.objects.count(), "label": "Jami mashg'ulotlar", "icon": "🎓", "color": "#7c3aed"},
            {"value": sum(e.students_count for e in Education.objects.all()), "label": "Qatnashchilar", "icon": "👥", "color": "#1d4ed8"},
            {"value": Building.objects.filter(building_type="quv_markaz").count(), "label": "O'quv markazlari", "icon": "🏛️", "color": "#0f766e"},
            {"value": len(years), "label": "Arxiv yillari", "icon": "📅", "color": "#eab308"},
        ],
        "panel_title": "O'quv markazi",
        "regions": [],
        "mini_items": [
            {"title": b.title, "url": b.get_absolute_url(), "image": b.image, "meta": f"{b.year} · {b.region}"}
            for b in Building.objects.filter(building_type="quv_markaz")[:5]
        ],
        "mini_title": "O'quv inshootlari",
    })


def talim_detail(request, slug):
    obj = get_object_or_404(Education, slug=slug)
    obj.views += 1
    obj.save(update_fields=["views"])
    return render(request, "core/material_detail.html", _detail_ctx(
        request, obj, active="talim",
        badge=obj.get_edu_type_display(), badge_color="#7c3aed",
        breadcrumbs=[{"title": "Ta'lim va o'quv mashg'ulotlari", "url": "/talim/"}, {"title": obj.title}],
        meta=[
            {"icon": "calendar", "value": obj.date},
            {"icon": "cap", "value": obj.get_edu_type_display},
            {"icon": "users", "value": obj.students_count},
        ],
        info=[
            {"icon": "calendar", "label": "Sana", "value": obj.date},
            {"icon": "cap", "label": "Mashg'ulot turi", "value": obj.get_edu_type_display},
            {"icon": "clock", "label": "Davomiyligi", "value": obj.duration or "—"},
            {"icon": "users", "label": "Qatnashchilar soni", "value": obj.students_count},
            {"icon": "shield", "label": "Tegishli bo'linma", "value": obj.department or "—"},
        ],
        tags=[t.name for t in obj.tags.all()] + [str(obj.year)],
        related=_related_materials(Education.objects.exclude(pk=obj.pk)[:5]),
        related_url="/talim/",
        gallery=list(MediaItem.objects.all()[:8]),
    ))


# ------------------------------------------------------------------ Galereya
def galereya(request):
    qs = MediaItem.objects.all()
    turi = request.GET.get("tur")
    if turi in ("photo", "video"):
        qs = qs.filter(media_type=turi)
    year = request.GET.get("yil")
    years = sorted(MediaItem.objects.values_list("year", flat=True).distinct(), reverse=True)
    active_year = int(year) if year and str(year).isdigit() else None
    if active_year:
        qs = qs.filter(year=active_year)
    return render(request, "core/list.html", {
        "active": "galereya",
        "title": "Foto va videoarxiv",
        "subtitle": "Milliy gvardiyaning tadbirlari, mashg'ulotlari, yangi binolari va xizmat faoliyatidan olingan foto hamda video materiallar arxivi.",
        "page": _page(request, qs),
        "types": MediaItem.MEDIA_TYPES,
        "tur": turi,
        "years": years,
        "active_year": active_year,
        "type_key": "media_type",
        "card_color": "#0e7490",
        "grid_class": "grid--4",
        "empty_icon": "🖼️",
        "stats": [
            {"value": MediaItem.objects.filter(media_type="photo").count(), "label": "Foto materiallar", "icon": "📷", "color": "#0e7490"},
            {"value": MediaItem.objects.filter(media_type="video").count(), "label": "Video materiallar", "icon": "🎥", "color": "#1d4ed8"},
            {"value": len(years), "label": "Arxiv yillari", "icon": "📅", "color": "#eab308"},
            {"value": MediaItem.objects.count(), "label": "Jami materiallar", "icon": "🗂️", "color": "#7c3aed"},
        ],
        "mini_items": [
            {"title": m.title, "url": m.get_absolute_url(), "image": m.image, "meta": m.date}
            for m in MediaItem.objects.order_by("-date")[:5]
        ],
        "mini_title": "So'nggi materiallar",
    })


# ----------------------------------------------------------------- Hujjatlar
def hujjatlar(request):
    qs = Document.objects.filter(is_published=True)
    tur = request.GET.get("tur")
    if tur:
        qs = qs.filter(doc_type=tur)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(doc_number__icontains=q))
    year = request.GET.get("yil")
    years = sorted(Document.objects.values_list("year", flat=True).distinct(), reverse=True)
    active_year = int(year) if year and str(year).isdigit() else None
    if active_year:
        qs = qs.filter(year=active_year)
    return render(request, "core/list.html", {
        "active": "hujjatlar",
        "title": "Hujjatlar va relikiyalar",
        "subtitle": "Milliy gvardiyaning normativ-huquqiy hujjatlari, buyruqlari, farmoyishlari, tarixiy hujjatlari va relikiyalar arxivi.",
        "page": _page(request, qs),
        "types": Document.DOC_TYPES,
        "tur": tur,
        "q": q,
        "years": years,
        "active_year": active_year,
        "type_key": "doc_type",
        "card_color": "#6d28d9",
        "grid_class": "grid--4",
        "empty_icon": "📄",
        "stats": [
            {"value": Document.objects.count(), "label": "Jami hujjatlar", "icon": "📄", "color": "#6d28d9"},
            {"value": Document.objects.filter(doc_type="hujjat").count(), "label": "Rasmiy hujjatlar", "icon": "🏛️", "color": "#1d4ed8"},
            {"value": Document.objects.filter(doc_type="relikiya").count(), "label": "Relikiyalar", "icon": "🏺", "color": "#b45309"},
            {"value": len(years), "label": "Arxiv yillari", "icon": "📅", "color": "#0f766e"},
        ],
        "panel_title": "Hujjat turlari bo'yicha",
        "mini_items": [
            {"title": d.title, "url": d.get_absolute_url(), "image": d.image, "meta": f"{d.doc_number or d.date}"}
            for d in Document.objects.order_by("-date")[:5]
        ],
        "mini_title": "So'nggi hujjatlar",
    })


def hujjat_detail(request, slug):
    obj = get_object_or_404(Document, slug=slug)
    obj.views += 1
    obj.save(update_fields=["views"])
    return render(request, "core/material_detail.html", _detail_ctx(
        request, obj, active="hujjatlar",
        badge=obj.get_doc_type_display(), badge_color="#6d28d9",
        breadcrumbs=[{"title": "Hujjatlar va relikiyalar", "url": "/hujjatlar/"}, {"title": obj.title}],
        meta=[
            {"icon": "calendar", "value": obj.date},
            {"icon": "file", "value": obj.doc_number or obj.get_doc_type_display},
            {"icon": "users", "value": obj.department or "Milliy gvardiya"},
        ],
        info=[
            {"icon": "calendar", "label": "Sana", "value": obj.date},
            {"icon": "file", "label": "Hujjat turi", "value": obj.get_doc_type_display},
            {"icon": "file", "label": "Hujjat raqami", "value": obj.doc_number or "—"},
            {"icon": "camera", "label": "Sahifalar soni", "value": obj.pages or "—"},
            {"icon": "shield", "label": "Tegishli bo'linma", "value": obj.department or "—"},
        ],
        tags=[t.name for t in obj.tags.all()] + [str(obj.year)],
        related=_related_materials(Document.objects.exclude(pk=obj.pk)[:5]),
        related_url="/hujjatlar/",
        bookmark="hujjat",
        gallery=list(MediaItem.objects.all()[:6]),
    ))


# ------------------------------------------------------------------ Shaxslar
def shaxslar(request):
    qs = Person.objects.all()
    tur = request.GET.get("tur")
    if tur:
        qs = qs.filter(person_type=tur)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(full_name__icontains=q) | Q(position__icontains=q))
    return render(request, "core/list.html", {
        "active": "shaxslar",
        "title": "Rahbarlar va shaxslar",
        "subtitle": "Milliy gvardiya tizimidagi rahbarlar, xizmat fidoyilari, qahramonlar va tarixiy shaxslarning biografiyalar arxivi.",
        "page": _page(request, qs),
        "types": Person.PERSON_TYPES,
        "tur": tur,
        "q": q,
        "type_key": "person_type",
        "card_color": "#0f766e",
        "grid_class": "grid--4",
        "empty_icon": "👤",
        "stats": [
            {"value": Person.objects.count(), "label": "Jami shaxslar", "icon": "👤", "color": "#0f766e"},
            {"value": Person.objects.filter(person_type="rahbar").count(), "label": "Rahbarlar", "icon": "⭐", "color": "#1d4ed8"},
            {"value": Person.objects.filter(person_type="qahramon").count(), "label": "Qahramonlar", "icon": "🏅", "color": "#eab308"},
            {"value": Person.objects.filter(person_type="tarixiy").count(), "label": "Tarixiy shaxslar", "icon": "📜", "color": "#7c3aed"},
        ],
        "panel_title": "Turlar bo'yicha",
        "mini_items": [
            {"title": p.full_name, "url": p.get_absolute_url(), "image": p.photo, "meta": p.position}
            for p in Person.objects.order_by("order")[:6]
        ],
        "mini_title": "Mashhur shaxslar",
    })


def shaxs_detail(request, slug):
    obj = get_object_or_404(Person, slug=slug)
    obj.views += 1
    obj.save(update_fields=["views"])
    return render(request, "core/material_detail.html", _detail_ctx(
        request, obj, active="shaxslar",
        badge=obj.get_person_type_display(), badge_color="#0f766e",
        breadcrumbs=[{"title": "Rahbarlar va shaxslar", "url": "/shaxslar/"}, {"title": obj.full_name}],
        meta=[
            {"icon": "user", "value": obj.full_name},
            {"icon": "calendar", "value": obj.service_period or obj.birth_date},
            {"icon": "building", "value": obj.position or "—"},
        ],
        info=[
            {"icon": "user", "label": "F.I.Sh.", "value": obj.full_name},
            {"icon": "building", "label": "Lavozim", "value": obj.position or "—"},
            {"icon": "calendar", "label": "Tug'ilgan sana", "value": obj.birth_date or "—"},
            {"icon": "clock", "label": "Xizmat davri", "value": obj.service_period or "—"},
            {"icon": "shield", "label": "Bo'linma", "value": obj.department or "—"},
            {"icon": "star", "label": "Mukofotlar", "value": obj.awards or "—"},
        ],
        tags=[obj.get_person_type_display()] + ([str(obj.department)] if obj.department else []),
        related=[
            {"title": p.full_name, "url": p.get_absolute_url(), "image": p.photo, "date": p.service_period, "meta": p.position}
            for p in Person.objects.exclude(pk=obj.pk)[:5]
        ],
        related_url="/shaxslar/",
        bookmark="shaxs",
    ))


# ------------------------------------------------------------ Muhim sanalar
def sanalar(request):
    qs = ImportantDate.objects.all()
    year = request.GET.get("yil")
    years = sorted({d.year for d in ImportantDate.objects.values_list("date", flat=True) if d}, reverse=True)
    active_year = int(year) if year and str(year).isdigit() else None
    if active_year:
        qs = qs.filter(date__year=active_year)
    return render(request, "core/list.html", {
        "active": "sanalar",
        "title": "Muhim sanalar",
        "subtitle": "Milliy gvardiya tarixidagi muhim voqealar, tashkil etilgan kunlar, tantanalar va esda qolishi kerak bo'lgan sanalar.",
        "page": _page(request, qs),
        "years": years,
        "active_year": active_year,
        "card_color": "#b45309",
        "grid_class": "grid--3",
        "type_key": "",
        "card_text": "Muhim sana",
        "empty_icon": "📅",
        "stats": [
            {"value": ImportantDate.objects.count(), "label": "Jami muhim sanalar", "icon": "📅", "color": "#b45309"},
            {"value": len(years), "label": "Arxiv yillari", "icon": "🗂️", "color": "#1d4ed8"},
            {"value": YearArchive.objects.count(), "label": "Yillar arxivi", "icon": "🏛️", "color": "#0f766e"},
            {"value": Event.objects.count(), "label": "Tadbirlar", "icon": "👥", "color": "#7c3aed"},
        ],
        "panel_title": "Yillar bo'yicha tarix",
        "mini_items": [
            {"title": y.title, "url": y.get_absolute_url(), "image": y.image, "meta": f"{y.year}-yil arxivi"}
            for y in YearArchive.objects.all()[:6]
        ],
        "mini_title": "Yillar arxivi",
    })


def sana_detail(request, slug):
    obj = get_object_or_404(ImportantDate, slug=slug)
    return render(request, "core/material_detail.html", _detail_ctx(
        request, obj, active="sanalar",
        badge="Muhim sana", badge_color="#b45309",
        breadcrumbs=[{"title": "Muhim sanalar", "url": "/sanalar/"}, {"title": obj.title}],
        meta=[
            {"icon": "calendar", "value": obj.date},
            {"icon": "star", "value": "Muhim sana"},
        ],
        info=[
            {"icon": "calendar", "label": "Sana", "value": obj.date},
            {"icon": "star", "label": "Turi", "value": "Muhim sana"},
            {"icon": "file", "label": "Tegishli tadbir", "value": obj.event or "—"},
        ],
        tags=[str(obj.date.year)],
        related=[
            {"title": d.title, "url": d.get_absolute_url(), "image": d.image, "date": d.date, "meta": ""}
            for d in ImportantDate.objects.exclude(pk=obj.pk)[:5]
        ],
        related_url="/sanalar/",
    ))


def media_detail(request, slug):
    obj = get_object_or_404(MediaItem, slug=slug)
    obj.views += 1
    obj.save(update_fields=["views"])
    return render(request, "core/material_detail.html", _detail_ctx(
        request, obj, active="galereya",
        badge=obj.get_media_type_display(), badge_color="#0e7490",
        breadcrumbs=[{"title": "Foto va videoarxiv", "url": "/galereya/"}, {"title": obj.title}],
        meta=[
            {"icon": "calendar", "value": obj.date},
            {"icon": "camera" if obj.media_type == "photo" else "video", "value": obj.get_media_type_display},
            {"icon": "eye", "value": obj.views},
        ],
        info=[
            {"icon": "calendar", "label": "Sana", "value": obj.date},
            {"icon": "camera", "label": "Turi", "value": obj.get_media_type_display},
            {"icon": "shield", "label": "Bo'linma", "value": obj.department or "—"},
            {"icon": "users", "label": "Tadbir", "value": obj.event or "—"},
            {"icon": "eye", "label": "Ko'rishlar", "value": obj.views},
        ],
        tags=[str(obj.year), obj.get_media_type_display()],
        related=[
            {"title": m.title, "url": m.get_absolute_url(), "image": m.image, "date": m.date, "meta": ""}
            for m in MediaItem.objects.exclude(pk=obj.pk)[:5]
        ],
        related_url="/galereya/",
    ))


# ------------------------------------------------------------- Yo'nalishlar
def yonalishlar(request):
    ctx = {"active": "yonalishlar", "directions": Direction.objects.all()}
    return render(request, "core/yonalishlar.html", ctx)


# ------------------------------------------------------------------ Qidiruv
def qidiruv(request):
    q = request.GET.get("q", "").strip()
    results = []
    if q:
        n = q.lower()
        for o in Building.objects.filter(Q(title__icontains=q) | Q(address__icontains=q))[:10]:
            results.append({"kind": "Yangi bino", "title": o.title, "date": o.handover_date, "url": o.get_absolute_url(), "image": o.image, "meta": o.address})
        for o in Department.objects.filter(Q(title__icontains=q) | Q(summary__icontains=q))[:10]:
            results.append({"kind": "Bo'linma", "title": o.title, "date": None, "url": o.get_absolute_url(), "image": o.image, "meta": o.year_range})
        for o in Achievement.objects.filter(is_published=True).filter(Q(title__icontains=q) | Q(summary__icontains=q))[:10]:
            results.append({"kind": "G'alaba", "title": o.title, "date": o.date, "url": o.get_absolute_url(), "image": o.image, "meta": TYPE_LABELS.get(o.achievement_type, "")})
        for o in Event.objects.filter(is_published=True).filter(Q(title__icontains=q) | Q(location__icontains=q))[:10]:
            results.append({"kind": "Tadbir", "title": o.title, "date": o.date, "url": o.get_absolute_url(), "image": o.image, "meta": o.location})
        for o in Document.objects.filter(is_published=True).filter(Q(title__icontains=q) | Q(doc_number__icontains=q))[:10]:
            results.append({"kind": "Hujjat", "title": o.title, "date": o.date, "url": o.get_absolute_url(), "image": o.image, "meta": o.doc_number})
        for o in Person.objects.filter(Q(full_name__icontains=q) | Q(position__icontains=q))[:10]:
            results.append({"kind": "Shaxs", "title": o.full_name, "date": o.birth_date, "url": o.get_absolute_url(), "image": o.photo, "meta": o.position})
        for o in ImportantDate.objects.filter(Q(title__icontains=q) | Q(description__icontains=q))[:10]:
            results.append({"kind": "Muhim sana", "title": o.title, "date": o.date, "url": o.get_absolute_url(), "image": o.image, "meta": ""})
        if q.isdigit():
            for y in YearArchive.objects.filter(year=int(q)):
                results.append({"kind": "Yil", "title": y.title, "date": None, "url": y.get_absolute_url(), "image": y.image, "meta": str(y.year)})
        del n
    ctx = {"active": "qidiruv", "q": q, "results": results, "count": len(results)}
    return render(request, "core/qidiruv.html", ctx)


# --------------------------------------------------------------- Saqlanganlar
def saqlanganlar(request):
    key = request.session.session_key
    saved = Bookmark.objects.filter(session_key=key)
    registry = {
        "bino": (Building, "Yangi bino"),
        "bolinma": (Department, "Bo'linma"),
        "galaba": (Achievement, "G'alaba"),
        "tadbir": (Event, "Tadbir"),
        "hujjat": (Document, "Hujjat"),
        "talim": (Education, "Ta'lim"),
        "shaxs": (Person, "Shaxs"),
        "media": (MediaItem, "Media"),
    }
    items = []
    for s in saved:
        entry = registry.get(s.content_type)
        if not entry:
            continue
        model, kind = entry
        obj = model.objects.filter(pk=s.object_id).first()
        if not obj:
            s.delete()
            continue
        items.append({
            "kind": kind,
            "ctype": s.content_type,
            "obj": obj,
            "url": obj.get_absolute_url(),
            "image": getattr(obj, "image", None) or getattr(obj, "photo", None),
            "title": getattr(obj, "title", None) or getattr(obj, "full_name", str(obj)),
            "bookmark_id": s.pk,
        })
    return render(request, "core/saqlanganlar.html", {
        "active": "saqlanganlar",
        "title": "Saqlanganlar",
        "subtitle": "Siz saqlagan materiallar ro'yxati. Saqlash tugmasi orqali materiallarni shu yerda to'plashingiz mumkin.",
        "items": items,
        "total": len(items),
    })


@require_POST
def bookmark_toggle(request):
    key = request.session.session_key
    if not key:
        request.session.create()
        key = request.session.session_key
    ctype = request.POST.get("ctype")
    oid = request.POST.get("oid")
    url = request.POST.get("next") or "/"
    if not oid or not ctype:
        return redirect(url)
    obj = Bookmark.objects.filter(session_key=key, content_type=ctype, object_id=oid).first()
    if obj:
        obj.delete()
        messages.success(request, "Saqlanganlardan olib tashlandi.")
    else:
        Bookmark.objects.create(session_key=key, content_type=ctype, object_id=oid)
        messages.success(request, "Saqlanganlarga qo'shildi.")
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"saved": not obj})
    return redirect(url)
