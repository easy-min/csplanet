from django import forms
from ..models import Exam

class ExamForm(forms.ModelForm):
    class Meta:
        model  = Exam
        fields = [
            'title',
            'start_datetime',
            'end_datetime',
            'total_questions',
            'chapters',
            'objective_ratio',
        ]
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_datetime'  : forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'total_questions': forms.NumberInput(attrs={'min': 1}),
            'chapters'      : forms.CheckboxSelectMultiple(),
        }