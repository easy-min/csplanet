app_name = "problems"

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.objective_views import ChapterListByTopicView, ObjectiveProblemViewSet, TopicViewSet
from .api.subjective_views import SubjectiveProblemViewSet

router = DefaultRouter()
router.register(r'objective-problems', ObjectiveProblemViewSet)
router.register(r'subjective-problems', SubjectiveProblemViewSet)
router.register(r'topics', TopicViewSet)  # 추가

urlpatterns = [
    path('', include(router.urls)),
    path('topics/<int:topic_id>/chapters/', ChapterListByTopicView.as_view(), name='chapter-list-by-topic'),
]
