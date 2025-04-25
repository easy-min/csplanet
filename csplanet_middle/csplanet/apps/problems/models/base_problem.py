from django.conf import settings
from django.db import models

from .chapter import Chapter


class BaseProblem(models.Model):
    """
    문제의 공통 속성(추상 모델).
    """
    MCQ = "MCQ"
    SA = "SA"
    QUESTION_TYPES = [
        (MCQ, "객관식"),
        (SA,  "주관식"),
    ]

    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        verbose_name="단원",
        help_text="이 문제가 속한 단원을 선택하세요.",
    )

    question_type = models.CharField(
        max_length=3,
        choices=QUESTION_TYPES,
        verbose_name="문제 유형",
        help_text="객관식(MCQ) 또는 주관식(SA)을 선택하세요.",
    )
    content = models.TextField(
        verbose_name="문제 내용",
        help_text="문제 내용을 입력하세요.",
    )
    explanation = models.TextField(
        blank=True,
        verbose_name="해설",
        help_text="정답 해설을 입력하세요 (선택사항).",
    )
    score = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="배점",
        help_text="이 문제의 배점을 입력하세요.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일",
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="작성자",
        help_text="문제를 작성한 사용자입니다.",
    )

    class Meta:
        abstract = True

    def __str__(self):
        teaser = self.content[:30]
        return f"[{self.get_question_type_display()}] {teaser}…"
