from collections.abc import Callable

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from catalog.models import Dataset


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def dataset_factory() -> Callable[..., Dataset]:
    def create_dataset(**overrides: object) -> Dataset:
        number = Dataset.objects.count() + 1
        values = {
            "title": f"Dataset {number}",
            "description": "Dataset used to test pagination.",
            "producer": "Default producer",
            "theme": "default",
            "tags": [],
            "source_url": f"https://example.com/datasets/{number}",
            "license": "Open Licence",
            "is_published": True,
        }
        values.update(overrides)
        return Dataset.objects.create(**values)

    return create_dataset


@pytest.mark.django_db
def test_dataset_list_is_paginated_in_stable_id_order(
    api_client: APIClient, dataset_factory: Callable[..., Dataset]
) -> None:
    datasets = [dataset_factory() for _ in range(15)]

    first_response = api_client.get(reverse("dataset-list"))
    second_response = api_client.get(reverse("dataset-list"), {"page": 2})

    assert first_response.status_code == status.HTTP_200_OK
    assert first_response.json()["count"] == 15
    assert first_response.json()["previous"] is None
    assert first_response.json()["next"].endswith("?page=2")
    assert [item["id"] for item in first_response.json()["results"]] == [
        dataset.id for dataset in datasets[:10]
    ]

    assert second_response.status_code == status.HTTP_200_OK
    assert second_response.json()["next"] is None
    assert second_response.json()["previous"] == "http://testserver/api/datasets/"
    assert [item["id"] for item in second_response.json()["results"]] == [
        dataset.id for dataset in datasets[10:]
    ]


@pytest.mark.django_db
def test_filters_can_be_combined_with_pagination(
    api_client: APIClient, dataset_factory: Callable[..., Dataset]
) -> None:
    matching_datasets = [
        dataset_factory(theme="energy", producer="ADEME") for _ in range(12)
    ]
    dataset_factory(theme="transport", producer="ADEME")
    dataset_factory(theme="energy", producer="INSEE")

    response = api_client.get(
        reverse("dataset-list"),
        {"theme": "energy", "producer": "ADEME", "page": 2},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 12
    assert [item["id"] for item in response.json()["results"]] == [
        dataset.id for dataset in matching_datasets[10:]
    ]


@pytest.mark.django_db
def test_pagination_excludes_unpublished_datasets_by_default(
    api_client: APIClient, dataset_factory: Callable[..., Dataset]
) -> None:
    published_datasets = [dataset_factory() for _ in range(11)]
    for _ in range(5):
        dataset_factory(is_published=False)

    response = api_client.get(reverse("dataset-list"), {"page": 2})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 11
    assert [item["id"] for item in response.json()["results"]] == [
        published_datasets[-1].id
    ]


@pytest.mark.django_db
def test_nonexistent_page_returns_not_found(
    api_client: APIClient, dataset_factory: Callable[..., Dataset]
) -> None:
    dataset_factory()

    response = api_client.get(reverse("dataset-list"), {"page": 2})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Invalid page."}
