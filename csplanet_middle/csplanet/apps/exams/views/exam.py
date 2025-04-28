from django.shortcuts import get_object_or_404, render, redirect
from ..models import Exam, ExamQuestion
from ..forms  import ExamForm
from csplanet.apps.problems.models import ObjectiveProblem, SubjectiveProblem
import random

def exam_list(request):
    exams = Exam.objects.all()
    return render(request, 'exams/list.html', {'exams': exams})

def exam_create(request):
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = request.user
            exam.save()
            form.save_m2m()

            # 문제 추출 로직
            total = exam.total_questions
            obj_count = int(total * exam.objective_ratio / 100)
            subj_count = total - obj_count

            chapters = exam.chapters.all()
            obj_pool = list(ObjectiveProblem.objects.filter(chapter__in=chapters))
            subj_pool = list(SubjectiveProblem.objects.filter(chapter__in=chapters))

            selected_objs = random.sample(obj_pool, min(obj_count, len(obj_pool))) if obj_pool else []
            selected_subs = random.sample(subj_pool, min(subj_count, len(subj_pool))) if subj_pool else []

            count = len(selected_objs) + len(selected_subs)
            weight = 100.0 / count if count else 0

            for prob in selected_objs:
                ExamQuestion.objects.create(
                    exam=exam, objective=prob, weight=weight
                )
            for prob in selected_subs:
                ExamQuestion.objects.create(
                    exam=exam, subjective=prob, weight=weight
                )

            return redirect('exams:exam_list')
    else:
        form = ExamForm()
    return render(request, 'exams/create.html', {'form': form})

def exam_edit(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            return redirect('exams:exam_list')
    else:
        form = ExamForm(instance=exam)
    return render(request, 'exams/create.html', {'form': form})

def exam_detail(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    return render(request, 'exams/detail.html', {'exam': exam})