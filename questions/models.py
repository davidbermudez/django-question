from django.db import models

# Create your models here.
class Question(models.Model):
    question_theme = models.CharField(max_length=256)
    question_chapter = models.CharField(max_length=256)
    question_text = models.TextField()
    question_response1 = models.TextField()
    question_response2 = models.TextField()
    question_response3 = models.TextField()
    question_response4 = models.TextField()
    question_valid = models.IntegerField()
