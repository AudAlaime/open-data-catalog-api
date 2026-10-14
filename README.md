# Open Data Catalog API

A minimal Django REST Framework API for managing a catalog of public datasets.

## Requirements

- Python 3.12
- [uv](https://docs.astral.sh/uv/)

## Setup

Install the project and development dependencies:

```bash
uv sync --dev
```

Start the development server:

```bash
uv run python manage.py runserver
```

The health endpoint is available at `http://127.0.0.1:8000/health`.

## Dataset API

List published datasets:

```bash
curl http://localhost:8000/api/datasets/
```

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

Filters can be combined. Without `is_published`, only published datasets are
returned.

Create a dataset:

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

Retrieve, partially update, or delete dataset `1`:

```bash
curl http://localhost:8000/api/datasets/1/
curl --request PATCH http://localhost:8000/api/datasets/1/ \
  --header "Content-Type: application/json" \
  --data '{"title": "Updated title"}'
curl --request DELETE http://localhost:8000/api/datasets/1/
```

## Docker

Docker Compose starts two services:

- `web`: the Django application;
- `db`: the PostgreSQL database.

Build the image and start both services in the background:

```bash
docker compose up --build --detach
```

The API is then available at `http://localhost:8000`. Check its health with:

```bash
curl http://localhost:8000/health
```

Check Django and PostgreSQL:

```bash
docker compose exec web python manage.py check
docker compose exec db pg_isready -U catalog_user -d open_data_catalog
```

Apply Django's built-in database migrations after the first start:

```bash
docker compose exec web python manage.py migrate
```

Create seven example datasets for local testing:

```bash
docker compose exec web python manage.py seed_datasets
```

The command is safe to run more than once. You can then list the examples or
search them:

```bash
curl http://localhost:8000/api/datasets/
curl "http://localhost:8000/api/datasets/?q=energy"
```

Without Docker, the equivalent command is:

```bash
uv run python manage.py seed_datasets
```

View the application logs:

```bash
docker compose logs --follow web
```

Stop and remove the containers:

```bash
docker compose down
```

The PostgreSQL data is kept in a Docker volume named `postgres_data`. To also
delete this local data when stopping the services, run:

```bash
docker compose down --volumes
```

## Database configuration

Inside Docker, Django reads `DATABASE_URL` and connects to the `db` service:

```text
postgresql://catalog_user:catalog_password@db:5432/open_data_catalog
```

You can also configure PostgreSQL with `POSTGRES_DB`, `POSTGRES_USER`,
`POSTGRES_PASSWORD`, `POSTGRES_HOST`, and `POSTGRES_PORT`. The available
variables are documented in `.env.example`. Do not commit a real `.env` file.

If neither `DATABASE_URL` nor `POSTGRES_DB` is defined, Django uses SQLite.
This is the default for local commands and tests.

## Quality checks

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```
