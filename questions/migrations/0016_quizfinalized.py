# Generated by Django 3.2.16 on 2022-12-19 18:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('questions', '0015_quizintent_quizintent_course'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuizFinalized',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quizfinalized_questions', models.JSONField(null=True)),
                ('quizfinalized_responses', models.JSONField(null=True)),
                ('quizfinalized_success', models.JSONField(null=True)),
                ('quizfinalized_result', models.IntegerField(null=True)),
                ('quizfinalized_course', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='questions.course')),
                ('quizfinalized_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
