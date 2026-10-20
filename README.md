# Open Data Catalog API

[![CI](https://github.com/AudAlaime/open-data-catalog-api/actions/workflows/ci.yml/badge.svg)](https://github.com/AudAlaime/open-data-catalog-api/actions/workflows/ci.yml)

Open Data Catalog API is a Django REST Framework project for managing and
exposing a catalog of public datasets through a REST API. It provides a small,
well-tested backend that can be run locally with either Docker and PostgreSQL
or Python and SQLite.

## Key Features

- CRUD API for public dataset records
- Text search across titles, descriptions, producers, themes, and tags
- Filters for theme, producer, license, and publication status
- Stable page-number pagination with 10 datasets per page
- Published datasets shown by default in list responses
- Idempotent command for loading realistic demonstration data
- Automated tests with pytest and code quality checks with Ruff
- GitHub Actions CI on pushes and pull requests

## Tech Stack

- Python 3.12
- Django and Django REST Framework
- PostgreSQL with SQLite available for local development and tests
- Docker and Docker Compose
- [uv](https://docs.astral.sh/uv/) for dependency management
- pytest and pytest-django
- Ruff
- GitHub Actions

## Quick Start with Docker

Build the image and start the Django and PostgreSQL services:

```bash
docker compose up --build --detach
```

Apply the database migrations and load seven example datasets:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_datasets
```

The seed command is idempotent, so running it again does not create duplicate
datasets.

Check the application and browse the seeded catalog:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/datasets/
curl "http://localhost:8000/api/datasets/?q=energy"
```

View application logs:

```bash
docker compose logs --follow web
```

Stop and remove the containers:

```bash
docker compose down
```

PostgreSQL data is kept in the `postgres_data` Docker volume. To remove the
local data as well, run:

```bash
docker compose down --volumes
```

## Local Setup

Requirements:

- Python 3.12
- [uv](https://docs.astral.sh/uv/)

Install the project and its development dependencies:

```bash
uv sync --dev
```

Start the development server:

```bash
uv run python manage.py runserver
```

Load the example datasets without Docker:

```bash
uv run python manage.py seed_datasets
```

Import up to five dataset metadata records from data.gouv.fr:

```bash
uv run python manage.py import_datagouv --query energie --limit 5
```

The API is available at `http://127.0.0.1:8000`, and the health endpoint is
available at `http://127.0.0.1:8000/health`.

## Dataset API

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/datasets/` | List published datasets with pagination |
| `POST` | `/api/datasets/` | Create a dataset |
| `GET` | `/api/datasets/{id}/` | Retrieve a dataset |
| `PATCH` | `/api/datasets/{id}/` | Partially update a dataset |
| `DELETE` | `/api/datasets/{id}/` | Delete a dataset |

### Search and filters

Search in titles, descriptions, producers, themes, and tags:

```bash
curl "http://localhost:8000/api/datasets/?q=energy"
```

Filter by theme, producer, license, or publication status:

```bash
curl "http://localhost:8000/api/datasets/?theme=energy"
curl "http://localhost:8000/api/datasets/?producer=ADEME"
curl "http://localhost:8000/api/datasets/?license=Open%20Licence"
curl "http://localhost:8000/api/datasets/?is_published=false"
```

Filters can be combined. If `is_published` is omitted, only published datasets
are returned.

### Pagination

Dataset lists contain 10 results per page and use the standard Django REST
Framework response structure:

```json
{
  "count": 15,
  "next": "http://localhost:8000/api/datasets/?page=2",
  "previous": null,
  "results": []
}
```

Request another page directly or combine pagination with search and filters:

```bash
curl "http://localhost:8000/api/datasets/?page=2"
curl "http://localhost:8000/api/datasets/?theme=energy&page=2"
curl "http://localhost:8000/api/datasets/?q=energy&page=2"
```

### Create a dataset

```bash
curl --request POST http://localhost:8000/api/datasets/ \
  --header "Content-Type: application/json" \
  --data '{
    "title": "Public transport stops",
    "description": "Locations of public transport stops.",
    "producer": "City Council",
    "theme": "Transport",
    "tags": ["transport", "mobility"],
    "source_url": "https://example.com/datasets/transport-stops",
    "license": "Open Database License",
    "is_published": true
  }'
```

### Retrieve, update, or delete a dataset

```bash
curl http://localhost:8000/api/datasets/1/
curl --request PATCH http://localhost:8000/api/datasets/1/ \
  --header "Content-Type: application/json" \
  --data '{"title": "Updated title"}'
curl --request DELETE http://localhost:8000/api/datasets/1/
```

## Database Configuration

Docker Compose starts two services:

- `web`: the Django application
- `db`: the PostgreSQL database

Inside Docker, Django reads `DATABASE_URL` and connects to the `db` service:

```text
postgresql://catalog_user:catalog_password@db:5432/open_data_catalog
```

You can also configure PostgreSQL with `POSTGRES_DB`, `POSTGRES_USER`,
`POSTGRES_PASSWORD`, `POSTGRES_HOST`, and `POSTGRES_PORT`. The available
variables are documented in `.env.example`. Do not commit a real `.env` file.

If neither `DATABASE_URL` nor `POSTGRES_DB` is defined, Django uses SQLite.
This is the default for local commands and tests.

Check Django and PostgreSQL inside Docker:

```bash
docker compose exec web python manage.py check
docker compose exec db pg_isready -U catalog_user -d open_data_catalog
```

## Importing Metadata from data.gouv.fr

Import the first page of public dataset metadata matching a search query:

```bash
uv run python manage.py import_datagouv --query energie --limit 5
```

With Docker:

```bash
docker compose exec web python manage.py import_datagouv \
  --query energie --limit 5
```

The default limit is 5 and the maximum is 20. The command imports metadata
only: it does not download dataset files. Records are identified by their
data.gouv.fr page URL, so running the same import again does not create
duplicates. Records without a usable public URL are skipped.

## Tests and Code Quality

Run the complete local test and quality suite:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

The GitHub Actions workflow in `.github/workflows/ci.yml` runs the same checks
automatically on every push and pull request using Python 3.12 and `uv`.
