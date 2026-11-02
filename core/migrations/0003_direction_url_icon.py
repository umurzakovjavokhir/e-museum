from django.db import migrations, models

DIRECTION_LINKS = {
    1: ("core:yillar", "calendar"),
    2: ("core:shaxslar", "user"),
    3: ("core:hujjatlar", "file"),
    4: ("core:tadbirlar", "users"),
    5: ("core:bolinmalar", "shield"),
    6: ("core:binolar", "building"),
    7: ("core:talim", "cap"),
    8: ("core:galereya", "image"),
    9: ("core:galabalar", "trophy"),
    10: ("core:sanalar", "star"),
}


def fill_links(apps, schema_editor):
    Direction = apps.get_model("core", "Direction")
    for direction in Direction.objects.all():
        url, icon = DIRECTION_LINKS.get(direction.number, ("core:yonalishlar", "star"))
        direction.url = url
        direction.icon = icon
        direction.save(update_fields=["url", "icon"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_alter_achievement_options_alter_document_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="direction",
            name="url",
            field=models.CharField(
                blank=True, default="core:yonalishlar", max_length=100,
                verbose_name="Havola (URL nomi)",
            ),
        ),
        migrations.AlterField(
            model_name="direction",
            name="icon",
            field=models.CharField(default="star", max_length=40, verbose_name="Belgi (svg nomi)"),
        ),
        migrations.RunPython(fill_links, migrations.RunPython.noop),
    ]
