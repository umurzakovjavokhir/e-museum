from django.urls import path

from core import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("landing/", views.landing, name="landing"),

    path("yillar/", views.yillar, name="yillar"),
    path("yillar/<int:year>/", views.yil_detail, name="yil_detail"),

    path("binolar/", views.binolar, name="binolar"),
    path("binolar/<slug:slug>/", views.bino_detail, name="bino_detail"),

    path("bolinmalar/", views.bolinmalar, name="bolinmalar"),
    path("bolinmalar/<slug:slug>/", views.bolinma_detail, name="bolinma_detail"),

    path("galabalar/", views.galabalar, name="galabalar"),
    path("galabalar/<slug:slug>/", views.galaba_detail, name="galaba_detail"),

    path("tadbirlar/", views.tadbirlar, name="tadbirlar"),
    path("tadbirlar/<slug:slug>/", views.tadbir_detail, name="tadbir_detail"),

    path("talim/", views.talim, name="talim"),
    path("talim/<slug:slug>/", views.talim_detail, name="talim_detail"),

    path("galereya/", views.galereya, name="galereya"),
    path("galereya/<slug:slug>/", views.media_detail, name="media_detail"),

    path("hujjatlar/", views.hujjatlar, name="hujjatlar"),
    path("hujjatlar/<slug:slug>/", views.hujjat_detail, name="hujjat_detail"),

    path("shaxslar/", views.shaxslar, name="shaxslar"),
    path("shaxslar/<slug:slug>/", views.shaxs_detail, name="shaxs_detail"),

    path("sanalar/", views.sanalar, name="sanalar"),
    path("sanalar/<slug:slug>/", views.sana_detail, name="sana_detail"),

    path("qidiruv/", views.qidiruv, name="qidiruv"),
    path("yonalishlar/", views.yonalishlar, name="yonalishlar"),

    path("saqlanganlar/", views.saqlanganlar, name="saqlanganlar"),
    path("saqlash/", views.bookmark_toggle, name="bookmark_toggle"),
]
