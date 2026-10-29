"""Additive, idempotent schema synchronisation for existing RajOS databases.

The application creates missing tables at startup with
``Base.metadata.create_all``.  That call never alters tables that already
exist, so a database created by an older release keeps its old columns and
breaks as soon as a newer model adds a field.

This module closes that gap **without ever destroying data**:

  * only ADDs missing columns (``ALTER TABLE ... ADD COLUMN``)
  * only creates missing tables (via ``create_all``)
  * only creates missing indexes (including the automation idempotency index)
  * never drops, renames or rewrites anything

Alembic revisions remain the documented migration history (see
``alembic/versions``); this sync guarantees a running server can always work
with the database it is pointed at, even if migrations have not been applied
yet.  Every change is logged.
"""

from __future__ import annotations

import logging
from typing import List

import sqlalchemy as sa
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text

logger = logging.getLogger(__name__)

# Indexes the application depends on: (index name, table, columns, unique)
_REQUIRED_INDEXES = (
    (
        "uq_automation_runs_automation_execution_key",
        "automation_runs",
        ["automation_id", "execution_key"],
        True,
    ),
)


def _literal_default(column: sa.Column, dialect) -> str:
    """Best-effort SQL literal for a NOT NULL default on an added column."""
    default = None
    if column.default is not None:
        default = column.default.arg
    elif column.server_default is not None:
        default = column.server_default.arg

    if isinstance(default, str) and default.upper().startswith("CURRENT_TIMESTAMP"):
        return "CURRENT_TIMESTAMP"
    if default is not None and not callable(default):
        if isinstance(default, bool):
            return "1" if default else "0"
        if isinstance(default, (int, float)):
            return str(default)
        return "'" + str(default).replace("'", "''") + "'"

    # Callable / missing defaults: fall back to a type-appropriate literal.
    col_type = column.type
    if isinstance(col_type, Boolean):
        return "0"
    if isinstance(col_type, (Integer, Float)):
        return "0" if isinstance(col_type, Integer) else "0.0"
    if isinstance(col_type, DateTime):
        return "CURRENT_TIMESTAMP"
    return "''"


def _add_column_ddl(table_name: str, column: sa.Column, dialect) -> str:
    type_sql = column.type.compile(dialect=dialect)
    ddl = f'ALTER TABLE "{table_name}" ADD COLUMN "{column.name}" {type_sql}'
    if not column.nullable:
        ddl += f" NOT NULL DEFAULT {_literal_default(column, dialect)}"
    return ddl


def sync_schema(engine) -> List[str]:
    """Bring the database up to date with the current models (additive only).

    Returns a list of human-readable changes that were applied.
    """
    changes: List[str] = []

    # 1. Missing tables (create_all is a no-op for existing tables).
    Base = _base()
    Base.metadata.create_all(bind=engine)

    inspector = sa.inspect(engine)
    tables = set(inspector.get_table_names())

    # 2. Missing columns.
    with engine.begin() as connection:
        for table in Base.metadata.sorted_tables:
            if table.name not in tables:
                continue
            existing = {c["name"] for c in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in existing:
                    continue
                ddl = _add_column_ddl(table.name, column, engine.dialect)
                connection.execute(sa.text(ddl))
                changes.append(f"{table.name}.{column.name} added")

        # 3. Missing indexes.
        for index_name, table_name, columns, unique in _REQUIRED_INDEXES:
            if table_name not in tables:
                continue
            known = {i["name"] for i in inspector.get_indexes(table_name)}
            if index_name in known:
                continue
            cols = ", ".join(f'"{c}"' for c in columns)
            unique_sql = "UNIQUE " if unique else ""
            connection.execute(
                sa.text(
                    f'CREATE {unique_sql}INDEX "{index_name}" '
                    f'ON "{table_name}" ({cols})'
                )
            )
            changes.append(f"index {index_name} created")

    if changes:
        logger.warning("Database schema synchronised: %s", "; ".join(changes))
    return changes


def _base():
    from app.database.connection import Base
    return Base


def schema_is_current(engine) -> bool:
    """Return True when the database already matches the current models."""
    inspector = sa.inspect(engine)
    tables = set(inspector.get_table_names())
    Base = _base()
    for table in Base.metadata.sorted_tables:
        if table.name not in tables:
            return False
        existing = {c["name"] for c in inspector.get_columns(table.name)}
        if any(column.name not in existing for column in table.columns):
            return False
    return True
