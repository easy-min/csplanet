from django.db import models
from django.conf import settings
from .exam import Exam, ExamQuestion
from csplanet.apps.problems.models.subjective_problem import QuestionKeywordMapping


class TestSession(models.Model):
    exam         = models.ForeignKey(Exam, on_delete=models.CASCADE)
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    started_at   = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.exam.title}"
    
    def grade_all(self):
        total = 0
        for ua in self.answers.all():
            _, score = ua.grade()
            total += score

        result, created = ExamResult.objects.get_or_create(session=self)
        result.total_score = total
        result.save()
        return result


class UserAnswer(models.Model):
    session         = models.ForeignKey(TestSession, on_delete=models.CASCADE, related_name="answers")
    question        = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(
        'problems.ObjectiveChoice', null=True, blank=True, on_delete=models.SET_NULL
    )  # 객관식인 경우
    text_answer     = models.TextField(blank=True)  # 주관식인 경우
    is_correct      = models.BooleanField(default=False)
    score           = models.FloatField(default=0)

    def __str__(self):
        return f"Answer {self.id} for {self.session}"
    
    def grade(self):
        eq: ExamQuestion = self.question
        # 1) 객관식 채점
        if eq.objective:
            correct_id = eq.objective.correct_choice_id
            self.is_correct = (self.selected_choice_id == correct_id)
            self.score = eq.weight if self.is_correct else 0

        # 2) 주관식 채점
        elif eq.subjective:
            # SubjectiveProblem.grade_text 활용
            matched = eq.subjective.grade_text(self.text_answer or '')
            self.is_correct = matched
            self.score = eq.weight if matched else 0

        else:
            # 의도치 않은 경우
            self.is_correct = False
            self.score = 0

        self.save()
        return self.is_correct, self.score


class ExamResult(models.Model):
    session     = models.OneToOneField(TestSession, on_delete=models.CASCADE)
    total_score = models.FloatField()
    graded_at   = models.DateTimeField(auto_now_add=True)

    @property
    def status(self):
        if self.total_score < 50:
            return "FAIL"
        if self.total_score < 70:
            return "WARNING"
        if self.total_score < 90:
            return "PASS"
        return "EXCELLENT"

    def __str__(self):
        return f"Result {self.session.user.username} - {self.status}"
