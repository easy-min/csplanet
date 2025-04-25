# csplanet/apps/problems/views/create_subjective.py
from django.shortcuts             import render, redirect
from django.views.decorators.http import require_http_methods
from django.db                    import transaction

from ..forms.forms                import SubjectiveQuestionForm, QuestionKeywordFormSet
from ..models.subjective_problem  import SubjectiveProblem
from ..models.topic               import Topic
from ..models.chapter             import Chapter

@require_http_methods(["GET", "POST"])
@transaction.atomic
def create_subjective(request):
    if request.method == 'POST':
        form    = SubjectiveQuestionForm(request.POST)
        formset = QuestionKeywordFormSet(request.POST, prefix='kw')

        if form.is_valid() and formset.is_valid():
            # 1) 문제 저장
            problem = form.save(commit=False)
            problem.creator = request.user
            problem.q_type  = 'subjective'
            problem.save()

            # 2) 키워드 formset 저장 (clean_keyword()에서 이미 인스턴스로 변환됨)
            formset.instance = problem
            formset.save()

            return redirect('home')

        # 유효성 오류 로그 (디버깅용)
        print("---- Form errors ----", form.errors)
        print("---- Formset errors ----", formset.errors)

    else:
        form    = SubjectiveQuestionForm()
        formset = QuestionKeywordFormSet(prefix='kw')

    topics   = Topic.objects.all()
    chapters = Chapter.objects.all()
    return render(request, 'problems/create_subjective.html', {
        'form':    form,
        'formset': formset,
        'topics':  topics,
        'chapters':chapters,
    })
