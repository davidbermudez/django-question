from django.contrib import admin
from .models import Question, Course, Type, Registration, QuizIntent


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
    
    list_display = ['question_course',
        'question_theme',
        'question_chapter',
        'question_text'
    ]


class CourseAdmin(admin.ModelAdmin):
    fields = ['course_name', 'course_type', 'course_slug']


class TypeAdmin(admin.ModelAdmin):
    fields = ['type_name',]


class RegistrationAdmin(admin.ModelAdmin):
    readonly_fields = ['registration_date']
    
    fields = ['registration_user',
        'registration_course',
        'registration_date',
        'registration_date_end']

    list_display = ['registration_user',
            'registration_course',
            'registration_date',
            'registration_date_end']


class QuizIntentAdmin(admin.ModelAdmin):
    fields = ['quizintent_user',
        'quizintent_questions',
        'quizintent_responses',
        'quizintent_active'
    ]

    list_display = ['quizintent_user',
        'quizintent_questions',
    ]

admin.site.register(QuizIntent, QuizIntentAdmin)


admin.site.register(Question, QuestionAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(Registration, RegistrationAdmin)