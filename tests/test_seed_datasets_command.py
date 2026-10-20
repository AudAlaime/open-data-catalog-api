from io import StringIO

import pytest
from django.core.management import call_command

from catalog.models import Dataset


@pytest.mark.django_db
def test_seed_command_creates_expected_datasets() -> None:
    call_command("seed_datasets", stdout=StringIO())

    assert Dataset.objects.count() == 7
    assert set(Dataset.objects.values_list("theme", flat=True)) == {
        "energy",
        "transport",
        "housing",
        "environment",
        "geography",
    }


@pytest.mark.django_db
def test_seed_command_is_idempotent() -> None:
    call_command("seed_datasets", stdout=StringIO())
    call_command("seed_datasets", stdout=StringIO())

    assert Dataset.objects.count() == 7


@pytest.mark.django_db
def test_seed_command_displays_a_summary() -> None:
    first_output = StringIO()
    second_output = StringIO()

    call_command("seed_datasets", stdout=first_output)
    call_command("seed_datasets", stdout=second_output)

    assert "Seed complete: 7 created, 0 already existed." in first_output.getvalue()
    assert "Seed complete: 0 created, 7 already existed." in second_output.getvalue()
