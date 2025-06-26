# serializers.py
from rest_framework import serializers
from ..models import Exam, ExamQuestion, TestSession, UserAnswer, ExamResult

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
