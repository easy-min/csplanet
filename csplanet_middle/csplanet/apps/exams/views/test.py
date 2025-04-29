from collections import defaultdict
from django.shortcuts      import render, get_object_or_404, redirect
from django.utils          import timezone
from django.db.models      import Sum, Prefetch
from ..models              import Exam, TestSession, ExamQuestion, ExamResult, UserAnswer
from ..forms               import AnswerForm
import datetime

import calendar
import datetime

from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from ..models import Exam, ExamResult, TestSession
# views.py
import calendar
from datetime import date
from django.shortcuts import render
from django.urls import reverse
from problems.utils.nlp   import tokenize_terms
from problems.models.subjective_problem import QuestionKeywordMapping

def monthly_calendar(request):
    year  = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))

    # 마감일(end_datetime) 기준으로 해당 월의 시험만 가져와서 날짜별로 묶기
    qs = Exam.objects.filter(
        end_datetime__year=year,
        end_datetime__month=month
    )
    calendar_map = defaultdict(list)
    for exam in qs:
        calendar_map[exam.end_datetime.date()].append(exam)

    # 달력의 시작·끝 날짜 계산
    first_weekday, last_day = calendar.monthrange(year, month)
    start_date = datetime.date(year, month, 1) - datetime.timedelta(days=first_weekday)
    end_date   = datetime.date(year, month, last_day)
    total = (end_date - start_date).days + 1
    if total % 7 != 0:
        total += 7 - (total % 7)

    dates = [start_date + datetime.timedelta(days=i) for i in range(total)]
    weeks = [dates[i:i+7] for i in range(0, len(dates), 7)]

    month_weeks = []
    for week in weeks:
        week_cells = []
        for day in week:
            week_cells.append({
                'date': day,
                'exams': calendar_map.get(day, []),
            })
        month_weeks.append(week_cells)

    # 이전/다음 달 계산
    ref = datetime.date(year, month, 15)
    prev = ref - datetime.timedelta(days=31)
    nxt  = ref + datetime.timedelta(days=31)

    return render(request, 'exams/monthly_calendar.html', {
        'month_weeks': month_weeks,
        'year':        year,
        'month':       month,
        'today':       timezone.now().date(),
        'prev_year':   prev.year,
        'prev_month':  prev.month,
        'next_year':   nxt.year,
        'next_month':  nxt.month,
    })

def list_exams(request):
    now   = timezone.now()
    exams = list(Exam.objects.all().order_by('-start_datetime'))

    # 1) 유저가 완료한 세션과 결과 미리 가져오기
    completed_sessions = TestSession.objects.filter(
        user=request.user,
        completed_at__isnull=False,
        exam__in=exams
    )
    results = {
        r.session.exam_id: r
        for r in ExamResult.objects.filter(session__in=completed_sessions)
    }

    # 2) 각 exam 에 user_result 속성 붙여주기
    for exam in exams:
        exam.user_result = results.get(exam.pk)  # 없으면 None

    return render(request, "exams/available.html", {
        'now': now,
        'exams': exams,
    })

def solve_list(request, exam_pk):
    """
    /exams/solve/<exam_pk>/ — 특정 시험의 문제 목록
    """
    exam      = get_object_or_404(Exam, pk=exam_pk)
    questions = exam.questions.all()
    return render(request, "exams/solve_list_for_exam.html", {
        'exam': exam,
        'questions': questions,
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.utils   import timezone
from django.db.models import Sum
from ..models       import Exam, TestSession, ExamQuestion, ExamResult, UserAnswer
from ..forms        import AnswerForm

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Sum
from ..models import Exam, TestSession, ExamResult
from ..forms import AnswerForm

def exam_take(request, exam_pk):
    exam      = get_object_or_404(Exam, pk=exam_pk)
    now       = timezone.now()
    if not (exam.start_datetime <= now <= exam.end_datetime):
        return render(request, 'exams/unavailable.html', {'exam': exam})

    # 이미 완료된 세션 체크
    completed = TestSession.objects.filter(
        exam=exam, user=request.user, completed_at__isnull=False
    ).first()
    if completed:
        return render(request, 'exams/already_taken.html', {
            'exam': exam,
            'completed_session_pk': completed.pk,
        })

    # 진행 중 세션 재사용 또는 생성
    session, _ = TestSession.objects.get_or_create(
        exam=exam, user=request.user, completed_at__isnull=True
    )

    if request.method == 'POST':
        # 기존 답안 지우고
        session.answers.all().delete()

        for q in exam.questions.all():
            form = AnswerForm(request.POST, prefix=str(q.id))
            if not form.is_valid():
                continue
            answer = form.save(commit=False)
            answer.session  = session
            answer.question = q

            # 객관식
            if q.objective:
                correct = bool(answer.selected_choice and answer.selected_choice.is_correct)
                answer.is_correct = correct
                answer.score      = q.weight if correct else 0

            # 주관식 (형태소+동의어)
            else:
                answer = _grade_subjective(q, answer)

            answer.save()

        # 총점 및 결과
        total = session.answers.aggregate(total=Sum('score'))['total'] or 0
        ExamResult.objects.update_or_create(
            session=session,
            defaults={'total_score': total}
        )
        session.completed_at = timezone.now()
        session.save()
        return redirect('exams:exam_result', session_pk=session.pk)

    # GET: 빈 폼
    forms = {q.id: AnswerForm(prefix=str(q.id)) for q in exam.questions.all()}
    return render(request, 'exams/take.html', {
        'session':   session,
        'questions': exam.questions.all(),
        'forms_dict': forms,
        'expires_at': exam.end_datetime,
    })



def exam_submit(request, session_pk):
    session = get_object_or_404(TestSession, pk=session_pk, user=request.user)
    if request.method != 'POST':
        return redirect('exams:list_exams')

    session.answers.all().delete()

    for q in session.exam.questions.all():
        form = AnswerForm(request.POST, prefix=str(q.id))
        if not form.is_valid():
            continue
        answer = form.save(commit=False)
        answer.session  = session
        answer.question = q

        if q.objective:
            correct = bool(answer.selected_choice and answer.selected_choice.is_correct)
            answer.is_correct = correct
            answer.score      = q.weight if correct else 0
        else:
            answer = _grade_subjective(q, answer)

        answer.save()

    total = session.answers.aggregate(score=Sum('score'))['score'] or 0
    ExamResult.objects.update_or_create(
        session=session,
        defaults={'total_score': total}
    )
    session.completed_at = timezone.now()
    session.save()
    return redirect('exams:exam_result', session_pk=session.pk)


def exam_result(request, session_pk):
    """
    /exams/result/<session_pk>/ — 시험 결과 페이지
    """
    # staff(관리자)는 모든 결과 조회 허용, 일반 사용자는 본인(session.user) 결과만
    lookup = {'session__pk': session_pk}
    if not request.user.is_staff:
        lookup['session__user'] = request.user

    result = get_object_or_404(ExamResult, **lookup)

    return render(request, 'exams/result.html', {
        'result': result,
    })


def _grade_subjective(q, answer):
    """
    q: ExamQuestion
    answer: UserAnswer 인스턴스 (commit=False 상태)
    """
    text = (answer.text_answer or '').lower()
    tokens = tokenize_terms(text)

    # 매핑된 키워드 + 동의어 모두 수집
    mappings = QuestionKeywordMapping.objects.filter(question=q.subjective).select_related('keyword')
    terms = {
        m.keyword.word.lower()
        for m in mappings
    }
    # JSONField 에 담긴 동의어 추가
    for m in mappings:
        for syn in m.keyword.synonyms:
            terms.add(syn.lower())

    matched = bool(tokens & terms)
    answer.is_correct = matched
    answer.score      = q.weight if matched else 0
    return answer