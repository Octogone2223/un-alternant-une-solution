# Generated by Django 4.0.3 on 2022-03-24 12:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0002_company_jobs_company_users"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="user",
            field=models.OneToOneField(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
    ]
