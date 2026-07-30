"""Persistence models.

Importing this package registers every ORM model on the shared metadata, so
importing it in `migrations/env.py` is sufficient for Alembic autogeneration to
see all tables.
"""

from mios.models.options import OptionStrikeSnapshot

__all__ = ["OptionStrikeSnapshot"]
