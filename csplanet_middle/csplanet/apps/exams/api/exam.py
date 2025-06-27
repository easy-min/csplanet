from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from ..models import Exam, ExamQuestion, TestSession, ExamResult, UserAnswer
from ..serializers import ExamSerializer, ExamQuestionSerializer, TestSessionSerializer, ExamResultSerializer
from csplanet.apps.problems.models import ObjectiveProblem, SubjectiveProblem
from csplanet.apps.exams.services.exam import create_exam_with_notification

# csplanet/apps/exams/api/exam.py

from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from ..models import Exam, ExamQuestion, TestSession, ExamResult, UserAnswer
from ..serializers import ExamSerializer, ExamQuestionSerializer, TestSessionSerializer, ExamResultSerializer

class AdminExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all().order_by('-start_datetime')
    serializer_class = ExamSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['get'], url_path='print')
    def print(self, request, pk=None):
        exam = self.get_object()
        serializer = self.get_serializer(exam)
        return Response(serializer.data)  # 반드시 Response 반환

    @action(detail=True, methods=['get'], url_path='sessions')
    def sessions(self, request, pk=None):
        exam = self.get_object()
        sessions = TestSession.objects.filter(exam=exam).select_related('user').order_by('-started_at')
        data = []
        for sess in sessions:
            try:
                result = sess.examresult
                data.append({
                    'session': TestSessionSerializer(sess).data,
                    'score': result.total_score,
                    'status': result.status,
                })
            except ExamResult.DoesNotExist:
                data.append({
                    'session': TestSessionSerializer(sess).data,
                    'score': None,
                    'status': '진행 중',
                })
        return Response(data)  # 반드시 Response 반환

    @action(detail=True, methods=['get'], url_path='results')
    def results(self, request, pk=None):
        exam = self.get_object()
        results = ExamResult.objects.filter(session__exam=exam)
        serializer = ExamResultSerializer(results, many=True)
        return Response(serializer.data)  # 반드시 Response 반환
class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exam.objects.all().order_by('-start_datetime')
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'], url_path='questions')
    def questions(self, request, pk=None):
        exam = self.get_object()
        questions = exam.questions.all()
        serializer = ExamQuestionSerializer(questions, many=True)
        return Response(serializer.data)  # 반드시 Response 반환
# 사용자용 세션 ViewSet
class UserSessionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, pk=None):
        exam = get_object_or_404(Exam, pk=pk)
        now = timezone.now()
        if not (exam.start_datetime <= now <= exam.end_datetime):
            return Response({'message': '시험 기간이 아닙니다.'}, status=status.HTTP_403_FORBIDDEN)
        completed = TestSession.objects.filter(exam=exam, user=request.user, completed_at__isnull=False).first()
        if completed:
            return Response({
                'message': '이미 응시한 시험입니다.',
                'completed_session_pk': completed.pk
            })
        session, _ = TestSession.objects.get_or_create(exam=exam, user=request.user, completed_at__isnull=True)
        questions = exam.questions.all()
        serializer = ExamQuestionSerializer(questions, many=True)
        return Response({'session': session.pk, 'questions': serializer.data})

    def retrieve(self, request, pk=None, session_pk=None):
        session = get_object_or_404(TestSession, pk=session_pk, user=request.user)
        serializer = TestSessionSerializer(session)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='answers')
    def save_answers(self, request, pk=None, session_pk=None):
        # 답안 저장 로직 (예시)
        return Response({'message': '답안 저장 완료'})

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None, session_pk=None):
        # 시험 제출 로직 (예시)
        return Response({'message': '시험 제출 완료'})

    @action(detail=True, methods=['get'], url_path='result')
    def result(self, request, pk=None, session_pk=None):
        # 결과 조회 로직 (예시)
        result = get_object_or_404(ExamResult, session__pk=session_pk, session__user=request.user)
        serializer = ExamResultSerializer(result)
        return Response(serializer.data)
# 필요시 관리자용 TestSessionViewSet, ExamResultViewSet 추가
class AdminTestSessionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TestSession.objects.all()
    serializer_class = TestSessionSerializer
    permission_classes = [IsAdminUser]

class AdminExamResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExamResult.objects.all()
    serializer_class = ExamResultSerializer
    permission_classes = [IsAdminUser]
