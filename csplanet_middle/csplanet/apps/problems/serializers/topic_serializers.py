from rest_framework import serializers
from ..models.topic import Topic

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name', 'description']
