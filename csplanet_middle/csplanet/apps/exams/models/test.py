from django.db import models
from django.conf import settings
from .exam import Exam, ExamQuestion
from problems.utils.nlp import tokenize_terms
from problems.models.subjective_problem import QuestionKeywordMapping

class TestSession(models.Model):
    exam         = models.ForeignKey(Exam, on_delete=models.CASCADE)
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    started_at   = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.exam.title}"
    
    
    def grade_all(self):
        """
        이 세션의 모든 UserAnswer를 grade()로 채점하고,
        ExamResult에 총점(total_score)를 저장/생성
        """
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
    ) #객관식인 경우
    text_answer     = models.TextField(blank=True) #주관식인 경우
    is_correct      = models.BooleanField(default=False)
    score           = models.FloatField(default=0)

    def __str__(self):
        return f"Answer {self.id} for {self.session}"
    
    def grade(self):
        """
        이 UserAnswer 인스턴스를 채점해서 is_correct, score를 업데이트.
        """
        eq: ExamQuestion = self.question
        # 1) 객관식 채점
        if eq.objective:
            correct_id = eq.objective.correct_choice_id  # 가정: ObjectiveProblem에 이 속성이 있음
            self.is_correct = (self.selected_choice_id == correct_id)
            self.score = eq.weight if self.is_correct else 0

        # 2) 주관식 채점 (형태소+동의어 매칭)
        elif eq.subjective:
            tokens = tokenize_terms(self.text_answer or '')
            mappings = QuestionKeywordMapping.objects.filter(question=eq.subjective).select_related('keyword')

            # 대표 키워드 + 동의어 수집
            terms = set()
            for m in mappings:
                terms.add(m.keyword.word.lower())
                for syn in m.keyword.synonyms:
                    terms.add(syn.lower())

            matched = bool(tokens & terms)
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