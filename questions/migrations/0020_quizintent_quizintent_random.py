# Generated by Django 3.2.16 on 2023-01-10 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0019_question_question_explanation'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizintent',
            name='quizintent_random',
            field=models.BooleanField(null=True),
        ),
    ]
