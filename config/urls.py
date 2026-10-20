from django.urls import include, path

from core.views import health_check

urlpatterns = [
    path("health", health_check, name="health"),
    path("api/datasets/", include("catalog.urls")),
]
