from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import UserViewSet  # UserRegistrationView, CustomAuthToken 제거

router = DefaultRouter()
router.register("", UserViewSet, basename="user")

app_name = "users"

urlpatterns = [
    path('', include(router.urls)),
]
