# Generated by Django 3.2.16 on 2022-12-17 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0010_auto_20221217_1755'),
    ]

    operations = [
        migrations.RenameField(
            model_name='quizintent',
            old_name='quizintent_intent',
            new_name='quizintent_questions',
        ),
        migrations.AddField(
            model_name='quizintent',
            name='quizintent_responses',
            field=models.JSONField(null=True),
        ),
    ]