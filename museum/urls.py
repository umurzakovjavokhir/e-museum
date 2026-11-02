from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Milliy gvardiya elektron muzeyi boshqaruvi"
admin.site.site_title = "MG Elektron muzey"
admin.site.index_title = "Boshqaruv paneli"
