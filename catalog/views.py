from django.db.models import QuerySet
from rest_framework.viewsets import ModelViewSet

from catalog.models import Dataset
from catalog.serializers import DatasetSerializer


class DatasetViewSet(ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

    def get_queryset(self) -> QuerySet[Dataset]:
        queryset = Dataset.objects.all()
        if self.action == "list":
            return queryset.filter(is_published=True)
        return queryset
