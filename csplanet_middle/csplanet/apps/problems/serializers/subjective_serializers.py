from rest_framework import serializers
from ..models.subjective_problem import SubjectiveProblem, QuestionKeywordMapping, SubjectiveKeyword

class SubjectiveKeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectiveKeyword
        fields = ['id', 'word']

class QuestionKeywordMappingSerializer(serializers.ModelSerializer):
    keyword = SubjectiveKeywordSerializer()

    class Meta:
        model = QuestionKeywordMapping
        fields = ['id', 'keyword', 'importance']
class SubjectiveProblemReadSerializer(serializers.ModelSerializer):
    keywords = QuestionKeywordMappingSerializer(
        many=True,
        source='questionkeywordmapping_set',
        read_only=True
    )

    class Meta:
        model = SubjectiveProblem
        fields = ['id', 'chapter', 'content', 'explanation', 'score', 'keywords']
        read_only_fields = ['creator']

class SubjectiveProblemWriteSerializer(serializers.ModelSerializer):
    keywords = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )

    class Meta:
        model = SubjectiveProblem
        fields = ['id', 'chapter', 'content', 'explanation', 'score', 'keywords']

    def create(self, validated_data):
        keywords_data = validated_data.pop('keywords')
        problem = SubjectiveProblem.objects.create(**validated_data)
        for kw_mapping in keywords_data:
            keyword_data = kw_mapping.get('keyword', {})
            keyword_obj, _ = SubjectiveKeyword.objects.get_or_create(word=keyword_data.get('word'))
            QuestionKeywordMapping.objects.create(
                question=problem,
                keyword=keyword_obj,
                importance=kw_mapping.get('importance', 1)
            )
        return problem

    def update(self, instance, validated_data):
        keywords_data = validated_data.pop('keywords', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if keywords_data is not None:
            instance.questionkeywordmapping_set.all().delete()
            for kw_mapping in keywords_data:
                keyword_data = kw_mapping.get('keyword', {})
                keyword_obj, _ = SubjectiveKeyword.objects.get_or_create(word=keyword_data.get('word'))
                QuestionKeywordMapping.objects.create(
                    question=instance,
                    keyword=keyword_obj,
                    importance=kw_mapping.get('importance', 1)
                )
        return instance
