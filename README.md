# AI Exam Auto-Correction Tool

This repository contains the FastAPI backend scaffolding for the Smart Score exam
correction service. The application code lives under `app/` and exposes both a
health endpoint and the first set of `/api` routes for working with exams,
questions, and rubrics.

## Project layout

- `app/main.py` – FastAPI application with the `/health` check plus the `/api`
  endpoints for creating exams, questions, and rubrics.
- `app/database.py` – Async SQLAlchemy engine/session helpers and the `init_db`
  routine used during startup.
- `app/models.py` – Declarative ORM models representing the users, students,
  exams, questions, rubrics, submissions, and answers used by the platform.
- `app/schemas.py` – Pydantic models mirroring the ORM entities for request and
  response payload validation.
- `app/crud.py` – Minimal data-access helpers behind the API endpoints.
- `tests/` – Pytest coverage for the health check, database metadata, and API
  flows.
- `docker-compose.yml` – Local orchestration for the FastAPI service and a
  PostgreSQL database.

The older placeholder `backend/` folder from a previous merge has been removed
now that the fully featured FastAPI application lives under `app/`.

## Development

Create a virtual environment, install the dependencies from `requirements.txt`,
and run the FastAPI server with Uvicorn:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

To run the automated tests:

```bash
pytest
```

## Configuration

The backend reads the `DATABASE_URL` environment variable to determine which
database to connect to. When the variable is not provided, it defaults to the
PostgreSQL service defined in `docker-compose.yml` (via
`postgresql+asyncpg://postgres:postgres@db:5432/postgres`). This makes it easy to
point the app or tests to a different database by exporting a new URL before
launching Uvicorn or invoking pytest.
