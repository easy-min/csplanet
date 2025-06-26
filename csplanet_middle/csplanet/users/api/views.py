from rest_framework import status, permissions, generics
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotAuthenticated

from csplanet.users.models import User
from .serializers import UserSerializer, UserRegistrationSerializer

from rest_framework import status, permissions
from rest_framework.exceptions import NotAuthenticated

class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "pk"
    # 모든 액션에 인증 필수 적용
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 인증된 사용자만 자신의 데이터 접근
        return super().get_queryset().filter(id=self.request.user.id)

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        # 인증 체크 (permission_classes가 이미 처리하지만 추가 보안)
        if not request.user.is_authenticated:
            raise NotAuthenticated("Authentication credentials were not provided.")
        
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user, 
                data=request.data, 
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            updated_user = serializer.save()
            
            # 안전한 디버깅 (인증된 사용자만 접근)
            print(f"Updated user name: {updated_user.name}")
            return Response(serializer.data)
