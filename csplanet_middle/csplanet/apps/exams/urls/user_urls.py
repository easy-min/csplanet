# csplanet/apps/exams/urls/user_urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..api.user_exam_view import ExamViewSet, UserSessionViewSet

app_name = 'user-exams'

router = DefaultRouter()
router.register(r'exams', ExamViewSet, basename='exam')

urlpatterns = [
    # 1) ExamViewSet: list and detail (+ questions action)
    path('', include(router.urls)),

    # 2) 시험 시작 (새 세션 생성)
    #    POST /api/exams/<exam_pk>/sessions/
    path(
        '<int:pk>/sessions/',
        UserSessionViewSet.as_view({'post': 'create'}),
        name='session-start'
    ),

    # 3) 세션 상세 조회
    #    GET /api/exams/<exam_pk>/sessions/<session_pk>/
    path(
        '<int:pk>/sessions/<int:session_pk>/',
        UserSessionViewSet.as_view({'get': 'retrieve'}),
        name='session-detail'
    ),

    # 4) 답안 저장
    #    PATCH /api/exams/<exam_pk>/sessions/<session_pk>/answers/
    path(
        '<int:pk>/sessions/<int:session_pk>/answers/',
        UserSessionViewSet.as_view({'patch': 'save_answers'}),
        name='session-save-answers'
    ),

    # 5) 시험 제출
    #    POST /api/exams/<exam_pk>/sessions/<session_pk>/submit/
    path(
        '<int:pk>/sessions/<int:session_pk>/submit/',
        UserSessionViewSet.as_view({'post': 'submit'}),
        name='session-submit'
    ),

    # 6) 결과 조회
    #    GET /api/exams/<exam_pk>/sessions/<session_pk>/result/
    path(
        '<int:pk>/sessions/<int:session_pk>/result/',
        UserSessionViewSet.as_view({'get': 'result'}),
        name='session-result'
    ),
]
