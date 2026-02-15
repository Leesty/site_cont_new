from django.db import migrations, models


def create_initial_base_and_lead_types(apps, schema_editor):
    BaseType = apps.get_model("core", "BaseType")
    LeadType = apps.get_model("core", "LeadType")

    base_definitions = [
        ("telegram", "Telegram", 50, 1),
        ("whatsapp", "WhatsApp", 35, 2),
        ("max", "Max", 35, 3),
        ("viber", "Viber", 35, 4),
        ("instagram", "Нельзяграм (там где Reels)", 300, 5),
        ("vk", "ВКонтакте", 250, 6),
        ("ok", "Одноклассники", 250, 7),
        ("email", "Почта", 100, 8),
    ]

    for slug, name, limit, order in base_definitions:
        BaseType.objects.update_or_create(
            slug=slug,
            defaults={
                "name": name,
                "default_daily_limit": limit,
                "order": order,
            },
        )

    lead_definitions = [
        ("telegram", "Telegram", 1),
        ("whatsapp", "WhatsApp", 2),
        ("max", "Max", 3),
        ("viber", "Viber", 4),
        ("instagram", "Нельзяграм", 5),
        ("vk", "ВКонтакте", 6),
        ("ok", "Одноклассники", 7),
        ("email", "Почта", 8),
        ("avito", "Авито", 9),
        ("yula", "Юла", 10),
        ("kwork", "Кворк", 11),
        ("other_social", "Прочие соц. сети", 12),
        ("self", "Самостоятельные лиды", 13),
    ]

    for slug, name, order in lead_definitions:
        LeadType.objects.update_or_create(
            slug=slug,
            defaults={
                "name": name,
                "order": order,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="lead",
            name="raw_contact",
            field=models.CharField(
                blank=True,
                max_length=255,
                help_text="Текстовое значение контакта (если нет связи с моделью Contact).",
            ),
        ),
        migrations.RunPython(create_initial_base_and_lead_types, migrations.RunPython.noop),
    ]

