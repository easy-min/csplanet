from rest_framework import viewsets
from ..models.subjective_problem import SubjectiveProblem
from ..serializers.subjective_serializers import SubjectiveProblemReadSerializer, SubjectiveProblemWriteSerializer

class SubjectiveProblemViewSet(viewsets.ModelViewSet):
    queryset = SubjectiveProblem.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SubjectiveProblemWriteSerializer
        return SubjectiveProblemReadSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
