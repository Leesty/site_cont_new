# Сброс всех дополнительных лимитов (окошко выдачи лимитов убрано)

from django.db import migrations


def reset_extra_limits(apps, schema_editor):
    UserBaseLimit = apps.get_model("core", "UserBaseLimit")
    UserBaseLimit.objects.all().update(extra_daily_limit=0)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_contactrequest"),
    ]

    operations = [
        migrations.RunPython(reset_extra_limits, noop),
    ]
