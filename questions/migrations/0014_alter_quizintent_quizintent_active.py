# Generated by Django 3.2.16 on 2022-12-17 23:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0013_alter_quizintent_quizintent_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizintent',
            name='quizintent_active',
            field=models.CharField(max_length=4, null=True),
        ),
    ]
