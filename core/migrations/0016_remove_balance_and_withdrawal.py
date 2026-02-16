# Generated migration: remove user balance and WithdrawalRequest model

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0015_lead_date"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="balance",
        ),
        migrations.DeleteModel(
            name="WithdrawalRequest",
        ),
    ]
