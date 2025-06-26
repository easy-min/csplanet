from rest_framework import serializers
from ..models.objective_problem import ObjectiveChoice, ObjectiveProblem

class ObjectiveChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectiveChoice
        fields = ['id', 'content', 'is_correct']

class ObjectiveProblemSerializer(serializers.ModelSerializer):
    choices = ObjectiveChoiceSerializer(many=True)
    
    class Meta:
        model = ObjectiveProblem
        fields = ['id', 'chapter', 'content', 'explanation', 'score', 'choices']
        read_only_fields = ['creator']

    def create(self, validated_data):
        choices_data = validated_data.pop('choices')
        problem = ObjectiveProblem.objects.create(**validated_data)
        for choice_data in choices_data:
            ObjectiveChoice.objects.create(question=problem, **choice_data)
        return problem

    def update(self, instance, validated_data):
        choices_data = validated_data.pop('choices', None)  # choices가 없으면 None 반환
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if choices_data is not None:
            instance.choices.all().delete()
            for choice_data in choices_data:
                ObjectiveChoice.objects.create(question=instance, **choice_data)
        return instance

