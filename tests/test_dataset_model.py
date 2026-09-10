import pytest

from catalog.models import Dataset


@pytest.fixture
def dataset() -> Dataset:
    return Dataset.objects.create(
        title="Public transport stops",
        description="Locations of public transport stops in the city.",
        producer="City Council",
        theme="Transport",
        source_url="https://example.com/datasets/transport-stops",
        license="Open Database License",
    )


@pytest.mark.django_db
def test_dataset_creation_and_defaults(dataset: Dataset) -> None:
    assert dataset.pk is not None
    assert dataset.tags == []
    assert dataset.is_published is True
    assert dataset.created_at is not None
    assert dataset.updated_at is not None
    assert str(dataset) == "Public transport stops"


@pytest.mark.django_db
def test_tags_default_is_not_shared_between_datasets(dataset: Dataset) -> None:
    another_dataset = Dataset.objects.create(
        title="Public parks",
        description="Locations of public parks.",
        producer="City Council",
        theme="Environment",
        source_url="https://example.com/datasets/public-parks",
        license="Open Database License",
    )

    dataset.tags.append("transport")

    assert another_dataset.tags == []


@pytest.mark.django_db
def test_datasets_are_ordered_by_title(dataset: Dataset) -> None:
    first_alphabetically = Dataset.objects.create(
        title="Air quality",
        description="Daily air-quality measurements.",
        producer="Environment Agency",
        theme="Environment",
        source_url="https://example.com/datasets/air-quality",
        license="Open Database License",
    )

    assert list(Dataset.objects.all()) == [first_alphabetically, dataset]
