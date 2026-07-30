# MIOS

**Market Intelligence & Operations System** — a FastAPI service providing market
analysis, decision support, and operational intelligence.

The canonical architecture specifications live in [`docs/`](docs/); this README covers
running and developing the application itself.

---

## Technology stack

| Concern | Choice |
|---|---|
| Language | Python 3.12 |
| Web framework | FastAPI |
| Validation | Pydantic v2 |
| Configuration | pydantic-settings |
| Persistence | SQLAlchemy 2 + psycopg (PostgreSQL) |
| Migrations | Alembic |
| Cache / messaging | Redis |
| Server | Uvicorn |
| Packaging | uv |
| Quality | ruff, mypy (strict), pytest |

## Requirements

- Python 3.12
- [uv](https://docs.astral.sh/uv/)

## Project structure

```
src/mios/
├── __init__.py          package metadata
├── __main__.py          executable entrypoint (python -m mios)
├── main.py              FastAPI application factory
├── api/                 routing
│   ├── router.py         aggregates API versions
│   └── v1/
│       ├── router.py     v1 routes
│       └── endpoints/    endpoint handlers
├── config/              constants and environment-driven settings
├── core/                logging, application lifespan
├── db/                  database access
├── domain/              domain logic
├── models/              persistence models
├── schemas/             request/response schemas
├── services/            application services
└── utils/               shared utilities
```

`config/constants.py` holds fixed properties of the application.
`config/settings.py` holds everything read from the environment — the two are kept
separate so deployment-specific values never get hard-coded.

## Development setup

```bash
uv sync
```

Create your local environment file from the template:

```bash
cp .env.example .env
```

| Variable | Default | Purpose |
|---|---|---|
| `APP_NAME` | `MIOS` | Application name, shown in OpenAPI |
| `APP_VERSION` | `0.1.0` | Application version |
| `APP_ENV` | `development` | Deployment environment |
| `DEBUG` | `true` | FastAPI debug mode |
| `HOST` | `127.0.0.1` | Bind address |
| `PORT` | `8000` | Bind port |
| `LOG_LEVEL` | `INFO` | Root log level |
| `API_PREFIX` | `/api/v1` | Mount point for the API |

`.env.test` provides the test defaults and is loaded automatically by pytest.

## Running the application

```bash
uv run python -m mios
```

With auto-reload during development:

```bash
uv run uvicorn mios.main:app --reload
```

Then:

- Swagger UI — http://127.0.0.1:8000/docs
- Health check — http://127.0.0.1:8000/api/v1/health

```json
{ "status": "healthy", "application": "MIOS", "version": "0.1.0" }
```

## Running tests

```bash
uv run pytest
```

## Linting

```bash
uv run ruff check .
```

Apply fixes and format:

```bash
uv run ruff check --fix . && uv run ruff format .
```

## Type checking

```bash
uv run mypy src
```

## Roadmap

- **Sprint 2** — database layer: SQLAlchemy 2 models, Alembic migrations, session management
- Domain model and persistence for the aggregates defined in [`docs/17-domain-model.md`](docs/17-domain-model.md)
- Analysis engines (price, liquidity, momentum, context) per [`docs/02-architecture.md`](docs/02-architecture.md)
- Event bus and market store integration
- Authentication and authorization per [`docs/27-security-model.md`](docs/27-security-model.md)
- Structured error handling per [`docs/26-error-model.md`](docs/26-error-model.md)
- Observability: metrics, tracing, correlation IDs per [`docs/28-observability-model.md`](docs/28-observability-model.md)
