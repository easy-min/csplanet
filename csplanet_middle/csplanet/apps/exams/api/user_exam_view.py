from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from ..serializers import (
    ExamSerializer,
    ExamQuestionDetailSerializer,
    ExamQuestionDetailAdminSerializer,
    TestSessionSerializer,
    UserAnswerSerializer,
    ExamResultSerializer,
)
from ..models import Exam, TestSession, UserAnswer, ExamResult


class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    사용자용 시험 조회 및 문제 목록 제공
    """
    queryset = Exam.objects.filter(start_datetime__lte=timezone.now(),
                                   end_datetime__gte=timezone.now()) \
                           .order_by('-start_datetime')
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'], url_path='questions')
    def questions(self, request, pk=None):
        exam = self.get_object()
        qs = exam.questions.all().order_by('order')
        if request.user.is_staff:
            serializer = ExamQuestionDetailAdminSerializer(qs, many=True)
        else:
            serializer = ExamQuestionDetailSerializer(qs, many=True)
        return Response(serializer.data)


class UserSessionViewSet(viewsets.ViewSet):
    """
    사용자 세션 생성, 답안 저장, 제출, 결과 조회
    """
    permission_classes = [IsAuthenticated]

    def create(self, request, pk=None):
        exam = get_object_or_404(Exam, pk=pk)
        session = TestSession.objects.create(user=request.user, exam=exam)
        serializer = TestSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='questions')
    def questions(self, request, pk=None):
        session = get_object_or_404(TestSession, pk=pk, user=request.user)
        qs = session.exam.questions.all().order_by('order')
        if request.user.is_staff:
            serializer = ExamQuestionDetailAdminSerializer(qs, many=True)
        else:
            serializer = ExamQuestionDetailSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='answers')
    def save_answers(self, request, pk=None):
        session = get_object_or_404(TestSession, pk=pk, user=request.user)
        serializer = UserAnswerSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        for data in serializer.validated_data:
            UserAnswer.objects.update_or_create(
                session=session,
                question_id=data['selected_choice'].question_id,
                defaults={
                    'selected_choice': data['selected_choice'],
                    'text_answer': data.get('text_answer', '')
                }
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        session = get_object_or_404(TestSession, pk=pk, user=request.user)
        session.is_submitted = True
        session.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='result')
    def result(self, request, pk=None):
        session = get_object_or_404(TestSession, pk=pk, user=request.user)
        result = get_object_or_404(ExamResult, session=session)
        serializer = ExamResultSerializer(result)
        return Response(serializer.data)
