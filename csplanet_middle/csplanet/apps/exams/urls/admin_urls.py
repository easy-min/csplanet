# csplanet/apps/exams/urls/user_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..api.user_exam_view import ExamViewSet, UserSessionViewSet

app_name = 'user-exams'

router = DefaultRouter()
# 사용자용 ExamViewSet 등록
router.register(r'exams', ExamViewSet, basename='exam')

urlpatterns = [
    # 1) /api/exams/                     - 시험 목록 & 상세 조회
    #    /api/exams/{pk}/questions/      - 문제 목록 조회
    path('', include(router.urls)),

    # 2) POST   /api/exams/{pk}/sessions/               - 시험 응시 세션 생성
    #    GET    /api/exams/{pk}/sessions/               - 사용자의 세션 목록 조회 (선택)
    path(
        'exams/<int:pk>/sessions/',
        UserSessionViewSet.as_view({'post': 'create', 'get': 'list'}),
        name='session-list-create'
    ),

    # 3) GET    /api/exams/{pk}/sessions/{session_pk}/  - 세션 상세 조회
    path(
        'exams/<int:pk>/sessions/<int:session_pk>/',
        UserSessionViewSet.as_view({'get': 'retrieve'}),
        name='session-detail'
    ),

    # 4) PATCH  /api/exams/{pk}/sessions/{session_pk}/answers/  - 답안 저장
    path(
        'exams/<int:pk>/sessions/<int:session_pk>/answers/',
        UserSessionViewSet.as_view({'patch': 'save_answers'}),
        name='session-save-answers'
    ),

    # 5) POST   /api/exams/{pk}/sessions/{session_pk}/submit/   - 시험 제출
    path(
        'exams/<int:pk>/sessions/<int:session_pk>/submit/',
        UserSessionViewSet.as_view({'post': 'submit'}),
        name='session-submit'
    ),

    # 6) GET    /api/exams/{pk}/sessions/{session_pk}/result/   - 시험 결과 조회
    path(
        'exams/<int:pk>/sessions/<int:session_pk>/result/',
        UserSessionViewSet.as_view({'get': 'result'}),
        name='session-result'
    ),
]
