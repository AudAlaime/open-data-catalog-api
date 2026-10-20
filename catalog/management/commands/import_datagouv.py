import json
from json import JSONDecodeError
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand, CommandError, CommandParser

from catalog.models import Dataset

API_URL = "https://www.data.gouv.fr/api/1/datasets/"
HTTP_TIMEOUT = 10
MAX_LIMIT = 20


class Command(BaseCommand):
    help = "Import dataset metadata from the public data.gouv.fr API."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--query", required=True, help="Search query")
        parser.add_argument(
            "--limit",
            type=int,
            default=5,
            help="Number of datasets to import (default: 5, maximum: 20)",
        )

    def handle(self, *args: object, **options: object) -> None:
        query = str(options["query"]).strip()
        limit = int(options["limit"])

        if not query:
            raise CommandError("The query cannot be empty.")
        if not 1 <= limit <= MAX_LIMIT:
            raise CommandError("The limit must be between 1 and 20.")

        records = self._fetch_records(query, limit)
        created_count = 0
        existing_count = 0
        skipped_count = 0

        for record in records:
            values = self._map_record(record, query)
            if values is None:
                skipped_count += 1
                continue

            source_url = values.pop("source_url")
            _, created = Dataset.objects.get_or_create(
                source_url=source_url,
                defaults=values,
            )
            created_count += int(created)
            existing_count += int(not created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete: {created_count} created, "
                f"{existing_count} already existed, {skipped_count} skipped."
            )
        )

    def _fetch_records(self, query: str, limit: int) -> list[dict[str, object]]:
        url = f"{API_URL}?{urlencode({'q': query, 'page': 1, 'page_size': limit})}"
        request = Request(url, headers={"User-Agent": "open-data-catalog-api/1.0"})

        try:
            with urlopen(request, timeout=HTTP_TIMEOUT) as response:  # noqa: S310
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            raise CommandError(f"data.gouv.fr returned HTTP {error.code}.") from error
        except (URLError, TimeoutError) as error:
            raise CommandError(f"Unable to reach data.gouv.fr: {error}.") from error
        except (JSONDecodeError, UnicodeDecodeError) as error:
            raise CommandError("data.gouv.fr returned invalid JSON.") from error

        if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
            raise CommandError("data.gouv.fr returned an unexpected response format.")

        records = [record for record in payload["data"] if isinstance(record, dict)]
        return records[:limit]

    def _map_record(
        self, record: dict[str, object], query: str
    ) -> dict[str, object] | None:
        source_url = self._source_url(record)
        if source_url is None:
            return None

        tags = record.get("tags")
        clean_tags = (
            [tag for tag in tags if isinstance(tag, str)]
            if isinstance(tags, list)
            else []
        )

        organization = record.get("organization")
        producer = "Unknown producer"
        if isinstance(organization, dict) and organization.get("name"):
            producer = str(organization["name"])
        else:
            owner = record.get("owner")
            if isinstance(owner, dict):
                owner_name = " ".join(
                    str(owner.get(field, "")).strip()
                    for field in ("first_name", "last_name")
                ).strip()
                producer = owner_name or producer

        license_value = record.get("license")
        if isinstance(license_value, dict):
            license_value = license_value.get("title") or license_value.get("id")

        title = str(record.get("title") or "Untitled data.gouv.fr dataset")[:255]
        description = str(
            record.get("description") or record.get("description_short") or ""
        )

        return {
            "title": title,
            "description": description,
            "producer": producer[:255],
            "theme": (clean_tags[0] if clean_tags else query)[:100],
            "tags": clean_tags,
            "source_url": source_url,
            "license": str(license_value or "Not specified")[:255],
            "is_published": not bool(record.get("private", False)),
        }

    @staticmethod
    def _source_url(record: dict[str, object]) -> str | None:
        for field in ("page", "uri"):
            value = record.get(field)
            if not isinstance(value, str) or len(value) > 200:
                continue
            parsed_url = urlparse(value)
            if parsed_url.scheme in {"http", "https"} and parsed_url.netloc:
                return value
        return None
