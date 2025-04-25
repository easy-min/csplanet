# csplanet/apps/problems/models/subjective_problem.py

from django.db import models
from .base_problem import BaseProblem

class SubjectiveKeyword(models.Model):
    word = models.CharField(max_length=100, unique=True, verbose_name='대표 키워드')
    synonyms = models.JSONField(default=list, blank=True, verbose_name='동의어 목록')

    class Meta:
        verbose_name = '주관식 키워드'
        verbose_name_plural = '주관식 키워드들'

    def __str__(self):
        return self.word


class SubjectiveProblem(BaseProblem):
    subjective_keywords = models.ManyToManyField(
        SubjectiveKeyword,
        through='problems.QuestionKeywordMapping',  # 앱 레이블 포함
        related_name='subjective_questions',
        verbose_name='채점용 키워드',
    )

    class Meta:
        verbose_name = '주관식 문제'
        verbose_name_plural = '주관식 문제들'

    def __str__(self):
        return self.content[:50]


class QuestionKeywordMapping(models.Model):
    question = models.ForeignKey(
        SubjectiveProblem,                   # 직접 클래스 참조
        on_delete=models.CASCADE,
        verbose_name='문제',
    )
    keyword = models.ForeignKey(
        SubjectiveKeyword,
        on_delete=models.CASCADE,
        verbose_name='키워드',
    )
    importance = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='중요도',
        help_text='채점 시 가중치로 사용',
    )

    class Meta:
        unique_together = ('question', 'keyword')
        verbose_name = '문제-키워드 매핑'
        verbose_name_plural = '문제-키워드 매핑들'

    def __str__(self):
        return f'{self.question.id} ↔ {self.keyword.word}'
