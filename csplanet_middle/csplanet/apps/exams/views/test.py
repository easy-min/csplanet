from django.shortcuts      import render, get_object_or_404, redirect
from django.utils          import timezone
from ..models              import Exam, TestSession, ExamQuestion, ExamResult
from ..forms               import AnswerForm

# 응시 가능 Exam 목록
def exam_available(request):
    now   = timezone.now()
    exams = Exam.objects.filter(start_datetime__lte=now, end_datetime__gte=now)
    return render(request, 'exams/list.html', {'exams': exams})

# 시험 응시 시작
def exam_take(request, exam_pk):
    exam = get_object_or_404(Exam, pk=exam_pk)
    now  = timezone.now()
    if not (exam.start_datetime <= now <= exam.end_datetime):
        return render(request, 'exams/unavailable.html')
    session   = TestSession.objects.create(exam=exam, user=request.user)
    questions = exam.questions.all()
    return render(request, 'exams/take.html', {
        'session': session,
        'questions': questions,
        'expires_at': exam.end_datetime,
    })

# 답안 제출 및 채점
def exam_submit(request, session_pk):
    session = get_object_or_404(TestSession, pk=session_pk, user=request.user)
    if request.method == 'POST':
        # 문제별로 AnswerForm(prefix=question.id) 생성
        for question in session.exam.questions.all():
            form = AnswerForm(
                request.POST,
                prefix=str(question.id),
                instance=question.useranswer_set.create(session=session, question=question)
            )
            if form.is_valid():
                answer = form.save(commit=False)
                # 채점 로직
                if question.objective:
                    # 객관식: 선택지의 is_correct로 채점
                    correct = bool(answer.selected_choice and answer.selected_choice.is_correct)
                    answer.is_correct = correct
                    answer.score = question.weight if correct else 0
                elif question.subjective:
                    # 주관식: 키워드 기반 간단 채점
                    text = answer.text_answer or ''
                    # QuestionKeywordMapping이 keyword.name으로 존재
                    keywords = [mapping.keyword.name for mapping in question.subjective.questionkeywordmapping_set.all()]
                    matched = any(kw.lower() in text.lower() for kw in keywords)
                    answer.is_correct = matched
                    answer.score = question.weight if matched else 0
                else:
                    answer.is_correct = False
                    answer.score = 0
                answer.save()

        # 총점 계산 및 결과 생성
        total = sum(a.score for a in session.answers.all())
        ExamResult.objects.create(session=session, total_score=total)

        # 세션 완료 시간 저장
        session.completed_at = timezone.now()
        session.save()
        return redirect('exams:exam_result', session_pk=session.pk)

    return redirect('exams:exam_available')

# 시험 결과
def exam_result(request, session_pk):
    result = get_object_or_404(ExamResult, session__pk=session_pk, session__user=request.user)
    return render(request, 'exams/result.html', {'result': result})