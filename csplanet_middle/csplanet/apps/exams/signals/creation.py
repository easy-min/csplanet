# csplanet/apps/exams/signals/creation.py

from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from ..models import Exam, ExamQuestion
from csplanet.apps.problems.models import ObjectiveProblem, SubjectiveProblem

@receiver(m2m_changed, sender=Exam.chapters.through)
def create_exam_questions_on_chapters(sender, instance: Exam, action, pk_set, **kwargs):
    """
    Exam 객체에 chapters가 추가된 후(post_add) 호출.
    total_questions, objective_ratio에 따라 ExamQuestion을 생성.
    """
    if action != 'post_add':
        return

    # 이미 문제를 생성한 상태라면 스킵
    if instance.questions.exists():
        return

    # 챕터(pk_set) 기반으로 문제 풀셋 조회
    chapters = instance.chapters.filter(pk__in=pk_set)
    objective_qs = ObjectiveProblem.objects.filter(chapter__in=chapters)
    subjective_qs = SubjectiveProblem.objects.filter(chapter__in=chapters)

    total = instance.total_questions
    obj_count = total * instance.objective_ratio // 100
    sub_count = total - obj_count

    selected_objectives = objective_qs.order_by('?')[:obj_count]
    selected_subjectives = subjective_qs.order_by('?')[:sub_count]

    order = 1
    for prob in selected_objectives:
        ExamQuestion.objects.create(
            exam=instance,
            objective=prob,
            weight=1.0,
            order=order
        )
        order += 1

    for prob in selected_subjectives:
        ExamQuestion.objects.create(
            exam=instance,
            subjective=prob,
            weight=1.0,
            order=order
        )
        order += 1
