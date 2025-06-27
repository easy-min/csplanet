# csplanet/apps/exams/urls/admin_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..api.exam import AdminExamViewSet, AdminTestSessionViewSet, AdminExamResultViewSet  # 또는 절대 경로
app_name = 'user-exams'

admin_router = DefaultRouter()
admin_router.register(r'exams', AdminExamViewSet, basename='admin-exam')

urlpatterns = [
    path('', include(admin_router.urls)),
    path('sessions/', AdminTestSessionViewSet.as_view({'get': 'list'}), name='admin-sessions'),
    path('sessions/<int:pk>/', AdminTestSessionViewSet.as_view({'get': 'retrieve'}), name='admin-session-detail'),
    path('results/', AdminExamResultViewSet.as_view({'get': 'list'}), name='admin-results'),
    path('results/<int:pk>/', AdminExamResultViewSet.as_view({'get': 'retrieve'}), name='admin-result-detail'),
]
