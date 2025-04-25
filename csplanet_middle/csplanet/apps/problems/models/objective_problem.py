from django.db import models
from ..models.base_problem import BaseProblem

class ObjectiveProblem(BaseProblem):
    class Meta:
        verbose_name = "객관식 문제"
        verbose_name_plural = "객관식 문제들"

class ObjectiveChoice(models.Model):
    question = models.ForeignKey(
        ObjectiveProblem,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name='문제',
    )
    content = models.CharField(
        max_length=200,
        verbose_name='보기 내용',
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name='정답 여부',
    )

    class Meta:
        verbose_name = '객관식 보기'
        verbose_name_plural = '객관식 보기들'

    def __str__(self):
        return f"{self.content} ({'정답' if self.is_correct else '오답'})"