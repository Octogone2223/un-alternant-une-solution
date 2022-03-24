# Generated by Django 4.0.3 on 2022-03-24 12:26

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '__first__'),
        ('authentication', '0003_student_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='courses',
            field=models.ManyToManyField(related_name='school_courses+', to='course.course'),
        ),
        migrations.AddField(
            model_name='school',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
