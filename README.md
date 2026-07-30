# MIOS

**Market Intelligence & Operations System** — a FastAPI service providing market
analysis, decision support, and operational intelligence.

The canonical architecture specifications in [`docs/`](docs/) are the single source
of truth; this README covers running and developing the application.

---

## Technology stack

| Concern | Choice |
|---|---|
| Language | Python 3.13 |
| Web framework | FastAPI |
| Validation | Pydantic v2 |
| Configuration | pydantic-settings |
| Primary database | PostgreSQL 17 |
| Time-series | TimescaleDB |
| ORM | SQLAlchemy 2 (async, psycopg 3) |
| Migrations | Alembic (async) |
| Cache | Redis |
| Event Bus | NATS JetStream |
| Server | Uvicorn |
| Containers | Docker Compose |
| Packaging | uv |
| Quality | ruff, mypy (strict), pytest |

## Requirements

- Python 3.13
- [uv](https://docs.astral.sh/uv/)
- Docker + Docker Compose (for infrastructure)

## Infrastructure

This layer provides platform services only — no ORM models, repositories, or
business logic. Each component is a lifecycle-managed singleton connected during
application startup and released on shutdown.

| Module | Responsibility |
|---|---|
| [`db/session.py`](src/mios/db/session.py) | Async engine, session factory, pool configuration, `get_session` dependency, `transaction()` for non-request callers |
| [`db/timescale.py`](src/mios/db/timescale.py) | TimescaleDB extension validation at startup |
| [`cache/client.py`](src/mios/cache/client.py) | Redis async client, pool, `get_cache` dependency |
| [`events/client.py`](src/mios/events/client.py) | NATS connection, JetStream context, reconnect handling, `get_jetstream` dependency |
| [`core/startup.py`](src/mios/core/startup.py) | Connection sequencing, startup validation, ordered shutdown |
| [`core/health.py`](src/mios/core/health.py) | Live connectivity probes for every component |

### Startup validation

With `STARTUP_VALIDATION=true` (the default), startup probes every component and
aborts if any is unreachable, so an instance never serves traffic it cannot
fulfil. Set it to `false` for local work without infrastructure — the
application then starts and reports `degraded` on its health endpoint.

### Project structure

```
src/mios/
├── __main__.py          executable entrypoint (python -m mios)
├── main.py              FastAPI application factory
├── api/                 versioned routing (router → v1 → endpoints)
├── cache/               Redis infrastructure
├── config/              constants and environment-driven settings
├── core/                logging, lifespan, startup, health
├── db/                  connection lifecycle: engine, sessions, TimescaleDB validation
├── domain/              domain logic (future)
├── events/              NATS JetStream infrastructure
├── models/              domain-specific models built on the persistence layer (future)
├── persistence/         the ORM base, mixins, types, and helpers — see below
├── schemas/             request/response schemas
├── services/            application services (future)
└── utils/               shared utilities
migrations/              Alembic environment
```

`config/constants.py` holds fixed properties of the application;
`config/settings.py` holds everything read from the environment. Connection
strings are always derived from settings — never hardcoded.

## Persistence architecture

`mios.persistence` is the platform's single ORM foundation — the only
inheritance point for mapped classes. It holds no business meaning: it declares
no tables and knows nothing about Users, Markets, Instruments, or any other
canonical concept. Those arrive as future models built *on* this layer, per
[`docs/24-database-design.md`](docs/24-database-design.md).

| Module | Provides |
|---|---|
| [`persistence/metadata.py`](src/mios/persistence/metadata.py) | The one `MetaData` object every mapped table belongs to, carrying the naming convention in `config/constants.py` |
| [`persistence/base.py`](src/mios/persistence/base.py) | `Base` — the `DeclarativeBase` all models inherit, with a `type_annotation_map` resolving `UUID`, `datetime`, `Decimal`, and `dict` annotations to the shared types below |
| [`persistence/types.py`](src/mios/persistence/types.py) | `UUIDType`, `UTCDateTime` (rejects naive datetimes, normalizes to UTC), `NumericType` (exact `Decimal`, never `float`), `JSONType`, `enum_column()` |
| [`persistence/mixins.py`](src/mios/persistence/mixins.py) | `IdentityMixin`, `TimestampMixin`, `AuditMixin`, `SoftDeleteMixin`, `VersionMixin` — independent, composable |
| [`persistence/utils.py`](src/mios/persistence/utils.py) | `new_uuid()`, `utc_now()`, `next_version()` — storage helpers, not business logic |

### Naming conventions

Every implicitly named constraint and index gets a deterministic name from
`DB_NAMING_CONVENTION` in [`config/constants.py`](src/mios/config/constants.py)
(`pk_<table>`, `uq_<table>_<column>`, `fk_<table>_<column>_<ref>`, `ix_<column>`,
`ck_<table>_<constraint>`). This is what makes a downgrade able to drop a
constraint by the same name its upgrade created, and keeps autogenerated
migrations stable across schema changes.

### Creating future models

```python
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from mios.persistence import Base, IdentityMixin, TimestampMixin, AuditMixin


class Widget(IdentityMixin, TimestampMixin, AuditMixin, Base):
    __tablename__ = "widget"

    name: Mapped[str] = mapped_column(unique=True)
    owner_id: Mapped[UUID]  # resolves to UUIDType via type_annotation_map
```

Compose only the mixins a model needs — `SoftDeleteMixin` and `VersionMixin` are
available the same way. A model using `SoftDeleteMixin` with a unique column
should pair it with `soft_delete_index()` so the uniqueness constraint excludes
deleted rows, letting a value be reused after deletion.

Once real models exist, import their module in
[`migrations/env.py`](migrations/env.py) so autogenerate can see their tables —
importing `mios.persistence` alone only registers the metadata object, not any
model that hasn't been imported elsewhere.

## Development setup

```bash
uv sync
```

```bash
cp .env.example .env
```

## Starting services

Bring up PostgreSQL/TimescaleDB, Redis, and NATS (with JetStream enabled):

```bash
docker compose up -d postgres redis nats
```

Run the full stack, API included:

```bash
docker compose up -d --build
```

Services start in dependency order — the API waits for all three to report
healthy. Data persists in the `postgres_data`, `redis_data`, and `nats_data`
volumes. Tear down, keeping data:

```bash
docker compose down
```

Discard data as well:

```bash
docker compose down -v
```

## Running locally

Against infrastructure started above:

```bash
uv run python -m mios
```

With auto-reload:

```bash
uv run uvicorn mios.main:app --reload
```

- Swagger UI — http://127.0.0.1:8000/docs
- Health — http://127.0.0.1:8000/api/v1/health

The health endpoint verifies live connectivity on every request and returns 503
when any component is unreachable:

```json
{
  "status": "healthy",
  "application": "MIOS",
  "version": "0.1.0",
  "environment": "development",
  "components": {
    "database": { "name": "database", "status": "up", "latency_ms": 1.24 },
    "redis": { "name": "redis", "status": "up", "latency_ms": 0.41 },
    "nats": { "name": "nats", "status": "up", "latency_ms": 0.38 }
  }
}
```

## Running migrations

Alembic resolves its connection from `Settings`, so no credentials live in
`alembic.ini`.

```bash
uv run alembic upgrade head
```

Revision `0001_baseline` enables the `timescaledb` extension — the only
database-level infrastructure this layer needs before any tables exist.

Roll back and re-apply:

```bash
uv run alembic downgrade base
uv run alembic upgrade head
```

Autogenerate a revision after adding ORM models — import the model's module in
[`migrations/env.py`](migrations/env.py) first, or autogenerate will see no
tables to compare against:

```bash
uv run alembic revision --autogenerate -m "describe the change"
```

Create an empty revision (for extensions, hypertables, or data migrations):

```bash
uv run alembic revision -m "describe the change"
```

Preview SQL without connecting:

```bash
uv run alembic upgrade head --sql
```

Check for drift between models and the database before committing a migration:

```bash
uv run alembic check
```

`env.py` reflects every PostgreSQL schema (`include_schemas=True`) so
cross-schema foreign keys are seen, but TimescaleDB's own catalog schemas
(`_timescaledb_catalog`, `_timescaledb_internal`, and similar) are excluded from
comparison — without that exclusion, autogenerate proposes dropping the
extension's internal tables.

Constraint names follow the convention in `config/constants.py`, so
autogenerated migrations stay stable. No migrations exist yet.

## Running tests

Infrastructure is mocked; no running services are required.

```bash
uv run pytest
```

`.env.test` supplies the test configuration and is loaded automatically.

## Linting

```bash
uv run ruff check .
```

```bash
uv run ruff format --check .
```

Apply fixes:

```bash
uv run ruff check --fix . && uv run ruff format .
```

## Type checking

```bash
uv run mypy .
```

## Environment variables

### Application

| Variable | Default | Purpose |
|---|---|---|
| `APP_NAME` | `MIOS` | Application name, shown in OpenAPI |
| `APP_VERSION` | `0.1.0` | Application version |
| `APP_ENV` | `development` | One of `development`, `testing`, `staging`, `production` |
| `DEBUG` | `true` | FastAPI debug mode |
| `HOST` | `127.0.0.1` | Bind address |
| `PORT` | `8000` | Bind port |
| `API_PREFIX` | `/api/v1` | Mount point for the API |
| `LOG_LEVEL` | `INFO` | One of `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG` |
| `LOG_JSON` | `false` | Emit structured JSON logs |
| `STARTUP_VALIDATION` | `true` | Abort startup when a component is unreachable |

### PostgreSQL

| Variable | Default | Purpose |
|---|---|---|
| `POSTGRES_HOST` | `127.0.0.1` | Server host |
| `POSTGRES_PORT` | `5432` | Server port |
| `POSTGRES_USER` | `mios` | Role |
| `POSTGRES_PASSWORD` | `mios` | Password |
| `POSTGRES_DB` | `mios` | Database name |
| `POSTGRES_POOL_SIZE` | `10` | Pooled connections |
| `POSTGRES_MAX_OVERFLOW` | `5` | Connections allowed beyond the pool |
| `POSTGRES_POOL_TIMEOUT` | `30` | Seconds to wait for a pooled connection |
| `POSTGRES_POOL_RECYCLE` | `1800` | Seconds before a connection is recycled |
| `POSTGRES_POOL_PRE_PING` | `true` | Validate connections before use |
| `POSTGRES_CONNECT_TIMEOUT` | `10` | Connection timeout in seconds |
| `POSTGRES_ECHO` | `false` | Log emitted SQL |
| `TIMESCALEDB_ENABLED` | `true` | Validate the TimescaleDB extension at startup |

### Redis

| Variable | Default | Purpose |
|---|---|---|
| `REDIS_HOST` | `127.0.0.1` | Server host |
| `REDIS_PORT` | `6379` | Server port |
| `REDIS_DB` | `0` | Logical database |
| `REDIS_PASSWORD` | _unset_ | Password, if required |
| `REDIS_MAX_CONNECTIONS` | `20` | Pool size |
| `REDIS_SOCKET_TIMEOUT` | `5` | Socket read timeout in seconds |
| `REDIS_CONNECT_TIMEOUT` | `5` | Socket connect timeout in seconds |

### NATS JetStream

| Variable | Default | Purpose |
|---|---|---|
| `NATS_SERVERS` | `nats://127.0.0.1:4222` | Comma-separated server list |
| `NATS_CONNECT_TIMEOUT` | `5` | Per-server connect timeout, and the startup budget |
| `NATS_MAX_RECONNECT_ATTEMPTS` | `-1` | Reconnect attempts after startup; `-1` is unlimited |
| `NATS_RECONNECT_TIME_WAIT` | `2` | Seconds between reconnect attempts |
| `NATS_PING_INTERVAL` | `30` | Seconds between server pings |

## Roadmap

- **Sprint 4** — Market Store domain models and repositories for the aggregates in [`docs/17-domain-model.md`](docs/17-domain-model.md), built on the persistence layer
- Event publishing and consumption over the Event Bus per [`docs/06-event-bus.md`](docs/06-event-bus.md) and [`docs/22-event-contracts.md`](docs/22-event-contracts.md)
- Analysis engines (price, liquidity, momentum, context) per [`docs/02-architecture.md`](docs/02-architecture.md)
- Decision and AI explanation engines
- Authentication and authorization per [`docs/27-security-model.md`](docs/27-security-model.md)
- Structured error handling per [`docs/26-error-model.md`](docs/26-error-model.md)
- Metrics, tracing, and correlation IDs per [`docs/28-observability-model.md`](docs/28-observability-model.md)
