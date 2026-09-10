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

Build the image and start the application in the background:

```bash
docker compose up --build --detach
```

The API is then available at `http://localhost:8000`. Check its health with:

```bash
curl http://localhost:8000/health
```

View the application logs:

```bash
docker compose logs --follow web
```

Stop and remove the containers:

```bash
docker compose down
```

## Quality checks

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```
