"""Declarative base and shared metadata.

Defines the metadata container and constraint naming conventions that Alembic
autogeneration targets. No tables or ORM models are declared here.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from mios.config.constants import DB_NAMING_CONVENTION

metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)


class Base(DeclarativeBase):
    """Declarative base for all future ORM models."""

    metadata = metadata
