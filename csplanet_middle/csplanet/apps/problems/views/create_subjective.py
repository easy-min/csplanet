from django.shortcuts             import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.db                    import transaction
from django.contrib.auth.decorators import login_required
from ..forms.forms                import SubjectiveQuestionForm, QuestionKeywordFormSet
from ..models.subjective_problem  import SubjectiveProblem
from ..models.topic               import Topic
from ..models.chapter             import Chapter

@login_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def subjective_upsert(request, pk=None):
    # pk가 있으면 수정(edit), 없으면 생성(create)
    problem = get_object_or_404(SubjectiveProblem, pk=pk) if pk else None

    if request.method == 'POST':
        form    = SubjectiveQuestionForm(request.POST, instance=problem)
        formset = QuestionKeywordFormSet(request.POST, prefix='kw', instance=problem)

        # 디버깅 출력
        print("▶ POST DATA:", request.POST)
        print("▶ form valid?", form.is_valid(), form.errors)
        print("▶ formset valid?", formset.is_valid(), formset.errors)

        if form.is_valid() and formset.is_valid():
            obj = form.save(commit=False)
            obj.creator = request.user
            obj.q_type  = 'subjective'
            if not pk:
                obj.topic = obj.chapter.topic
            obj.save()

            formset.instance = obj
            formset.save()
            return redirect('problems:detail_subjective', pk=obj.pk)
    else:
        form    = SubjectiveQuestionForm(instance=problem)
        formset = QuestionKeywordFormSet(prefix='kw', instance=problem)

    topics   = Topic.objects.all()
    chapters = Chapter.objects.all()
    return render(request, 'problems/create_subjective.html', {
        'form':     form,
        'formset':  formset,
        'topics':   topics,
        'chapters': chapters,
        'edit':     bool(pk),
    })

@login_required
@require_http_methods(["GET"])
def detail_subjective(request, pk):
    """
    주관식 문제 상세보기
    """
    problem = get_object_or_404(SubjectiveProblem, pk=pk)
    return render(request, 'problems/subjective_detail.html', {
        'problem': problem
    })
