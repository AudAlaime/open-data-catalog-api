from rest_framework import serializers

from catalog.models import Dataset


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = [
            "id",
            "title",
            "description",
            "producer",
            "theme",
            "tags",
            "source_url",
            "license",
            "is_published",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
