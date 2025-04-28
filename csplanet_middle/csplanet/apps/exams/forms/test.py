from django import forms
from ..models import UserAnswer

class AnswerForm(forms.ModelForm):
    class Meta:
        model  = UserAnswer
        fields = ['selected_choice', 'text_answer']