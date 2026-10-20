import json
from io import StringIO
from unittest.mock import MagicMock, patch
from urllib.error import URLError
from urllib.parse import parse_qs, urlparse

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from catalog.models import Dataset


def api_record(**overrides: object) -> dict[str, object]:
    record = {
        "title": "Energy consumption by municipality",
        "description": "Annual energy consumption statistics.",
        "organization": {"name": "ADEME"},
        "tags": ["energy", "statistics"],
        "page": "https://www.data.gouv.fr/fr/datasets/energy-consumption/",
        "license": "lov2",
        "private": False,
    }
    record.update(overrides)
    return record


def mocked_response(payload: object) -> MagicMock:
    response = MagicMock()
    response.__enter__.return_value.read.return_value = json.dumps(payload).encode()
    return response


@pytest.mark.django_db
@patch("catalog.management.commands.import_datagouv.urlopen")
def test_imports_metadata_and_uses_expected_api_parameters(
    urlopen_mock: MagicMock,
) -> None:
    urlopen_mock.return_value = mocked_response({"data": [api_record()]})
    output = StringIO()

    call_command("import_datagouv", query="energie", limit=5, stdout=output)

    dataset = Dataset.objects.get()
    assert dataset.title == "Energy consumption by municipality"
    assert dataset.description == "Annual energy consumption statistics."
    assert dataset.producer == "ADEME"
    assert dataset.theme == "energy"
    assert dataset.tags == ["energy", "statistics"]
    assert dataset.source_url.endswith("/energy-consumption/")
    assert dataset.license == "lov2"
    assert dataset.is_published is True
    assert "1 created, 0 already existed, 0 skipped" in output.getvalue()

    request = urlopen_mock.call_args.args[0]
    parameters = parse_qs(urlparse(request.full_url).query)
    assert parameters == {"q": ["energie"], "page": ["1"], "page_size": ["5"]}
    assert urlopen_mock.call_args.kwargs["timeout"] == 10


@pytest.mark.django_db
@patch("catalog.management.commands.import_datagouv.urlopen")
def test_import_is_idempotent(urlopen_mock: MagicMock) -> None:
    urlopen_mock.return_value = mocked_response({"data": [api_record()]})

    call_command("import_datagouv", query="energie", stdout=StringIO())
    second_output = StringIO()
    call_command("import_datagouv", query="energie", stdout=second_output)

    assert Dataset.objects.count() == 1
    assert "0 created, 1 already existed, 0 skipped" in second_output.getvalue()


@pytest.mark.django_db
@patch("catalog.management.commands.import_datagouv.urlopen")
def test_import_never_processes_more_records_than_the_limit(
    urlopen_mock: MagicMock,
) -> None:
    second_record = api_record(
        title="Second dataset",
        page="https://www.data.gouv.fr/fr/datasets/second-dataset/",
    )
    urlopen_mock.return_value = mocked_response({"data": [api_record(), second_record]})

    call_command("import_datagouv", query="energie", limit=1, stdout=StringIO())

    assert Dataset.objects.count() == 1
    assert Dataset.objects.get().title == "Energy consumption by municipality"


@pytest.mark.django_db
@patch("catalog.management.commands.import_datagouv.urlopen")
def test_handles_missing_fields_and_skips_records_without_source_url(
    urlopen_mock: MagicMock,
) -> None:
    record_with_fallbacks = {
        "uri": "https://www.data.gouv.fr/api/1/datasets/example/",
        "owner": {"first_name": "Ada", "last_name": "Lovelace"},
    }
    urlopen_mock.return_value = mocked_response(
        {"data": [record_with_fallbacks, api_record(page=None)]}
    )
    output = StringIO()

    call_command("import_datagouv", query="energie", stdout=output)

    dataset = Dataset.objects.get()
    assert dataset.title == "Untitled data.gouv.fr dataset"
    assert dataset.description == ""
    assert dataset.producer == "Ada Lovelace"
    assert dataset.theme == "energie"
    assert dataset.tags == []
    assert dataset.license == "Not specified"
    assert "1 created, 0 already existed, 1 skipped" in output.getvalue()


@pytest.mark.parametrize("limit", [0, 21])
@patch("catalog.management.commands.import_datagouv.urlopen")
def test_rejects_limits_outside_allowed_range(
    urlopen_mock: MagicMock, limit: int
) -> None:
    with pytest.raises(CommandError, match="between 1 and 20"):
        call_command("import_datagouv", query="energie", limit=limit)

    urlopen_mock.assert_not_called()


@pytest.mark.django_db
@patch("catalog.management.commands.import_datagouv.urlopen")
def test_reports_network_errors(urlopen_mock: MagicMock) -> None:
    urlopen_mock.side_effect = URLError("connection refused")

    with pytest.raises(CommandError, match="Unable to reach data.gouv.fr"):
        call_command("import_datagouv", query="energie")


@pytest.mark.django_db
@patch("catalog.management.commands.import_datagouv.urlopen")
def test_rejects_invalid_api_response(urlopen_mock: MagicMock) -> None:
    urlopen_mock.return_value = mocked_response({"unexpected": []})

    with pytest.raises(CommandError, match="unexpected response format"):
        call_command("import_datagouv", query="energie")
