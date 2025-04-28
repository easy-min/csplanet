# apps/problems/forms/forms.py
from django import forms
from django.forms import HiddenInput
from django.forms.models import inlineformset_factory

from ..models.objective_problem   import ObjectiveProblem, ObjectiveChoice
from ..models.subjective_problem  import (
    SubjectiveProblem,
    QuestionKeywordMapping,
    SubjectiveKeyword,
)

# ──────────────────────────────────────────
# 1. 객관식 문제/선택지
# ──────────────────────────────────────────
class ObjectiveQuestionForm(forms.ModelForm):
    """객관식 문제 생성/수정 폼"""
    # score를 필수가 아니게 덮어쓰기
    score = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class':'form-control'})
    )
    class Meta:
        model   = ObjectiveProblem
        exclude = ['creator', 'created_at', 'q_type', 'question_type', 'topic']
        widgets = {
            'chapter'    : forms.Select(attrs={'class': 'form-select'}),
            'content'    : forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'explanation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'score'      : forms.NumberInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'content'    : '문항을 입력하세요 (객관식).',
            'explanation': '문항에 대한 해설을 입력하세요.',
        }

ObjectiveChoiceFormSet = inlineformset_factory(
    ObjectiveProblem,
    ObjectiveChoice,
    fields       = ['content', 'is_correct'],
    extra        = 2,   
    max_num      = 7,
    min_num      = 2,
    validate_min = True,
    validate_max = True,
    can_delete   = True,
    widgets      = {
        'content'   : forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '보기 내용을 입력하세요'}
        ),
        'is_correct': HiddenInput(),
        'DELETE'    : HiddenInput(),
    }
)

# ──────────────────────────────────────────
# 2. 주관식 문제/키워드
# ──────────────────────────────────────────
class SubjectiveQuestionForm(forms.ModelForm):
    """주관식 문제 생성/수정 폼"""
    class Meta:
        model   = SubjectiveProblem
        exclude = ['creator', 'created_at', 'q_type', 'question_type', 'subjective_keywords']
        widgets = {
            'chapter':    forms.Select(attrs={'class': 'form-select'}),
            'content':    forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'explanation':forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'score':      forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
        help_texts = {
            'content': '문항을 입력하세요 (주관식).',
        }

    def clean(self):
        cleaned = super().clean()
        if len(cleaned.get('content', '')) < 10:
            self.add_error('content', '문항은 최소 10자 이상이어야 합니다.')
        return cleaned

class QuestionKeywordMappingForm(forms.ModelForm):
    keyword = forms.CharField(
        max_length=100,
        label='키워드',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '키워드를 입력하세요'}),
    )
    class Meta:
        model  = QuestionKeywordMapping
        fields = ['keyword', 'importance']   # DELETE 필드는 inline formset이 자동 처리
        widgets = {
            'importance': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
        }
    def clean_keyword(self):
        text = self.cleaned_data['keyword'].strip()
        # 없으면 새로 만들고, 있으면 가져옴
        kw_obj, _ = SubjectiveKeyword.objects.get_or_create(word=text)
        return kw_obj

QuestionKeywordFormSet = inlineformset_factory(
    SubjectiveProblem,
    QuestionKeywordMapping,
    form         = QuestionKeywordMappingForm,
    extra        = 1,
    max_num      = 7,
    min_num      = 1,
    validate_min = True,
    validate_max = True,
    can_delete   = True,
)