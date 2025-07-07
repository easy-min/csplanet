from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from ..serializers import (
    ExamSerializer,
    ExamResultSerializer,
    TestSessionSerializer,
)
from ..models import Exam, TestSession, ExamResult


class AdminExamViewSet(viewsets.ModelViewSet):
    """
    관리자용 시험 CRUD 및 관련 액션
    """
    queryset = Exam.objects.all().order_by('-start_datetime')
    serializer_class = ExamSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['get'], url_path='sessions')
    def sessions(self, request, pk=None):
        exam = self.get_object()
        sessions = TestSession.objects.filter(exam=exam)
        serializer = TestSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='results')
    def results(self, request, pk=None):
        exam = self.get_object()
        results = ExamResult.objects.filter(exam=exam)
        serializer = ExamResultSerializer(results, many=True)
        return Response(serializer.data)
