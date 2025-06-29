import logging
import sys
import traceback
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from django.core.exceptions import ValidationError as DjangoValidationError

from csplanet.csplanet_middle.csplanet.apps.exams.serializers.serializers import ExamQuestionDetailSerializer
from ..models import Exam, ExamQuestion, TestSession, ExamResult, UserAnswer
from ..serializers import ExamSerializer, ExamQuestionSerializer, TestSessionSerializer, ExamResultSerializer
from csplanet.apps.problems.models import ObjectiveProblem, SubjectiveProblem
from .exception_handlers import log_api_call, log_api_success

# 로거 설정
logger = logging.getLogger(__name__)

class AdminExamViewSet(viewsets.ModelViewSet):
    """
    관리자용 시험 관리 ViewSet
    모든 CRUD 작업과 추가 액션들을 포함하며, 포괄적인 로깅과 예외 처리 제공
    """
    queryset = Exam.objects.all().order_by('-start_datetime')
    serializer_class = ExamSerializer
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        """시험 목록 조회"""
        try:
            log_api_call(
                view_name=self.__class__.__name__,
                method_name='list',
                user=request.user,
                extra_info=f"Query params: {dict(request.query_params)}"
            )
            
            response = super().list(request, *args, **kwargs)
            
            log_api_success(
                view_name=self.__class__.__name__,
                method_name='list',
                user=request.user,
                response_info=f"Returned {len(response.data)} exams"
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Error in {self.__class__.__name__}.list: {str(e)} | "
                f"User: {request.user} | Traceback: {traceback.format_exc()}"
            )
            return Response(
                {'error': 'Failed to retrieve exam list', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        """새 시험 생성"""
        try:
            log_api_call(
                view_name=self.__class__.__name__,
                method_name='create',
                user=request.user,
                request_data=request.data
            )
            
            response = super().create(request, *args, **kwargs)
            
            log_api_success(
                view_name=self.__class__.__name__,
                method_name='create',
                user=request.user,
                response_info=f"Created exam with ID: {response.data.get('id')}"
            )
            
            return response
            
        except DjangoValidationError as e:
            logger.warning(
                f"Validation error in {self.__class__.__name__}.create: {str(e)} | "
                f"User: {request.user} | Data: {request.data}"
            )
            return Response(
                {'error': 'Validation failed', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(
                f"Error in {self.__class__.__name__}.create: {str(e)} | "
                f"User: {request.user} | Data: {request.data} | Traceback: {traceback.format_exc()}"
            )
            return Response(
                {'error': 'Failed to create exam', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        """단일 시험 조회"""
        try:
            exam_id = kwargs.get('pk')
            log_api_call(
                view_name=self.__class__.__name__,
                method_name='retrieve',
                user=request.user,
                extra_info=f"Exam ID: {exam_id}"
            )
            
            response = super().retrieve(request, *args, **kwargs)
            
            log_api_success(
                view_name=self.__class__.__name__,
                method_name='retrieve',
                user=request.user,
                response_info=f"Retrieved exam: {response.data.get('title', 'N/A')}"
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Error in {self.__class__.__name__}.retrieve: {str(e)} | "
                f"User: {request.user} | Exam ID: {kwargs.get('pk')} | Traceback: {traceback.format_exc()}"
            )
            return Response(
                {'error': 'Failed to retrieve exam', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        """시험 전체 수정"""
        try:
            exam_id = kwargs.get('pk')
            log_api_call(
                view_name=self.__class__.__name__,
                method_name='update',
                user=request.user,
                request_data=request.data,
                extra_info=f"Exam ID: {exam_id}"
            )
            
            response = super().update(request, *args, **kwargs)
            
            log_api_success(
                view_name=self.__class__.__name__,
                method_name='update',
                user=request.user,
                response_info=f"Updated exam: {response.data.get('title', 'N/A')}"
            )
            
            return response
            
        except DjangoValidationError as e:
            logger.warning(
                f"Validation error in {self.__class__.__name__}.update: {str(e)} | "
                f"User: {request.user} | Exam ID: {kwargs.get('pk')} | Data: {request.data}"
            )
            return Response(
                {'error': 'Validation failed', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(
                f"Error in {self.__class__.__name__}.update: {str(e)} | "
                f"User: {request.user} | Exam ID: {kwargs.get('pk')} | Data: {request.data} | "
                f"Traceback: {traceback.format_exc()}"
            )
            return Response(
                {'error': 'Failed to update exam', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def partial_update(self, request, *args, **kwargs):
        """시험 부분 수정"""
        try:
            exam_id = kwargs.get('pk')
            log_api_call(
                view_name=self.__class__.__name__,
                method_name='partial_update',
                user=request.user,
                request_data=request.data,
                extra_info=f"Exam ID: {exam_id}"
            )
            
            response = super().partial_update(request, *args, **kwargs)
            
            log_api_success(
                view_name=self.__class__.__name__,
                method_name='partial_update',
                user=request.user,
                response_info=f"Partially updated exam: {response.data.get('title', 'N/A')}"
            )
            
            return response
            
        except DjangoValidationError as e:
            logger.warning(
                f"Validation error in {self.__class__.__name__}.partial_update: {str(e)} | "
                f"User: {request.user} | Exam ID: {kwargs.get('pk')} | Data: {request.data}"
            )
            return Response(
                {'error': 'Validation failed', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(
                f"Error in {self.__class__.__name__}.partial_update: {str(e)} | "
                f"User: {request.user} | Exam ID: {kwargs.get('pk')} | Data: {request.data} | "
                f"Traceback: {traceback.format_exc()}"
            )
            return Response(
                {'error': 'Failed to partially update exam', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, *args, **kwargs):
        """시험 삭제"""
        try:
            exam_id = kwargs.get('pk')
            exam = self.get_object()
            exam_title = exam.title
            
            log_api_call(
                view_name=self.__class__.__name__,
                method_name='destroy',
                user=request.user,
                extra_info=f"Exam ID: {exam_id}, Title: {exam_title}"
            )
            
            response = super().destroy(request, *args, **kwargs)
            
            log_api_success(
                view_name=self.__class__.__name__,
                method_name='destroy',
                user=request.user,
                response_info=f"Deleted exam: {exam_title}"
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Error in {self.__class__.__name__}.destroy: {str(e)} | "
                f"User: {request.user} | Exam ID: {kwargs.get('pk')} | Traceback: {traceback.format_exc()}"
            )
            return Response(
                {'error': 'Failed to delete exam', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'], url_path='print')
    def print(self, request, pk=None):
        """시험 인쇄용 데이터 조회"""
        try:
            log_api_call(
                view_name=self.__class__.__name__,
                method_name='print',
                user=request.user,
                extra_info=f"Exam ID: {pk}"
            )
            
            exam = self.get_object()
            serializer = self.get_serializer(exam)
            
            log_api_success(
                view_name=self.__class__.__name__,
                method_name='print',
                user=request.user,
                response_info=f"Print data for exam: {exam.title}"
            )
            
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(
                f"Error in {self.__class__.__name__}.print: {str(e)} | "
                f"User: {request.user} | Exam ID: {pk} | Traceback: {traceback.format_exc()}"
            )
            return Response(
                {'error': 'Failed to get print data', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'], url_path='sessions')
    def sessions(self, request, pk=None):
        """특정 시험의 모든 세션 조회"""
        try:
            log_api_call(
                view_name=self.__class__.__name__,
                method_name='sessions',
                user=request.user,
                extra_info=f"Exam ID: {pk}"
            )
            
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
                except Exception as session_error:
                    logger.warning(
                        f"Error processing session {sess.id}: {str(session_error)} | "
                        f"User: {request.user}"
                    )
                    data.append({
                        'session': TestSessionSerializer(sess).data,
                        'score': None,
                        'status': '오류',
                    })
            
            log_api_success(
                view_name=self.__class__.__name__,
                method_name='sessions',
                user=request.user,
                response_info=f"Retrieved {len(data)} sessions for exam: {exam.title}"
            )
            
            return Response(data)
            
        except Exception as e:
            logger.error(
                f"Error in {self.__class__.__name__}.sessions: {str(e)} | "
                f"User: {request.user} | Exam ID: {pk} | Traceback: {traceback.format_exc()}"
            )
            return Response(
                {'error': 'Failed to retrieve sessions', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'], url_path='results')
    def results(self, request, pk=None):
        """특정 시험의 모든 결과 조회"""
        try:
            log_api_call(
                view_name=self.__class__.__name__,
                method_name='results',
                user=request.user,
                extra_info=f"Exam ID: {pk}"
            )
            
            exam = self.get_object()
            results = ExamResult.objects.filter(session__exam=exam).select_related('session__user')
            serializer = ExamResultSerializer(results, many=True)
            
            log_api_success(
                view_name=self.__class__.__name__,
                method_name='results',
                user=request.user,
                response_info=f"Retrieved {len(results)} results for exam: {exam.title}"
            )
            
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(
                f"Error in {self.__class__.__name__}.results: {str(e)} | "
                f"User: {request.user} | Exam ID: {pk} | Traceback: {traceback.format_exc()}"
            )
            return Response(
                {'error': 'Failed to retrieve results', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    일반 사용자용 시험 조회 ViewSet
    시험 목록 조회, 상세 조회, 문제 조회 기능 제공
    """
    queryset = Exam.objects.all().order_by('-start_datetime')
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """사용자가 접근 가능한 시험 목록 조회"""
        try:
            log_api_call(
                view_name=self.__class__.__name__,
                method_name='list',
                user=request.user,
                extra_info=f"Query params: {dict(request.query_params)}"
            )
            
            # 현재 시간 기준으로 활성 시험만 필터링 (선택사항)
            now = timezone.now()
            active_exams = self.get_queryset().filter(
                start_datetime__lte=now,
                end_datetime__gte=now
            )
            
            page = self.paginate_queryset(active_exams)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                log_api_success(
                    view_name=self.__class__.__name__,
                    method_name='list',
                    user=request.user,
                    response_info=f"Returned paginated {len(serializer.data)} active exams"
                )
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(active_exams, many=True)
            
            log_api_success(
                view_name=self.__class__.__name__,
                method_name='list',
                user=request.user,
                response_info=f"Returned {len(serializer.data)} active exams"
            )
            
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(
                f"Error in {self.__class__.__name__}.list: {str(e)} | "
                f"User: {request.user} | Traceback: {traceback.format_exc()}"
            )
            return Response(
                {'error': 'Failed to retrieve exam list', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        """특정 시험 상세 정보 조회"""
        try:
            exam_id = kwargs.get('pk')
            log_api_call(
                view_name=self.__class__.__name__,
                method_name='retrieve',
                user=request.user,
                extra_info=f"Exam ID: {exam_id}"
            )
            
            exam = self.get_object()
            
            # 시험 접근 권한 확인 (예: 시험 기간 내인지 확인)
            now = timezone.now()
            if not (exam.start_datetime <= now <= exam.end_datetime):
                logger.warning(
                    f"User {request.user} tried to access exam {exam_id} outside allowed time period"
                )
                return Response(
                    {'error': 'Exam not accessible', 'detail': 'This exam is not currently available'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = self.get_serializer(exam)
            
            log_api_success(
                view_name=self.__class__.__name__,
                method_name='retrieve',
                user=request.user,
                response_info=f"Retrieved exam: {exam.title}"
            )
            
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(
                f"Error in {self.__class__.__name__}.retrieve: {str(e)} | "
                f"User: {request.user} | Exam ID: {kwargs.get('pk')} | Traceback: {traceback.format_exc()}"
            )
            return Response(
                {'error': 'Failed to retrieve exam', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'], url_path='questions')
    def questions(self, request, pk=None):
        """특정 시험의 문제 목록 조회"""
        try:
            log_api_call(
                view_name=self.__class__.__name__,
                method_name='questions',
                user=request.user,
                extra_info=f"Exam ID: {pk}"
            )
            
            exam = self.get_object()
            
            # 시험 접근 권한 확인
            now = timezone.now()
            if not (exam.start_datetime <= now <= exam.end_datetime):
                logger.warning(
                    f"User {request.user} tried to access questions for exam {pk} outside allowed time period"
                )
                return Response(
                    {'error': 'Questions not accessible', 'detail': 'This exam is not currently available'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # 사용자가 이미 시험을 완료했는지 확인
            completed_session = TestSession.objects.filter(
                exam=exam,
                user=request.user,
                completed_at__isnull=False
            ).first()
            
            if completed_session:
                logger.info(
                    f"User {request.user} tried to access questions for already completed exam {pk}"
                )
                return Response(
                    {'error': 'Already completed', 'detail': 'You have already completed this exam'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            questions = exam.questions.all().order_by('order')
            serializer = ExamQuestionSerializer(questions, many=True)
            
            log_api_success(
                view_name=self.__class__.__name__,
                method_name='questions',
                user=request.user,
                response_info=f"Retrieved {len(questions)} questions for exam: {exam.title}"
            )
            
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(
                f"Error in {self.__class__.__name__}.questions: {str(e)} | "
                f"User: {request.user} | Exam ID: {pk} | Traceback: {traceback.format_exc()}"
            )
            return Response(
                {'error': 'Failed to retrieve questions', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserSessionViewSet(viewsets.ViewSet):
    """
    사용자 시험 세션 관리 ViewSet
    시험 시작, 답안 저장, 시험 제출, 결과 조회 등의 기능 제공
    """
    permission_classes = [IsAuthenticated]

    def create(self, request, pk=None):
        """새로운 시험 세션 생성 (시험 시작)"""
        try:
            log_api_call(
                view_name=self.__class__.__name__,
                method_name='create',
                user=request.user,
                extra_info=f"Exam ID: {pk}"
            )
            
            exam = get_object_or_404(Exam, pk=pk)
            now = timezone.now()
            
            # 시험 기간 확인
            if not (exam.start_datetime <= now <= exam.end_datetime):
                logger.warning(
                    f"User {request.user} tried to start exam {pk} outside allowed time period"
                )
                return Response(
                    {'message': '시험 기간이 아닙니다.', 'current_time': now, 'exam_period': {
                        'start': exam.start_datetime,
                        'end': exam.end_datetime
                    }},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # 이미 완료된 시험인지 확인
            completed = TestSession.objects.filter(
                exam=exam,
                user=request.user,
                completed_at__isnull=False
            ).first()
            
            if completed:
                logger.info(
                    f"User {request.user} tried to restart already completed exam {pk}"
                )
                return Response({
                    'message': '이미 응시한 시험입니다.',
                    'completed_session_pk': completed.pk,
                    'completed_at': completed.completed_at
                })
            
            # 진행 중인 세션 확인 또는 새 세션 생성
            session, created = TestSession.objects.get_or_create(
                exam=exam,
                user=request.user,
                completed_at__isnull=True,
                defaults={'started_at': now}
            )
            
            questions = exam.questions.all().order_by('order')
            serializer = ExamQuestionSerializer(questions, many=True)
            
            session_info = {
                'session': session.pk,
                'questions': serializer.data,
                'exam_title': exam.title,
                'started_at': session.started_at,
                'created_new_session': created
            }
            
            log_api_success(
                view_name=self.__class__.__name__,
                method_name='create',
                user=request.user,
                response_info=f"{'Created new' if created else 'Retrieved existing'} session {session.pk} for exam: {exam.title}"
            )
            
            return Response(session_info)
            
        except Exception as e:
            logger.error(
                f"Error in {self.__class__.__name__}.create: {str(e)} | "
                f"User: {request.user} | Exam ID: {pk} | Traceback: {traceback.format_exc()}"
            )
            return Response(
                {'error': 'Failed to create session', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None, session_pk=None):
        """특정 세션 정보 조회"""
        try:
            log_api_call(
                view_name=self.__class__.__name__,
                method_name='retrieve',
                user=request.user,
                extra_info=f"Session ID: {session_pk}"
            )
            
            session = get_object_or_404(TestSession, pk=session_pk, user=request.user)
            serializer = TestSessionSerializer(session)
            
            log_api_success(
                view_name=self.__class__.__name__,
                method_name='retrieve',
                user=request.user,
                response_info=f"Retrieved session {session_pk} for exam: {session.exam.title}"
            )
            
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(
                f"Error in {self.__class__.__name__}.retrieve: {str(e)} | "
                f"User: {request.user} | Session ID: {session_pk} | Traceback: {traceback.format_exc()}"
            )
            return Response(
                {'error': 'Failed to retrieve session', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @action(detail=True, methods=['get'], url_path='questions')
    def questions(self, request, pk=None, session_pk=None):
        """
        GET /api/exams/{pk}/sessions/{session_pk}/questions/
        → 객관식·주관식 문제를 섞은 리스트로 반환
        """
        session = get_object_or_404(TestSession, pk=session_pk, user=request.user)
        qs = session.exam.questions.all().order_by('order')
        serializer = ExamQuestionDetailSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='answers')
    def save_answers(self, request, pk=None, session_pk=None):
        """답안 저장"""
        try:
            log_api_call(
                view_name=self.__class__.__name__,
                method_name='save_answers',
                user=request.user,
                request_data=request.data,
                extra_info=f"Session ID: {session_pk}"
            )
            
            session = get_object_or_404(TestSession, pk=session_pk, user=request.user)
            
            # 세션이 완료되었는지 확인
            if session.completed_at:
                logger.warning(
                    f"User {request.user} tried to save answers for completed session {session_pk}"
                )
                return Response(
                    {'error': 'Session completed', 'detail': 'Cannot save answers for completed session'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # 시험 시간 제한 확인
            remaining_secs = (session.exam.end_datetime - timezone.now()).total_seconds()
            if remaining_secs <= 0:
                return Response(
                    {'error': '시험 종료', 'detail': '시험 시간이 지나 답안을 저장할 수 없습니다.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # 답안 저장 로직 구현
            answers = request.data.get('answers', [])
            saved_count = 0
            
            for answer_data in answers:
                try:
                    question_id = answer_data.get('question_id')
                    answer_text = answer_data.get('answer')
                    
                    if question_id and answer_text is not None:
                        question = get_object_or_404(ExamQuestion, id=question_id, exam=session.exam)
                        
                        user_answer, created = UserAnswer.objects.update_or_create(
                            session=session,
                            question=question,
                            defaults={'answer': answer_text, 'answered_at': timezone.now()}
                        )
                        saved_count += 1
                        
                except Exception as answer_error:
                    logger.warning(
                        f"Failed to save individual answer: {str(answer_error)} | "
                        f"User: {request.user} | Session: {session_pk} | Answer data: {answer_data}"
                    )
                    continue
            
            log_api_success(
                view_name=self.__class__.__name__,
                method_name='save_answers',
                user=request.user,
                response_info=f"Saved {saved_count} answers for session {session_pk}"
            )
            
            return Response({
                'message': '답안 저장 완료',
                'saved_count': saved_count,
                'total_answers': len(answers)
            })
            
        except Exception as e:
            logger.error(
                f"Error in {self.__class__.__name__}.save_answers: {str(e)} | "
                f"User: {request.user} | Session ID: {session_pk} | Data: {request.data} | "
                f"Traceback: {traceback.format_exc()}"
            )
            return Response(
                {'error': 'Failed to save answers', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None, session_pk=None):
        """시험 제출"""
        try:
            log_api_call(
                view_name=self.__class__.__name__,
                method_name='submit',
                user=request.user,
                extra_info=f"Session ID: {session_pk}"
            )
            
            session = get_object_or_404(TestSession, pk=session_pk, user=request.user)
            
            # 이미 제출된 세션인지 확인
            if session.completed_at:
                logger.warning(
                    f"User {request.user} tried to resubmit already completed session {session_pk}"
                )
                return Response(
                    {'error': 'Already submitted', 'detail': 'This session has already been submitted'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # 세션 완료 처리
            session.completed_at = timezone.now()
            session.save()
            
            # 채점 로직 구현 (간단한 예시)
            user_answers = UserAnswer.objects.filter(session=session)
            total_score = 0
            max_score = 0
            
            for user_answer in user_answers:
                question = user_answer.question
                max_score += question.points
                
                # 객관식 문제 채점 (예시)
                if hasattr(question, 'objective_problem'):
                    if user_answer.answer == question.objective_problem.correct_answer:
                        total_score += question.points
                
                # 주관식 문제는 수동 채점 필요
            
            # 결과 저장
            exam_result, created = ExamResult.objects.update_or_create(
                session=session,
                defaults={
                    'total_score': total_score,
                    'max_score': max_score,
                    'status': 'completed',
                    'submitted_at': session.completed_at
                }
            )
            
            log_api_success(
                view_name=self.__class__.__name__,
                method_name='submit',
                user=request.user,
                response_info=f"Submitted session {session_pk} with score {total_score}/{max_score}"
            )
            
            return Response({
                'message': '시험 제출 완료',
                'session_id': session.pk,
                'total_score': total_score,
                'max_score': max_score,
                'submitted_at': session.completed_at
            })
            
        except Exception as e:
            logger.error(
                f"Error in {self.__class__.__name__}.submit: {str(e)} | "
                f"User: {request.user} | Session ID: {session_pk} | Traceback: {traceback.format_exc()}"
            )
            return Response(
                {'error': 'Failed to submit exam', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'], url_path='result')
    def result(self, request, pk=None, session_pk=None):
        """시험 결과 조회"""
        try:
            log_api_call(
                view_name=self.__class__.__name__,
                method_name='result',
                user=request.user,
                extra_info=f"Session ID: {session_pk}"
            )
            
            result = get_object_or_404(
                ExamResult,
                session__pk=session_pk,
                session__user=request.user
            )
            
            serializer = ExamResultSerializer(result)
            
            log_api_success(
                view_name=self.__class__.__name__,
                method_name='result',
                user=request.user,
                response_info=f"Retrieved result for session {session_pk}: {result.total_score}/{result.max_score}"
            )
            
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(
                f"Error in {self.__class__.__name__}.result: {str(e)} | "
                f"User: {request.user} | Session ID: {session_pk} | Traceback: {traceback.format_exc()}"
            )
            return Response(
                {'error': 'Failed to retrieve result', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminTestSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    관리자용 테스트 세션 조회 ViewSet
    """
    queryset = TestSession.objects.all().select_related('user', 'exam').order_by('-started_at')
    serializer_class = TestSessionSerializer
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        """모든 테스트 세션 목록 조회"""
        try:
            log_api_call(
                view_name=self.__class__.__name__,
                method_name='list',
                user=request.user,
                extra_info=f"Query params: {dict(request.query_params)}"
            )
            
            response = super().list(request, *args, **kwargs)
            
            log_api_success(
                view_name=self.__class__.__name__,
                method_name='list',
                user=request.user,
                response_info=f"Retrieved {len(response.data)} test sessions"
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Error in {self.__class__.__name__}.list: {str(e)} | "
                f"User: {request.user} | Traceback: {traceback.format_exc()}"
            )
            return Response(
                {'error': 'Failed to retrieve test sessions', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        """특정 테스트 세션 상세 조회"""
        try:
            session_id = kwargs.get('pk')
            log_api_call(
                view_name=self.__class__.__name__,
                method_name='retrieve',
                user=request.user,
                extra_info=f"Session ID: {session_id}"
            )
            
            response = super().retrieve(request, *args, **kwargs)
            
            log_api_success(
                view_name=self.__class__.__name__,
                method_name='retrieve',
                user=request.user,
                response_info=f"Retrieved session details for ID: {session_id}"
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Error in {self.__class__.__name__}.retrieve: {str(e)} | "
                f"User: {request.user} | Session ID: {kwargs.get('pk')} | Traceback: {traceback.format_exc()}"
            )
            return Response(
                {'error': 'Failed to retrieve test session', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminExamResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    관리자용 시험 결과 조회 ViewSet
    """
    queryset = ExamResult.objects.all().select_related('session__user', 'session__exam').order_by('-session__completed_at')
    serializer_class = ExamResultSerializer
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        """모든 시험 결과 목록 조회"""
        try:
            log_api_call(
                view_name=self.__class__.__name__,
                method_name='list',
                user=request.user,
                extra_info=f"Query params: {dict(request.query_params)}"
            )
            
            response = super().list(request, *args, **kwargs)
            
            log_api_success(
                view_name=self.__class__.__name__,
                method_name='list',
                user=request.user,
                response_info=f"Retrieved {len(response.data)} exam results"
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Error in {self.__class__.__name__}.list: {str(e)} | "
                f"User: {request.user} | Traceback: {traceback.format_exc()}"
            )
            return Response(
                {'error': 'Failed to retrieve exam results', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        """특정 시험 결과 상세 조회"""
        try:
            result_id = kwargs.get('pk')
            log_api_call(
                view_name=self.__class__.__name__,
                method_name='retrieve',
                user=request.user,
                extra_info=f"Result ID: {result_id}"
            )
            
            response = super().retrieve(request, *args, **kwargs)
            
            log_api_success(
                view_name=self.__class__.__name__,
                method_name='retrieve',
                user=request.user,
                response_info=f"Retrieved result details for ID: {result_id}"
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Error in {self.__class__.__name__}.retrieve: {str(e)} | "
                f"User: {request.user} | Result ID: {kwargs.get('pk')} | Traceback: {traceback.format_exc()}"
            )
            return Response(
                {'error': 'Failed to retrieve exam result', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
