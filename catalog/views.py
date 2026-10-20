from django.db.models import Q, QuerySet, TextField
from django.db.models.functions import Cast
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet

from catalog.models import Dataset
from catalog.serializers import DatasetSerializer


class DatasetPagination(PageNumberPagination):
    page_size = 10


class DatasetViewSet(ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    pagination_class = DatasetPagination

    def get_queryset(self) -> QuerySet[Dataset]:
        queryset = Dataset.objects.all()
        if self.action != "list":
            return queryset

        params = self.request.query_params

        publication_status = params.get("is_published", "true").lower()
        if publication_status in {"true", "false"}:
            queryset = queryset.filter(is_published=publication_status == "true")
        else:
            queryset = queryset.filter(is_published=True)

        for field in ("theme", "producer", "license"):
            value = params.get(field)
            if value:
                queryset = queryset.filter(**{f"{field}__iexact": value})

        query = params.get("q", "").strip()
        if query:
            queryset = queryset.annotate(tags_text=Cast("tags", TextField())).filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(producer__icontains=query)
                | Q(theme__icontains=query)
                | Q(tags_text__icontains=query)
            )

        return queryset.order_by("id")
