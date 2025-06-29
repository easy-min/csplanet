# serializers.py
from rest_framework import serializers
from ..models import Exam, ExamQuestion, TestSession, UserAnswer, ExamResult
from csplanet.apps.problems.models import ObjectiveChoice, SubjectiveKeyword


class ExamSerializer(serializers.ModelSerializer):
    start_datetime = serializers.DateTimeField(format="%Y-%m-%dT%H:%M")
    end_datetime = serializers.DateTimeField(format="%Y-%m-%dT%H:%M")
    class Meta:
        model = Exam
        fields = ['title', 'start_datetime', 'end_datetime', 'total_questions', 'chapters', 'objective_ratio']

class ExamQuestionSerializer(serializers.ModelSerializer):
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


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectiveChoice
        fields = ('id', 'text')


class ExamQuestionDetailSerializer(serializers.ModelSerializer):
    """
    순수하게 문제와 객관식 선택지(or 주관식 텍스트)만 노출
    """
    type = serializers.SerializerMethodField()         # 문제 유형
    question_text = serializers.SerializerMethodField()  # 질문 텍스트
    choices = serializers.SerializerMethodField()      # 객관식 선택지 리스트

    class Meta:
        model = ExamQuestion
        fields = ('id', 'type', 'question_text', 'choices', 'order')

    def get_type(self, obj):
        return 'objective' if obj.objective_id else 'subjective'

    def get_question_text(self, obj):
        if obj.objective:
            return obj.objective.text  # ObjectiveProblem의 질문 필드명
        return obj.subjective.text      # SubjectiveProblem의 질문 필드명

    def get_choices(self, obj):
        if not obj.objective:
            return None
        # obj.objective.choices: ObjectiveProblem ↔ Choice 역참조 필드명
        return ChoiceSerializer(obj.objective.choices.all(), many=True).data