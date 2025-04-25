# csplanet/apps/problems/views/views.py

from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from ..forms.forms import ObjectiveQuestionForm, ObjectiveChoiceFormSet
from ..models.objective_problem import ObjectiveProblem
from ..models.base_problem import BaseProblem
from ..models.topic import Topic
from ..models.chapter import Chapter

@require_http_methods(["GET", "POST"])
def create_objective(request):
    topics   = Topic.objects.all()
    chapters = Chapter.objects.all()

    if request.method == "POST":
        form    = ObjectiveQuestionForm(request.POST)
        obj_q   = None

        if form.is_valid():
            obj_q = form.save(commit=False)
            obj_q.creator       = request.user
            obj_q.question_type = BaseProblem.MCQ    # ★ 꼭 MCQ로 세팅
            obj_q.save()

        # form 유효성 검사 후에도 반드시 instance 지정
        formset = ObjectiveChoiceFormSet(
            request.POST,
            instance = obj_q or ObjectiveProblem()
        )

        if form.is_valid() and formset.is_valid():
            formset.save()
            return redirect('problems:solve_problems')

    else:
        form    = ObjectiveQuestionForm()
        formset = ObjectiveChoiceFormSet(instance=ObjectiveProblem())

    return render(request, 'problems/create_objective.html', {
        'form':     form,
        'formset':  formset,
        'topics':   topics,
        'chapters': chapters,
    })