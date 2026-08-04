# syntax=docker/dockerfile:1

# --- Builder: resolve dependencies into a self-contained virtualenv ----------
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Dependencies are installed before the source is copied so the layer is reused
# whenever only application code changes.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,id=uv-cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# README.md is required by the build backend: pyproject declares it as the
# project readme, so packaging fails without it.
COPY README.md ./
COPY src ./src
COPY alembic.ini ./
COPY migrations ./migrations
RUN --mount=type=cache,id=uv-cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# --- Runtime ----------------------------------------------------------------
FROM python:3.13-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

RUN groupadd --system --gid 1001 mios \
    && useradd --system --uid 1001 --gid mios mios

WORKDIR /app

COPY --from=builder --chown=mios:mios /app /app

# Writable data directory for the persisted Fyers session. Creating it in the
# image owned by `mios` means a named volume mounted here inherits that
# ownership on first initialisation, so the non-root app user can write the
# session file without root.
RUN mkdir -p /app/data && chown -R mios:mios /app/data

USER mios

EXPOSE 8000

CMD ["uvicorn", "mios.main:app", "--host", "0.0.0.0", "--port", "8000"]
