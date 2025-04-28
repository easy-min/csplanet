# apps/problems/views/objective_upsert.py

from django.shortcuts                import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http    import require_http_methods

from ..forms.forms                  import ObjectiveQuestionForm, ObjectiveChoiceFormSet
from ..models.objective_problem     import ObjectiveProblem
from ..models.base_problem          import BaseProblem
from ..models.topic                 import Topic
from ..models.chapter               import Chapter

@login_required
@require_http_methods(["GET", "POST"])
def objective_upsert(request, pk=None):
    # 1) instance 결정: pk 있으면 edit, 없으면 create
    problem  = get_object_or_404(ObjectiveProblem, pk=pk) if pk else None
    topics   = Topic.objects.all()
    chapters = Chapter.objects.all()

    if request.method == "POST":
        #print(request.POST)
        form    = ObjectiveQuestionForm(request.POST, instance=problem)
        formset = ObjectiveChoiceFormSet(request.POST, instance=problem)

        if form.is_valid() and formset.is_valid():
            # 2) 문제 저장(commit=False → topic, creator, type 설정)
            obj = form.save(commit=False)
            obj.topic = obj.chapter.topic
            if problem is None:
                obj.creator       = request.user
                obj.question_type = BaseProblem.MCQ
            obj.save()

            # 3) formset.instance 갱신 및 저장(DELETE 포함)
            formset.instance = obj
            formset.save()

            return redirect('problems:detail_objective', pk=obj.pk)
        # 유효성 에러 시 fall through → 같은 form/formset 그대로 렌더링

    else:
        # GET: 새 폼 / edit 폼
        form    = ObjectiveQuestionForm(instance=problem)
        formset = ObjectiveChoiceFormSet(instance=problem)

    return render(request, 'problems/create_objective.html', {
        'form':     form,
        'formset':  formset,
        'topics':   topics,
        'chapters': chapters,
        'problem':  problem,
        'edit':     bool(pk),
    })
@login_required
@require_http_methods(["GET"])
def detail_objective(request, pk):
    """
    객관식 문제 상세 보기
    """
    problem = get_object_or_404(ObjectiveProblem, pk=pk)
    return render(request, 'problems/objective_detail.html', {
        'problem': problem
    })
