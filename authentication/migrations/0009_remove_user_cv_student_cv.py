# Generated by Django 4.0.3 on 2022-03-31 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0008_company_logo_school_logo_user_cv_user_logo"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="cv",
        ),
        migrations.AddField(
            model_name="student",
            name="cv",
            field=models.FileField(blank=True, null=True, upload_to="cv"),
        ),
    ]
