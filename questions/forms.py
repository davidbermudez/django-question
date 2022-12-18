from django import forms
from django.forms import ModelForm
from .models import Question

class CsvUploadForm(forms.Form):
    csvFile = forms.FileField()


class OneQuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = [
            'question_theme',
            'question_chapter',
            'question_text',
            'question_response1',
            'question_response2',
            'question_response3',
            'question_response4'
        ]

class QuizForm(forms.Form):
    quiz_option1 = forms.ChoiceField()
    quiz_option2 = forms.ChoiceField()
    quiz_option3 = forms.ChoiceField()
    quiz_option4 = forms.ChoiceField()