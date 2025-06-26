# exams/services/exam.py

import random
from django.utils import timezone
from csplanet.apps.problems.models import ObjectiveProblem, SubjectiveProblem, Chapter
from ..models import Exam, ExamQuestion, UserAnswer

# exams/services/exam.py

import random
import logging
from django.utils import timezone
from csplanet.apps.problems.models import ObjectiveProblem, SubjectiveProblem, Chapter
from ..models import Exam, ExamQuestion

def select_questions_with_notification(objective_problems, subjective_problems, objective_count, subjective_count):
    """
    요청한 개수만큼 문제를 뽑되, 부족하면 있는 만큼만 뽑고 관리자에게 알림
    """
    selected_objectives = []
    selected_subjectives = []
    
    # 객관식 문제
    if objective_problems.count() < objective_count:
        logging.warning(f"Not enough objective problems: requested {objective_count}, available {objective_problems.count()}")
        selected_objectives = list(objective_problems)  # 있는 만큼만
    else:
        selected_objectives = random.sample(list(objective_problems), objective_count)

    # 주관식 문제
    if subjective_problems.count() < subjective_count:
        logging.warning(f"Not enough subjective problems: requested {subjective_count}, available {subjective_problems.count()}")
        selected_subjectives = list(subjective_problems)  # 있는 만큼만
    else:
        selected_subjectives = random.sample(list(subjective_problems), subjective_count)

    # 부족 여부 체크
    objective_shortage = len(selected_objectives) < objective_count
    subjective_shortage = len(selected_subjectives) < subjective_count

    return selected_objectives, selected_subjectives, objective_shortage, subjective_shortage

def notify_admin_of_shortage(exam_title, objective_shortage, subjective_shortage):
    """
    문제 부족 시 관리자에게 알림 (이메일 또는 로그)
    """
    message = f"[Alert] 문제 부족 알림 - 시험: {exam_title}\n"
    if objective_shortage:
        message += "- 객관식 문제가 부족합니다.\n"
    if subjective_shortage:
        message += "- 주관식 문제가 부족합니다.\n"
    message += "빠른 확인 부탁드립니다."

    logging.warning(message)  # 로그로 남김

def create_exam_with_notification(
    title, start_datetime, end_datetime, total_questions, objective_ratio,
    chapters, created_by
):
    """
    시험 생성 및 문항 자동 구성, 문제 부족 시 관리자 알림
    """
    exam = Exam.objects.create(
        title=title,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        total_questions=total_questions,
        objective_ratio=objective_ratio,
        created_by=created_by,
    )
    exam.chapters.set(chapters)
    exam.save()

    objective_problems = ObjectiveProblem.objects.filter(chapter__in=chapters)
    subjective_problems = SubjectiveProblem.objects.filter(chapter__in=chapters)

    objective_count = int(total_questions * objective_ratio / 100)
    subjective_count = total_questions - objective_count

    selected_objectives, selected_subjectives, obj_short, subj_short = select_questions_with_notification(
        objective_problems, subjective_problems, objective_count, subjective_count
    )

    for obj in selected_objectives:
        ExamQuestion.objects.create(
            exam=exam,
            objective=obj,
            weight=1.0
        )
    for subj in selected_subjectives:
        ExamQuestion.objects.create(
            exam=exam,
            subjective=subj,
            weight=1.0
        )

    if obj_short or subj_short:
        notify_admin_of_shortage(exam.title, obj_short, subj_short)

    return exam

def update_exam_status():
    """
    모든 시험의 상태를 시간에 따라 자동 업데이트
    """
    now = timezone.now()
    # 준비중 → 진행중
    Exam.objects.filter(
        status='preparing',
        start_datetime__lte=now,
        end_datetime__gt=now
    ).update(status='ongoing')
    # 진행중 → 종료
    Exam.objects.filter(
        status='ongoing',
        end_datetime__lte=now
    ).update(status='finished')

def grade_user_answer(user_answer):
    """
    UserAnswer 인스턴스를 채점하고 결과 저장
    """
    if user_answer.question.objective:
        # 객관식 채점
        correct_id = user_answer.question.objective.correct_choice_id
        user_answer.is_correct = (user_answer.selected_choice_id == correct_id)
        user_answer.score = user_answer.question.weight if user_answer.is_correct else 0
    elif user_answer.question.subjective:
        # 주관식 채점 (기존 자동 채점, 추후 ChatGPT API 확장 가능)
        matched = user_answer.question.subjective.grade_text(user_answer.text_answer or '')
        user_answer.is_correct = matched
        user_answer.score = user_answer.question.weight if matched else 0
    else:
        # 의도치 않은 경우
        user_answer.is_correct = False
        user_answer.score = 0
    user_answer.save()
    return user_answer.is_correct, user_answer.score

# 추가로 필요한 서비스 함수를 아래에 계속 작성하세요.
