from django.db import models
from django.conf import settings
from csplanet.apps.problems.models import Chapter, ObjectiveProblem, SubjectiveProblem

class Exam(models.Model):
    title            = models.CharField(max_length=100)
    start_datetime   = models.DateTimeField()
    end_datetime     = models.DateTimeField()
    total_questions  = models.PositiveIntegerField(
        default=10,
        help_text="Total number of questions"
    )
    objective_ratio  = models.PositiveSmallIntegerField(
        help_text="Percentage of objective questions"
    )
    chapters         = models.ManyToManyField(Chapter)
    created_by       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ExamQuestion(models.Model):
    exam       = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    objective  = models.ForeignKey(
        ObjectiveProblem,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    subjective = models.ForeignKey(
        SubjectiveProblem,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    weight     = models.FloatField()

    def __str__(self):
        return f"{self.exam.title} - Q{self.id}"
    
    def grade(self, submitted_answer):
        """
        submitted_answer: Test(응시 답안 모델) 인스턴스
        """
        # 객관식 채점 로직 (예시)
        if self.objective:
            # 예를 들어 selected_choice_id 비교 등
            is_correct = (submitted_answer.selected_choice_id == self.objective.correct_choice_id)
            score = self.weight if is_correct else 0

        # 주관식 채점
        elif self.subjective:
            is_correct = self.subjective.grade_text(submitted_answer.text_answer)
            score = self.weight if is_correct else 0

        else:
            is_correct = False
            score = 0

        # submitted_answer 에 결과 기록
        submitted_answer.is_correct = is_correct
        submitted_answer.score = score
        submitted_answer.save()
        return is_correct, score