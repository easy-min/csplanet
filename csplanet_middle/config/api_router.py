from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from csplanet.users.api.views import UserViewSet

from csplanet.apps.exams.api.exam import ExamViewSet, TestSessionViewSet, ExamResultViewSet

from csplanet.apps.problems.api.objective_views import ObjectiveProblemViewSet
from csplanet.apps.problems.api.subjective_views import SubjectiveProblemViewSet
router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)

router.register("objective-problems", ObjectiveProblemViewSet, basename="objective-problem")
router.register("subjective-problems", SubjectiveProblemViewSet, basename="subjective-problem")
router.register("exams", ExamViewSet, basename="exam")
router.register("exam-questions", ExamResultViewSet, basename="exam-question")
router.register("test-sessions", TestSessionViewSet, basename="test-session")
router.register("exam-results", ExamResultViewSet, basename="exam-result")


app_name = "api"
urlpatterns = router.urls
