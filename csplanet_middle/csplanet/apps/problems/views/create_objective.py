from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from ..forms.forms import ObjectiveQuestionForm, ObjectiveChoiceFormSet
from ..models.objective_problem import ObjectiveProblem
from ..models.base_problem import BaseProblem
from ..models.topic import Topic
from ..models.chapter import Chapter

@require_http_methods(["GET", "POST"])
def create_objective(request):
    topics = Topic.objects.all()
    chapters = Chapter.objects.all()

    if request.method == "POST":
        form = ObjectiveQuestionForm(request.POST)
        obj_q = None

        if form.is_valid():
            obj_q = form.save(commit=False)
            obj_q.topic = obj_q.chapter.topic
            obj_q.creator = request.user
            obj_q.question_type = BaseProblem.MCQ
            obj_q.save()

        formset = ObjectiveChoiceFormSet(
            request.POST,
            instance=obj_q or ObjectiveProblem()
        )

        if form.is_valid() and formset.is_valid():
            formset.save()
            return redirect('problems:detail_objective', pk=obj_q.pk)
    else:
        form = ObjectiveQuestionForm()
        formset = ObjectiveChoiceFormSet(instance=ObjectiveProblem())

    return render(request, 'problems/create_objective.html', {
        'form': form,
        'formset': formset,
        'topics': topics,
        'chapters': chapters,
    })

@require_http_methods(["GET"])
def detail_objective(request, pk):
    problem = get_object_or_404(ObjectiveProblem, pk=pk)
    return render(request, 'problems/objective_detail.html', {
        'problem': problem
    })

@require_http_methods(["GET", "POST"])
def edit_objective(request, pk):
    problem = get_object_or_404(ObjectiveProblem, pk=pk)
    topics = Topic.objects.all()
    chapters = Chapter.objects.all()

    if request.method == "POST":
        form = ObjectiveQuestionForm(request.POST, instance=problem)
        formset = ObjectiveChoiceFormSet(request.POST, instance=problem)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('problems:detail_objective', pk=problem.pk)
    else:
        form = ObjectiveQuestionForm(instance=problem)
        formset = ObjectiveChoiceFormSet(instance=problem)

    return render(request, 'problems/create_objective.html', {
        'form': form,
        'formset': formset,
        'topics': topics,
        'chapters': chapters,
        'problem':problem,
        'edit': True,
        
    })
