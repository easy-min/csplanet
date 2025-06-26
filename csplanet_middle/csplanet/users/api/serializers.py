from rest_framework import serializers
from django.contrib.auth import get_user_model
from dj_rest_auth.registration.serializers import RegisterSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["name", "email"]  # username 제거, name 추가

class UserRegistrationSerializer(RegisterSerializer):
    name = serializers.CharField(required=True, max_length=255)
    username = None

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['name'] = self.validated_data.get('name', '')
        return data

    def save(self, request):
        user = super().save(request)
        user.name = self.validated_data.get('name', '')
        user.save()
        return user
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance
