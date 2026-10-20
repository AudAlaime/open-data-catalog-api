import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from catalog.models import Dataset


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def dataset_payload() -> dict[str, object]:
    return {
        "title": "Public transport stops",
        "description": "Locations of public transport stops in the city.",
        "producer": "City Council",
        "theme": "Transport",
        "tags": ["transport", "mobility"],
        "source_url": "https://example.com/datasets/transport-stops",
        "license": "Open Database License",
        "is_published": True,
    }


@pytest.fixture
def dataset(dataset_payload: dict[str, object]) -> Dataset:
    return Dataset.objects.create(**dataset_payload)


@pytest.mark.django_db
def test_list_only_returns_published_datasets(
    api_client: APIClient, dataset: Dataset, dataset_payload: dict[str, object]
) -> None:
    unpublished_payload = {
        **dataset_payload,
        "title": "Unpublished dataset",
        "is_published": False,
    }
    Dataset.objects.create(**unpublished_payload)

    response = api_client.get(reverse("dataset-list"))

    assert response.status_code == status.HTTP_200_OK
    assert [item["id"] for item in response.json()["results"]] == [dataset.id]


@pytest.mark.django_db
def test_create_dataset(
    api_client: APIClient, dataset_payload: dict[str, object]
) -> None:
    response = api_client.post(reverse("dataset-list"), dataset_payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["title"] == dataset_payload["title"]
    assert Dataset.objects.filter(pk=response.json()["id"]).exists()


@pytest.mark.django_db
def test_retrieve_dataset(api_client: APIClient, dataset: Dataset) -> None:
    response = api_client.get(reverse("dataset-detail", args=[dataset.id]))

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == dataset.id
    assert response.json()["title"] == dataset.title


@pytest.mark.django_db
def test_partially_update_dataset(api_client: APIClient, dataset: Dataset) -> None:
    response = api_client.patch(
        reverse("dataset-detail", args=[dataset.id]),
        {"title": "Updated transport stops"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    dataset.refresh_from_db()
    assert dataset.title == "Updated transport stops"


@pytest.mark.django_db
def test_delete_dataset(api_client: APIClient, dataset: Dataset) -> None:
    response = api_client.delete(reverse("dataset-detail", args=[dataset.id]))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Dataset.objects.filter(pk=dataset.id).exists()


@pytest.mark.django_db
def test_create_dataset_requires_title(
    api_client: APIClient, dataset_payload: dict[str, object]
) -> None:
    dataset_payload.pop("title")

    response = api_client.post(reverse("dataset-list"), dataset_payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "title" in response.json()
