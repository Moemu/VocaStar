"""Ensure the careers table has the `cover` column.

Usage (from project root):

    uv run python scripts/migrate_add_career_cover.py

The script checks the current SQL dialect and adds the nullable `cover` column
when required. For existing rows we do not backfill any data because the field
represents an optional image path.
"""

from __future__ import annotations

import asyncio

from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.sql import async_session_maker

COLUMN_NAME = "cover"
TABLE_NAME = "careers"
COLUMN_SQL_TYPE = "VARCHAR(100)"


def _has_column(sync_conn: Connection, table_name: str, column_name: str) -> bool:
    inspector = inspect(sync_conn)
    columns = inspector.get_columns(table_name)
    return any(col["name"] == column_name for col in columns)


def _build_sqlite_alter() -> str:
    return f"ALTER TABLE {TABLE_NAME} ADD COLUMN {COLUMN_NAME} {COLUMN_SQL_TYPE}"


def _build_postgres_alter() -> str:
    return f"ALTER TABLE {TABLE_NAME} ADD COLUMN IF NOT EXISTS {COLUMN_NAME} {COLUMN_SQL_TYPE}"


async def get_async_engine() -> AsyncEngine:
    async with async_session_maker() as session:
        bind = session.bind
    if bind is None:
        raise RuntimeError("Could not acquire database engine from session maker")
    if not isinstance(bind, AsyncEngine):
        raise TypeError("Expected an AsyncEngine instance")
    return bind


async def ensure_cover_column(async_engine: AsyncEngine) -> bool:
    """Add the careers.cover column when it is missing.

    Returns True if the column was added during this run, False if it already existed.
    """

    async with async_engine.begin() as conn:
        column_exists = await conn.run_sync(_has_column, TABLE_NAME, COLUMN_NAME)
    if column_exists:
        print("✔️  Column cover already exists on careers")
        return False

    dialect = async_engine.dialect.name
    print(f"Detected database dialect: {dialect}")

    if dialect == "sqlite":
        alter_sql = _build_sqlite_alter()
    elif dialect == "postgresql":
        alter_sql = _build_postgres_alter()
    else:
        raise RuntimeError(f"Unsupported dialect {dialect!r}; please add migration logic for it")

    async with async_engine.begin() as conn:
        await conn.execute(text(alter_sql))
        print("✅ Added cover column to careers")

    return True


async def main() -> None:
    engine = await get_async_engine()
    try:
        await ensure_cover_column(engine)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
