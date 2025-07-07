# serializers.py

from rest_framework import serializers
from ..models import Exam, ExamQuestion, TestSession, UserAnswer, ExamResult
from csplanet.apps.problems.models import ObjectiveChoice, SubjectiveKeyword


class ExamSerializer(serializers.ModelSerializer):
    start_datetime = serializers.DateTimeField(format="%Y-%m-%dT%H:%M")
    end_datetime = serializers.DateTimeField(format="%Y-%m-%dT%H:%M")

    class Meta:
        model = Exam
        fields = [
            'id', 'title',
            'start_datetime', 'end_datetime',
            'total_questions', 'chapters',
            'objective_ratio'
        ]


class ExamQuestionSerializer(serializers.ModelSerializer):
    """관리자용 전체 필드 포함 기본 Serializer"""
    class Meta:
        model = ExamQuestion
        fields = '__all__'


class TestSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSession
        fields = '__all__'


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = ['selected_choice', 'text_answer']


class ExamResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamResult
        fields = '__all__'


# ─── Choice Serializers ─────────────────────────────────────────────────────

class ChoiceSerializer(serializers.ModelSerializer):
    """사용자용: 텍스트만 노출"""
    class Meta:
        model = ObjectiveChoice
        fields = ('id', 'text')


class ChoiceAdminSerializer(serializers.ModelSerializer):
    """관리자용: 정답 여부 포함"""
    class Meta:
        model = ObjectiveChoice
        fields = ('id', 'text', 'is_correct')


# ─── Base Detail Serializer ──────────────────────────────────────────────────

class BaseExamQuestionDetailSerializer(serializers.ModelSerializer):
    """
    문제 유형, 본문, 선택지, 순서, 배점을 공통으로 처리
    하위 클래스에서 get_choices() 구현 필수
    """
    type = serializers.SerializerMethodField()
    question_text = serializers.SerializerMethodField()
    choices = serializers.SerializerMethodField()

    class Meta:
        model = ExamQuestion
        fields = ('id', 'type', 'question_text', 'choices', 'order', 'weight')

    def get_type(self, obj):
        return 'objective' if obj.objective_id else 'subjective'

    def get_question_text(self, obj):
        if obj.objective:
            return obj.objective.text
        return obj.subjective.text if obj.subjective else None

    def get_choices(self, obj):
        raise NotImplementedError("서브클래스에서 get_choices 구현 필요")


# ─── User Detail Serializer ──────────────────────────────────────────────────

class ExamQuestionDetailSerializer(BaseExamQuestionDetailSerializer):
    """
    사용자용: 문제 본문과 선택지만 제공
    (정답, 해설 등 민감 정보 제외)
    """
    def get_choices(self, obj):
        if not obj.objective:
            return None
        return ChoiceSerializer(obj.objective.choices.all(), many=True).data


# ─── Admin Detail Serializer ─────────────────────────────────────────────────

class ExamQuestionDetailAdminSerializer(BaseExamQuestionDetailSerializer):
    """
    관리자용: 정답, 해설, 선택지의 is_correct 등
    모든 정보 포함
    """
    explanation = serializers.SerializerMethodField()
    correct_answer = serializers.SerializerMethodField()

    class Meta(BaseExamQuestionDetailSerializer.Meta):
        fields = BaseExamQuestionDetailSerializer.Meta.fields + (
            'explanation',
            'correct_answer',
        )

    def get_choices(self, obj):
        if not obj.objective:
            return None
        return ChoiceAdminSerializer(obj.objective.choices.all(), many=True).data

    def get_explanation(self, obj):
        if obj.objective:
            return getattr(obj.objective, 'explanation', None)
        return getattr(obj.subjective, 'explanation', None) if obj.subjective else None

    def get_correct_answer(self, obj):
        if obj.objective:
            correct = obj.objective.choices.filter(is_correct=True).first()
            return correct.id if correct else None
        # 주관식의 키워드 정답 반환
        if obj.subjective and hasattr(obj.subjective, 'keywords'):
            keywords = obj.subjective.keywords.all()
            return [kw.keyword for kw in keywords] if keywords else None
        return None
