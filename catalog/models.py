from django.db import models


class Dataset(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    producer = models.CharField(max_length=255, db_index=True)
    theme = models.CharField(max_length=100, db_index=True)
    tags = models.JSONField(default=list)
    source_url = models.URLField()
    license = models.CharField(max_length=255)
    is_published = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title
