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


class QuestionKeywordMapping(models.Model):
    question = models.ForeignKey(
        'problems.SubjectiveProblem',
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


class SubjectiveProblem(BaseProblem):
    subjective_keywords = models.ManyToManyField(
        SubjectiveKeyword,
        through=QuestionKeywordMapping,
        related_name='subjective_questions',
        verbose_name='채점용 키워드',
    )

    class Meta:
        verbose_name = '주관식 문제'
        verbose_name_plural = '주관식 문제들'

    def __str__(self):
        return self.content[:50]
    
    def grade_text(self, answer_text: str) -> bool:
        """
        응답 텍스트에 대표 키워드나 동의어가 포함되어 있는지 간단히 검사합니다.
        """
        if not answer_text:
            return False
        text = answer_text.lower()
        mappings = QuestionKeywordMapping.objects.filter(question=self).select_related('keyword')

        for m in mappings:
            # 대표 키워드 + 동의어 리스트
            candidates = [m.keyword.word.lower()] + [syn.lower() for syn in m.keyword.synonyms]
            for term in candidates:
                if term and term in text:
                    return True
        return False
