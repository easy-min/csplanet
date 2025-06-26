from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.exam import ExamViewSet, TestSessionViewSet, ExamResultViewSet

app_name = 'exams'

# ViewSet 등록 (DefaultRouter 사용)
router = DefaultRouter()
router.register(r'admin/exams', ExamViewSet, basename='admin-exam')
router.register(r'test-sessions', TestSessionViewSet, basename='test-session')
router.register(r'exam-results', ExamResultViewSet, basename='exam-result')

# 커스텀 액션들은 ViewSet의 @action 데코레이터로 이미 url_path가 지정되어 있음
# 하지만, 아래처럼 직접 path로 연결하면 엔드포인트명이 더 명확해짐
# 단, ViewSet의 @action 데코레이터의 url_path와 겹치지 않게 주의

# 관리자용 URL (staff 전용) - ViewSet의 @action으로 이미 처리됨
# 필요하다면 아래처럼 직접 연결도 가능 (예시)
# admin_patterns = [
#     path('admin/exams/<int:pk>/print/', ExamViewSet.as_view({'get': 'print'}), name='exam-print'),
#     path('admin/exams/<int:exam_pk>/sessions/', ExamViewSet.as_view({'get': 'by_exam'}), name='session-list'),
# ]

# 사용자용 URL - ViewSet의 @action으로 이미 처리됨
# 필요하다면 아래처럼 직접 연결도 가능 (예시)
# user_patterns = [
#     path('exams/', ExamViewSet.as_view({'get': 'user_exams'}), name='user-exams'),
#     path('exams/<int:pk>/questions/', ExamViewSet.as_view({'get': 'questions'}), name='exam-questions'),
# ]

# 실제로는 router.urls만 사용해도 되지만,
# 커스텀 액션의 엔드포인트명이 API 문서와 완전히 일치하도록 하려면
# 아래처럼 path를 직접 추가할 수 있음
custom_urlpatterns = [
    # 관리자용
    path('admin/exams/<int:pk>/print/', ExamViewSet.as_view({'get': 'print'}), name='exam-print'),
    path('admin/exams/<int:exam_pk>/sessions/', ExamViewSet.as_view({'get': 'by_exam'}), name='session-list'),
    # 사용자용
    path('exams/', ExamViewSet.as_view({'get': 'user_exams'}), name='user-exams'),
    path('exams/<int:pk>/questions/', ExamViewSet.as_view({'get': 'questions'}), name='exam-questions'),
    # 시험 응시/답안/제출/결과 조회는 TestSessionViewSet, ExamResultViewSet의 @action으로 처리됨
    # 필요하다면 아래처럼 직접 연결도 가능
    path('exams/<int:exam_pk>/sessions/', TestSessionViewSet.as_view({'post': 'take'}), name='exam-take'),
    path('exams/<int:exam_pk>/sessions/<int:session_pk>/answers/', TestSessionViewSet.as_view({'patch': 'save_answers'}), name='exam-answers'),
    path('exams/<int:exam_pk>/sessions/<int:session_pk>/submit/', TestSessionViewSet.as_view({'post': 'submit'}), name='exam-submit'),
    path('exams/<int:exam_pk>/sessions/<int:session_pk>/result/', ExamResultViewSet.as_view({'get': 'by_session'}), name='exam-result'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('', include(custom_urlpatterns)),
]
