# Generated by Django 3.2.16 on 2022-12-10 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0005_auto_20221210_1745'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='course_slug',
            field=models.SlugField(default='0', max_length=255, unique=True),
        ),
    ]
