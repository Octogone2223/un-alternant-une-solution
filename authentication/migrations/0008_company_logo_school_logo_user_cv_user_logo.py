# Generated by Django 4.0.3 on 2022-03-31 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_student_course'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='logos_company'),
        ),
        migrations.AddField(
            model_name='school',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='logos_school'),
        ),
        migrations.AddField(
            model_name='user',
            name='cv',
            field=models.FileField(blank=True, null=True, upload_to='cv'),
        ),
        migrations.AddField(
            model_name='user',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='logos'),
        ),
    ]
