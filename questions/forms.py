from django import forms
from django.forms import ModelForm
from .models import Question

class CsvUploadForm(forms.Form):
    csvFile = forms.FileField()


class OneQuestionForm(ModelForm):
    referer = forms.CharField()
    class Meta:
        model = Question
        fields = [
            'question_text',
            'question_response1',
            'question_response2',
            'question_response3',
            'question_response4',
            'question_explanation'
        ]

    def __init__(self, *args, **kwargs):
        super(OneQuestionForm, self).__init__(*args, **kwargs)
        self.fields['question_explanation'].required = False


class QuizForm(forms.Form):
    quiz_option1 = forms.ChoiceField()
    quiz_option2 = forms.ChoiceField()
    quiz_option3 = forms.ChoiceField()
    quiz_option4 = forms.ChoiceField()


class QuizInit(forms.Form):
    select_theme = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)