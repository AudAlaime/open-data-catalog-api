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
