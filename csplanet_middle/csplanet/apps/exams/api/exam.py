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

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all().order_by('-start_datetime')
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]
    def get_permissions(self):
        if self.action in ['list', 'create', 'print', 'partial_update', 'by_exam']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        
    @action(detail=True, methods=['get'], url_path='print')
    def print(self, request, pk=None):
        exam = self.get_object()
        serializer = self.get_serializer(exam)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='admin/sessions')
    def by_exam(self, request):
        exam_pk = request.query_params.get('exam_pk')
        exam = get_object_or_404(Exam, pk=exam_pk)
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
        return Response(data)

    @action(detail=False, methods=['get'])
    def user_exams(self, request):
        now = timezone.now()
        exams = Exam.objects.all().order_by('-start_datetime')
        completed_sessions = TestSession.objects.filter(
            user=request.user, completed_at__isnull=False, exam__in=exams)
        results = {r.session.exam_id: r for r in ExamResult.objects.filter(session__in=completed_sessions)}
        data = []
        for exam in exams:
            data.append({
                'exam': ExamSerializer(exam).data,
                'user_result': ExamResultSerializer(results.get(exam.pk)).data if exam.pk in results else None
            })
        return Response(data)

    @action(detail=True, methods=['get'], url_path='questions')
    def questions(self, request, pk=None):
        exam = self.get_object()
        questions = exam.questions.all()
        serializer = ExamQuestionSerializer(questions, many=True)
        return Response(serializer.data)

class TestSessionViewSet(viewsets.ModelViewSet):
    queryset = TestSession.objects.all()
    serializer_class = TestSessionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='exams/(?P<exam_pk>[^/.]+)/sessions')
    def take(self, request, exam_pk=None):
        exam = get_object_or_404(Exam, pk=exam_pk)
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

    @action(detail=False, methods=['patch'], url_path='exams/(?P<exam_pk>[^/.]+)/sessions/(?P<session_pk>[^/.]+)/answers')
    def save_answers(self, request, exam_pk=None, session_pk=None):
        session = get_object_or_404(TestSession, pk=session_pk, user=request.user, completed_at__isnull=True)
        session.answers.all().delete()
        for q in session.exam.questions.all():
            answer_data = request.data.get(str(q.id))
            if not answer_data:
                continue
            answer = UserAnswer(session=session, question=q)
            if q.type == 'objective':
                answer.selected_choice_id = answer_data.get('selected_choice')
                correct = bool(answer.selected_choice_id and q.problem.objectiveproblem.choices.filter(id=answer.selected_choice_id, is_correct=True).exists())
                answer.is_correct = correct
                answer.score = q.weight if correct else 0
            else:
                answer.text_answer = answer_data.get('text_answer')
                answer = self._grade_subjective(q, answer)
            answer.save()
        return Response({'message': '답안 저장 완료'})

    @action(detail=False, methods=['post'], url_path='exams/(?P<exam_pk>[^/.]+)/sessions/(?P<session_pk>[^/.]+)/submit')
    def submit(self, request, exam_pk=None, session_pk=None):
        session = get_object_or_404(TestSession, pk=session_pk, user=request.user, completed_at__isnull=True)
        session.answers.all().delete()
        for q in session.exam.questions.all():
            answer_data = request.data.get(str(q.id))
            if not answer_data:
                continue
            answer = UserAnswer(session=session, question=q)
            if q.type == 'objective':
                answer.selected_choice_id = answer_data.get('selected_choice')
                correct = bool(answer.selected_choice_id and q.problem.objectiveproblem.choices.filter(id=answer.selected_choice_id, is_correct=True).exists())
                answer.is_correct = correct
                answer.score = q.weight if correct else 0
            else:
                answer.text_answer = answer_data.get('text_answer')
                answer = self._grade_subjective(q, answer)
            answer.save()
        total = session.answers.aggregate(total=Sum('score'))['total'] or 0
        ExamResult.objects.update_or_create(session=session, defaults={'total_score': total, 'status': '제출 완료'})
        session.completed_at = timezone.now()
        session.save()
        return Response({'message': '제출 완료', 'session_pk': session.pk})

    def _grade_subjective(self, q, answer):
        # 주관식 채점 예시: 키워드 포함 여부로 간단히 처리 (실제로는 더 복잡할 수 있음)
        text = answer.text_answer or ''
        if q.type == 'subjective' and hasattr(q.problem, 'subjectiveproblem'):
            keywords = q.problem.subjectiveproblem.keywords.all()
            matched = any(keyword.keyword in text for keyword in keywords)
            answer.is_correct = matched
            answer.score = q.weight if matched else 0
        return answer

class ExamResultViewSet(viewsets.ModelViewSet):
    queryset = ExamResult.objects.all()
    serializer_class = ExamResultSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='exams/(?P<exam_pk>[^/.]+)/sessions/(?P<session_pk>[^/.]+)/result')
    def by_session(self, request, exam_pk=None, session_pk=None):
        lookup = {'session__pk': session_pk}
        if not request.user.is_staff:
            lookup['session__user'] = request.user
        result = get_object_or_404(ExamResult, **lookup)
        serializer = self.get_serializer(result)
        return Response(serializer.data)
