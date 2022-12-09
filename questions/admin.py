from django.contrib import admin
from .models import Question

class QuestionAdmin(admin.ModelAdmin):
    fields = ['question_theme',
        'question_chapter',
        'question_text',
        'question_response1',
        'question_response2',
        'question_response3',
        'question_response4',
        'question_valid'
        ]

admin.site.register(Question, QuestionAdmin)