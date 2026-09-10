from django.contrib import admin

from catalog.models import Dataset


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("title", "producer", "theme", "is_published", "updated_at")
    list_filter = ("theme", "is_published")
