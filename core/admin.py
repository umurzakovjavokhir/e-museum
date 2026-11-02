from django.contrib import admin

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
    Tag,
    YearArchive,
)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_other")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "color", "order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("title", "year_range", "region", "category", "views", "order")
    list_filter = ("region", "category", "is_featured")
    search_fields = ("title", "summary")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("order",)


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ("title", "year", "building_type", "region", "capacity", "cost", "is_active")
    list_filter = ("year", "building_type", "region", "is_active")
    search_fields = ("title", "address")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("is_active",)


@admin.register(YearArchive)
class YearArchiveAdmin(admin.ModelAdmin):
    list_display = ("year", "title", "new_buildings", "new_departments", "achievements", "documents")
    list_editable = ("new_buildings", "new_departments", "achievements", "documents")


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("title", "achievement_type", "date", "region", "views", "is_published")
    list_filter = ("achievement_type", "year", "region", "is_published", "is_featured")
    search_fields = ("title", "summary")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_type", "date", "location", "is_published")
    list_filter = ("event_type", "year", "region")
    search_fields = ("title", "location")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("title", "edu_type", "date", "students_count", "is_published")
    list_filter = ("edu_type", "year")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "doc_type", "doc_number", "date", "pages", "is_published")
    list_filter = ("doc_type", "year")
    search_fields = ("title", "doc_number")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("full_name", "position", "person_type", "service_period", "order")
    list_filter = ("person_type",)
    search_fields = ("full_name", "position")
    prepopulated_fields = {"slug": ("full_name",)}
    list_editable = ("order",)


@admin.register(ImportantDate)
class ImportantDateAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "is_featured")
    list_filter = ("is_featured",)
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}


@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ("title", "media_type", "date", "year", "views")
    list_filter = ("media_type", "year")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "icon", "url")
    list_editable = ("title", "icon", "url")


@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ("title", "building", "department", "order")
    list_filter = ("building", "department")
    list_editable = ("order",)


@admin.register(StatCard)
class StatCardAdmin(admin.ModelAdmin):
    list_display = ("value", "label", "icon", "color", "order")
    prepopulated_fields = {"slug": ("label",)}
    list_editable = ("order",)


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("session_key", "content_type", "object_id", "created_at")
