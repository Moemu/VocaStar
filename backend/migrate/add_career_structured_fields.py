"""Add structured career fields required by the revamped YAML schema.

Usage (from project root):

    uv run python scripts/migrate_add_career_structured_fields.py

The script inspects the current database schema and appends the following
nullable columns to the ``careers`` table when they are missing:

- ``career_header_image``: VARCHAR(500)
- ``overview``: JSON
- ``competency_requirements``: JSON
- ``salary_and_distribution``: JSON
- ``skill_map``: JSON

The migration is idempotent and safe to run multiple times. It currently
supports SQLite and PostgreSQL—extend ``_build_alter_statement`` if you need
another dialect.
"""

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from app.core.sql import async_session_maker  # noqa: E402

TABLE_NAME = "careers"


@dataclass(frozen=True)
class ColumnSpec:
    name: str
    sqlite_type: str
    postgres_type: str

    def build_sql(self, dialect: str) -> str:
        builder: dict[str, Callable[[ColumnSpec], str]] = {
            "sqlite": lambda spec: f"ALTER TABLE {TABLE_NAME} ADD COLUMN {spec.name} {spec.sqlite_type}",
            "postgresql": lambda spec: f"ALTER TABLE {TABLE_NAME} ADD COLUMN IF NOT EXISTS {spec.name} {spec.postgres_type}",  # noqa: E501
        }
        if dialect not in builder:
            raise RuntimeError(f"Unsupported database dialect {dialect!r}; please add migration logic before retrying")
        return builder[dialect](self)


COLUMNS: tuple[ColumnSpec, ...] = (
    ColumnSpec("career_header_image", "VARCHAR(500)", "VARCHAR(500)"),
    ColumnSpec("overview", "JSON", "JSON"),
    ColumnSpec("competency_requirements", "JSON", "JSON"),
    ColumnSpec("salary_and_distribution", "JSON", "JSON"),
    ColumnSpec("skill_map", "JSON", "JSON"),
)


async def _get_async_engine() -> AsyncEngine:
    async with async_session_maker() as session:
        bind = session.bind
    if bind is None:
        raise RuntimeError("Could not acquire database engine from session maker")
    if not isinstance(bind, AsyncEngine):
        raise TypeError("Expected an AsyncEngine instance")
    return bind


def _has_column(sync_conn: Connection, table_name: str, column_name: str) -> bool:
    inspector = inspect(sync_conn)
    columns = inspector.get_columns(table_name)
    return any(col["name"] == column_name for col in columns)


async def _column_exists(engine: AsyncEngine, column: ColumnSpec) -> bool:
    async with engine.begin() as conn:
        return await conn.run_sync(_has_column, TABLE_NAME, column.name)


async def _add_column(engine: AsyncEngine, column: ColumnSpec) -> None:
    dialect = engine.dialect.name
    sql = column.build_sql(dialect)
    async with engine.begin() as conn:
        await conn.execute(text(sql))
    print(f"✅ Added column {column.name} ({dialect})")


async def migrate() -> None:
    engine = await _get_async_engine()
    try:
        dialect = engine.dialect.name
        print(f"Connected to database (dialect={dialect})")
        for column in COLUMNS:
            exists = await _column_exists(engine, column)
            if exists:
                print(f"✔️  Column {column.name} already present on {TABLE_NAME}")
                continue
            await _add_column(engine, column)
    finally:
        await engine.dispose()


def main() -> None:
    asyncio.run(migrate())


if __name__ == "__main__":
    main()
