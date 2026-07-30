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
| [`db/session.py`](src/mios/db/session.py) | Async engine, session factory, pool configuration, `get_session` dependency |
| [`db/base.py`](src/mios/db/base.py) | Declarative base and metadata carrying constraint naming conventions |
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
├── db/                  engine, sessions, TimescaleDB validation
├── domain/              domain logic (future)
├── events/              NATS JetStream infrastructure
├── models/              persistence models (future)
├── schemas/             request/response schemas
├── services/            application services (future)
└── utils/               shared utilities
migrations/              Alembic environment
```

`config/constants.py` holds fixed properties of the application;
`config/settings.py` holds everything read from the environment. Connection
strings are always derived from settings — never hardcoded.

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

Autogenerate a revision after adding ORM models:

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

- **Sprint 3** — Market Store persistence: ORM models, repositories, and migrations for the aggregates in [`docs/17-domain-model.md`](docs/17-domain-model.md)
- Event publishing and consumption over the Event Bus per [`docs/06-event-bus.md`](docs/06-event-bus.md) and [`docs/22-event-contracts.md`](docs/22-event-contracts.md)
- Analysis engines (price, liquidity, momentum, context) per [`docs/02-architecture.md`](docs/02-architecture.md)
- Decision and AI explanation engines
- Authentication and authorization per [`docs/27-security-model.md`](docs/27-security-model.md)
- Structured error handling per [`docs/26-error-model.md`](docs/26-error-model.md)
- Metrics, tracing, and correlation IDs per [`docs/28-observability-model.md`](docs/28-observability-model.md)
