from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Course(models.Model):    
    course_name = models.CharField(max_length=256, )
    course_type = models.ForeignKey(
        'Type',
        on_delete=models.CASCADE,
        null = True,        
    )
    course_slug = models.SlugField(
        max_length=255,
        unique=True,
        default='0'
    )

    def __str__(self):
        return self.course_name


class Registration(models.Model):
    registration_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
    )
    registration_course=models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        null=True,
    )
    registration_date = models.DateTimeField(auto_now_add=True, editable=False)
    registration_date_end = models.DateTimeField(null=True)


class Question(models.Model):
    question_theme = models.CharField(max_length=256)
    question_chapter = models.CharField(max_length=256)
    question_text = models.TextField()
    question_response1 = models.TextField()
    question_response2 = models.TextField()
    question_response3 = models.TextField()
    question_response4 = models.TextField()
    question_valid = models.IntegerField()
    question_course = models.ForeignKey(
        'Course', 
        on_delete=models.CASCADE,
        null=True)
    question_explanation = models.TextField(null=True)

    def __str__(self):
        return self.question_text


class Type(models.Model):
    type_name = models.CharField(max_length=25)

    def __str__(self):
        return self.type_name


class QuizIntent(models.Model):
    quizintent_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
    )
    quizintent_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        null=True,
    )
    quizintent_questions = models.JSONField(null=True)
    quizintent_responses = models.JSONField(null=True)
    quizintent_active = models.CharField(max_length=4, null=True)
    quizintent_dateInit = models.DateTimeField(auto_now_add=True, editable=False)


class QuizFinalized(models.Model):
    quizfinalized_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
    )
    quizfinalized_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        null=True,
    )
    quizfinalized_questions = models.JSONField(null=True)
    quizfinalized_responses = models.JSONField(null=True)
    quizfinalized_success = models.JSONField(null=True)
    quizfinalized_result = models.IntegerField(null=True)
    quizfinalized_dateInit = models.DateTimeField(null=True, editable=False)
    quizfinalized_dateEnd = models.DateTimeField(auto_now_add=True, editable=False)