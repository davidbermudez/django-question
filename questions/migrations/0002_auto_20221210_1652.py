# Generated by Django 3.2.16 on 2022-12-10 16:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_name', models.CharField(max_length=256)),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='question_course',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='questions.course'),
        ),
    ]
