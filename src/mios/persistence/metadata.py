"""The single metadata object for the platform.

Every mapped table, index, and constraint in MIOS belongs to this `MetaData`, so
Alembic autogeneration sees one coherent schema and constraint names are derived
consistently rather than left to the database.
"""

from sqlalchemy import MetaData

from mios.config.constants import DB_NAMING_CONVENTION

#: Shared metadata. `naming_convention` gives every implicitly named constraint
#: and index a deterministic name, which keeps migrations reversible: a
#: downgrade can drop a constraint by the same name the upgrade created.
metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)
