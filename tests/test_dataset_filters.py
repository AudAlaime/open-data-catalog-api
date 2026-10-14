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
        values = {
            "title": "Public transport stops",
            "description": "Locations of public transport stops.",
            "producer": "City Council",
            "theme": "Transport",
            "tags": ["transport", "mobility"],
            "source_url": "https://example.com/datasets/transport-stops",
            "license": "Open Database License",
            "is_published": True,
        }
        values.update(overrides)
        return Dataset.objects.create(**values)

    return create_dataset


@pytest.mark.django_db
@pytest.mark.parametrize(
    "field,value",
    [
        ("title", "Energy production"),
        ("description", "Energy consumption by municipality."),
        ("producer", "Energy Agency"),
        ("theme", "Energy"),
        ("tags", ["energy", "electricity"]),
    ],
)
def test_search_across_dataset_fields(
    api_client: APIClient,
    dataset_factory: Callable[..., Dataset],
    field: str,
    value: object,
) -> None:
    matching_dataset = dataset_factory(**{field: value})
    dataset_factory(title="Road traffic")

    response = api_client.get(reverse("dataset-list"), {"q": "energy"})

    assert response.status_code == status.HTTP_200_OK
    assert [item["id"] for item in response.json()] == [matching_dataset.id]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "parameter,value,matching_value",
    [
        ("theme", "energy", "Energy"),
        ("producer", "ademe", "ADEME"),
        ("license", "open licence", "Open Licence"),
    ],
)
def test_filter_by_text_field(
    api_client: APIClient,
    dataset_factory: Callable[..., Dataset],
    parameter: str,
    value: str,
    matching_value: str,
) -> None:
    matching_dataset = dataset_factory(**{parameter: matching_value})
    dataset_factory(title="Another dataset")

    response = api_client.get(reverse("dataset-list"), {parameter: value})

    assert response.status_code == status.HTTP_200_OK
    assert [item["id"] for item in response.json()] == [matching_dataset.id]


@pytest.mark.django_db
@pytest.mark.parametrize("value,expected_status", [("true", True), ("false", False)])
def test_filter_by_publication_status(
    api_client: APIClient,
    dataset_factory: Callable[..., Dataset],
    value: str,
    expected_status: bool,
) -> None:
    matching_dataset = dataset_factory(is_published=expected_status)
    dataset_factory(title="Other publication status", is_published=not expected_status)

    response = api_client.get(reverse("dataset-list"), {"is_published": value})

    assert response.status_code == status.HTTP_200_OK
    assert [item["id"] for item in response.json()] == [matching_dataset.id]


@pytest.mark.django_db
def test_list_defaults_to_published_datasets(
    api_client: APIClient, dataset_factory: Callable[..., Dataset]
) -> None:
    published_dataset = dataset_factory()
    dataset_factory(title="Draft dataset", is_published=False)

    response = api_client.get(reverse("dataset-list"))

    assert response.status_code == status.HTTP_200_OK
    assert [item["id"] for item in response.json()] == [published_dataset.id]
