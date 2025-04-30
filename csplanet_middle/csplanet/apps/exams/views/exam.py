# csplanet/apps/exams/views/exam.py

from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from ..models import Exam, ExamQuestion
from ..forms import ExamForm
from csplanet.apps.problems.models import ObjectiveProblem, SubjectiveProblem
from ..models import Exam, TestSession, ExamResult
import random

def exam_list(request):
    """
    /exams/ — 전체 시험 목록 (관리자 전용)
    시작 전, 진행 중, 종료된 시험을 구분하여 버튼/배지 표시
    """
    now = timezone.now()
    exams = Exam.objects.all().order_by('-start_datetime')
    return render(request, "exams/list.html", {
        'exams': exams,
        'now': now,
    })

def exam_create(request):
    """
    /exams/create/ — 시험 생성 및 문제 자동 배분
    """
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

            selected_objs = random.sample(obj_pool, min(obj_count, len(obj_pool)))
            selected_subs = random.sample(subj_pool, min(subj_count, len(subj_pool)))

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
    """
    /exams/<pk>/edit/ — 시험 정보 수정
    """
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            return redirect('exams:exam_list')
    else:
        form = ExamForm(instance=exam)

    return render(request, 'exams/create.html', {'form': form})

def exam_print(request, exam_id):
    """
    /exams/<exam_id>/print/ — 시험지 프린트용 뷰
    """
    exam = get_object_or_404(Exam, pk=exam_id)
    return render(request, 'exams/print.html', {'exam': exam})

def session_list(request, exam_pk):
    """
    관리자용: 해당 시험에 응시한 세션(사용자) 목록과 점수/상태 보기
    URL: /exams/<exam_pk>/sessions/
    """
    exam     = get_object_or_404(Exam, pk=exam_pk)
    sessions = (
        TestSession.objects
        .filter(exam=exam)
        .select_related('user')
        .order_by('-started_at')
    )

    data = []
    for sess in sessions:
        try:
            result = sess.examresult
            score  = result.total_score
            status = result.status
        except ExamResult.DoesNotExist:
            score  = None
            status = '진행 중'
        data.append({
            'session': sess,
            'score': score,
            'status': status,
        })

    return render(request, 'exams/session_list.html', {
        'exam': exam,
        'data': data,
    })