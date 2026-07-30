"""Generic persistence helpers.

Storage-level utilities only — nothing here interprets what a record means.
"""

import datetime as dt
from uuid import UUID, uuid4

#: First version assigned to a newly inserted row.
INITIAL_VERSION = 1


def new_uuid() -> UUID:
    """Generate a random identifier for a new record."""
    return uuid4()


def utc_now() -> dt.datetime:
    """Return the current instant as a timezone-aware UTC datetime."""
    return dt.datetime.now(dt.UTC)


def next_version(current: int) -> int:
    """Return the version that follows `current`."""
    if current < INITIAL_VERSION:
        msg = f"Version must be >= {INITIAL_VERSION}, got {current}"
        raise ValueError(msg)
    return current + 1
