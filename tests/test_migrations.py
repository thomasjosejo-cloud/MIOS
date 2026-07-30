"""Tests for the Alembic migration environment.

Configuration and revision wiring are checked without a database; applying
migrations against a real server is covered by `test_persistence_integration.py`.
"""

from pathlib import Path

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy.schema import SchemaItem

from mios.config import get_settings
from mios.persistence import metadata

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ALEMBIC_INI = PROJECT_ROOT / "alembic.ini"


@pytest.fixture
def alembic_config() -> Config:
    return Config(str(ALEMBIC_INI))


@pytest.fixture
def scripts(alembic_config: Config) -> ScriptDirectory:
    return ScriptDirectory.from_config(alembic_config)


def test_alembic_ini_exists() -> None:
    assert ALEMBIC_INI.is_file()


def test_script_location_is_configured(alembic_config: Config) -> None:
    assert alembic_config.get_main_option("script_location") == "migrations"


def test_no_database_url_is_hardcoded(alembic_config: Config) -> None:
    """The DSN must come from Settings, never from the ini file."""
    assert alembic_config.get_main_option("sqlalchemy.url") is None


def test_environment_resolves_the_dsn_from_settings() -> None:
    assert get_settings().database_dsn.startswith("postgresql+psycopg://")


def test_revision_chain_has_a_single_head(scripts: ScriptDirectory) -> None:
    assert len(scripts.get_heads()) == 1


def test_baseline_is_the_root_revision(scripts: ScriptDirectory) -> None:
    revisions = list(scripts.walk_revisions())

    assert revisions[-1].revision == "0001_baseline"
    assert revisions[-1].down_revision is None


def test_every_revision_is_reversible(scripts: ScriptDirectory) -> None:
    """Each revision must define both upgrade and downgrade."""
    for revision in scripts.walk_revisions():
        source = Path(revision.path).read_text()
        assert "def upgrade() -> None:" in source
        assert "def downgrade() -> None:" in source


def test_baseline_declares_no_tables(scripts: ScriptDirectory) -> None:
    """The baseline enables extensions only; business tables come later."""
    baseline = next(
        revision
        for revision in scripts.walk_revisions()
        if revision.revision == "0001_baseline"
    )
    source = Path(baseline.path).read_text()

    assert "create_table" not in source
    assert "timescaledb" in source


def test_target_metadata_is_the_shared_metadata() -> None:
    env = (PROJECT_ROOT / "migrations" / "env.py").read_text()

    assert "from mios.persistence import metadata" in env
    assert "target_metadata = metadata" in env
    assert metadata.naming_convention


def test_script_template_produces_typed_revisions() -> None:
    template = (PROJECT_ROOT / "migrations" / "script.py.mako").read_text()

    assert "def upgrade() -> None:" in template
    assert "def downgrade() -> None:" in template
    assert "down_revision: str | None" in template


# --- Extension schema filtering ----------------------------------------------
#
# `include_schemas=True` makes autogenerate reflect every schema on the server,
# including TimescaleDB's internal catalogs. Without a filter, `alembic check`
# proposes dropping those catalogs entirely (verified manually against a real
# server before this filter was added). `env.py` runs top-level code on import
# and dispatches to a live database connection, so its filter functions are
# loaded directly from source here rather than imported, to exercise the actual
# logic without triggering that dispatch.


@pytest.fixture(scope="module")
def env_namespace() -> dict[str, object]:
    """Execute env.py's filter definitions in isolation.

    Skips its top-level Alembic wiring (`context.config`, engine setup), which
    requires an active migration context this test does not create.
    """
    source = (PROJECT_ROOT / "migrations" / "env.py").read_text()
    start = source.index("EXTENSION_SCHEMAS = frozenset(")
    end = source.index("def migration_options")
    body = source[start:end]

    namespace: dict[str, object] = {"SchemaItem": SchemaItem}
    exec(compile(body, "env.py", "exec"), namespace)
    return namespace


def test_timescaledb_schemas_are_excluded_by_name(
    env_namespace: dict[str, object],
) -> None:
    include_name = env_namespace["include_name"]
    schemas = env_namespace["EXTENSION_SCHEMAS"]

    for schema in schemas:  # type: ignore[attr-defined]
        assert include_name(schema, "schema", {}) is False  # type: ignore[operator]

    assert include_name("public", "schema", {}) is True  # type: ignore[operator]


def test_objects_within_timescaledb_schemas_are_excluded(
    env_namespace: dict[str, object],
) -> None:
    include_name = env_namespace["include_name"]

    assert (
        include_name(  # type: ignore[operator]
            "bgw_job", "table", {"schema_name": "_timescaledb_catalog"}
        )
        is False
    )
    assert (
        include_name("some_table", "table", {"schema_name": "public"})  # type: ignore[operator]
        is True
    )


def test_include_object_checks_the_objects_own_schema(
    env_namespace: dict[str, object],
) -> None:
    include_object = env_namespace["include_object"]

    class FakeObject:
        def __init__(self, schema: str | None) -> None:
            self.schema = schema

    excluded = FakeObject("_timescaledb_internal")
    included = FakeObject("public")
    unschemad = FakeObject(None)

    assert include_object(excluded, "x", "table", False, None) is False  # type: ignore[operator]
    assert include_object(included, "x", "table", False, None) is True  # type: ignore[operator]
    assert include_object(unschemad, "x", "table", False, None) is True  # type: ignore[operator]
