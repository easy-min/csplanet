from django.db import models
from django.conf import settings
from .exam import Exam, ExamQuestion

class TestSession(models.Model):
    exam         = models.ForeignKey(Exam, on_delete=models.CASCADE)
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    started_at   = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.exam.title}"

class UserAnswer(models.Model):
    session         = models.ForeignKey(TestSession, on_delete=models.CASCADE, related_name="answers")
    question        = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(
        'problems.ObjectiveChoice', null=True, blank=True, on_delete=models.SET_NULL
    )
    text_answer     = models.TextField(blank=True)
    is_correct      = models.BooleanField(default=False)
    score           = models.FloatField(default=0)

    def __str__(self):
        return f"Answer {self.id} for {self.session}"

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