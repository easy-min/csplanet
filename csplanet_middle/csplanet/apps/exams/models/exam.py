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