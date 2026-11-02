from django.conf import settings

from core.models import Bookmark, Department, Direction


def site_globals(request):
    menu = [{"name": "Bosh sahifa", "url": "core:home", "icon": "home"}]
    for direction in Direction.objects.all().order_by("number"):
        menu.append(
            {
                "name": direction.title,
                "url": direction.url or "core:yonalishlar",
                "icon": direction.icon or "star",
            }
        )
    if not request.session.session_key:
        request.session.create()

    bookmark_count = Bookmark.objects.filter(
        session_key=request.session.session_key
    ).count()

    return {
        "MENU": menu,
        "DIRECTIONS": Direction.objects.all()[:10],
        "DEPARTMENT_LIST": Department.objects.all()[:20],
        "BOOKMARK_COUNT": bookmark_count,
        "SITE_TITLE": "Milliy gvardiya elektron muzeyi",
        "MEDIA_URL": settings.MEDIA_URL,
    }
