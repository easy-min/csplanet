# apps/problems/views/objective_views.py

from rest_framework import viewsets
from ..models.objective_problem import ObjectiveProblem
from ..serializers.objective_serializers import ObjectiveProblemSerializer
from ..models.topic import Topic
from ..models.chapter import Chapter
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from ..serializers.topic_serializers import TopicSerializer
from ..serializers.chapter_serializers import ChapterSerializer
from rest_framework import generics

class ObjectiveProblemViewSet(viewsets.ModelViewSet):
    queryset = ObjectiveProblem.objects.all()
    serializer_class = ObjectiveProblemSerializer
    permission_classes = [IsAuthenticated]  # 로그인한 사용자만 접근 가능
    def perform_create(self, serializer):
        # 현재 로그인한 사용자를 creator로 자동 할당
        serializer.save(creator=self.request.user)
        
        
class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]  # 관리자만 생성/수정/삭제
        else:
            permission_classes = [IsAuthenticated]  # 로그인한 사용자는 조회만 가능
        return [permission() for permission in permission_classes]

class ChapterListByTopicView(generics.ListAPIView):
    serializer_class = ChapterSerializer
    permission_classes = [IsAuthenticated]  # 로그인한 사용자는 조회만 가능

    def get_queryset(self):
        topic_id = self.kwargs['topic_id']
        return Chapter.objects.filter(topic_id=topic_id)