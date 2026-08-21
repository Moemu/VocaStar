"""Ensure table cosplay_wrongbook exists with the latest schema.

This script is idempotent and supports SQLite and PostgreSQL. It will:
1) Create the table if missing (with the latest columns)
2) If the table exists, ensure the column `selected_option_text` exists; if missing, add it

Usage:
    uv run python migrate/add_cosplay_wrongbook.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from app.core.config import config  # noqa: E402

TABLE_NAME = "cosplay_wrongbook"
COLUMN_SELECTED = "selected_option_text"


async def table_exists(conn, table_name: str) -> bool:
    def _exists(sync_conn) -> bool:
        dialect_name = sync_conn.dialect.name
        if dialect_name == "sqlite":
            res = sync_conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name"), {"name": table_name}
            )
            return res.fetchone() is not None
        # PostgreSQL
        res = sync_conn.execute(text("SELECT to_regclass(:name)"), {"name": table_name})
        row = res.fetchone()
        return bool(row and row[0])

    return await conn.run_sync(_exists)


async def create_table(conn) -> None:
    def _create(sync_conn) -> None:
        dialect_name = sync_conn.dialect.name
        if dialect_name == "sqlite":
            sync_conn.exec_driver_sql(
                f"""
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    script_id INTEGER NOT NULL,
                    scene_id VARCHAR(100) NOT NULL,
                    script_title VARCHAR(200) NOT NULL,
                    scene_title VARCHAR(200) NOT NULL,
                    {COLUMN_SELECTED} VARCHAR(500) NULL,
                    correct_option_text VARCHAR(500) NOT NULL,
                    analysis TEXT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT (datetime('now'))
                )
                """
            )
            # Indexes and unique constraint
            sync_conn.exec_driver_sql(
                f"CREATE UNIQUE INDEX IF NOT EXISTS idx_wrongbook_user_script_scene ON {TABLE_NAME}"
                "(user_id, script_id, scene_id)"
            )
            sync_conn.exec_driver_sql(
                f"CREATE INDEX IF NOT EXISTS idx_wrongbook_created_at ON {TABLE_NAME}(created_at)"
            )
        else:
            # PostgreSQL
            sync_conn.exec_driver_sql(
                f"""
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    script_id INTEGER NOT NULL REFERENCES cosplay_scripts(id) ON DELETE CASCADE,
                    scene_id VARCHAR(100) NOT NULL,
                    script_title VARCHAR(200) NOT NULL,
                    scene_title VARCHAR(200) NOT NULL,
                    {COLUMN_SELECTED} VARCHAR(500) NULL,
                    correct_option_text VARCHAR(500) NOT NULL,
                    analysis TEXT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
            sync_conn.exec_driver_sql(
                f"CREATE UNIQUE INDEX IF NOT EXISTS idx_wrongbook_user_script_scene ON {TABLE_NAME}"
                "(user_id, script_id, scene_id)"
            )
            sync_conn.exec_driver_sql(
                f"CREATE INDEX IF NOT EXISTS idx_wrongbook_created_at ON {TABLE_NAME}(created_at)"
            )

    await conn.run_sync(_create)


async def column_exists(conn, table_name: str, column_name: str) -> bool:
    def _exists(sync_conn) -> bool:
        dialect_name = sync_conn.dialect.name
        if dialect_name == "sqlite":
            res = sync_conn.exec_driver_sql(f"PRAGMA table_info({table_name})")
            for row in res.fetchall():
                # row[1] is column name
                if len(row) > 1 and str(row[1]).lower() == column_name.lower():
                    return True
            return False
        # PostgreSQL
        res = sync_conn.execute(
            text(
                """
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = :table AND column_name = :column
                """
            ),
            {"table": table_name, "column": column_name},
        )
        return res.fetchone() is not None

    return await conn.run_sync(_exists)


async def add_selected_option_column(conn) -> None:
    def _add(sync_conn) -> None:
        dialect_name = sync_conn.dialect.name
        if dialect_name == "sqlite":
            # SQLite 不支持在 ALTER TABLE ADD COLUMN 语句中使用 IF NOT EXISTS，这里在检查后再执行
            sync_conn.exec_driver_sql(f"ALTER TABLE {TABLE_NAME} ADD COLUMN {COLUMN_SELECTED} VARCHAR(500)")
        else:
            sync_conn.exec_driver_sql(
                f"ALTER TABLE {TABLE_NAME} ADD COLUMN IF NOT EXISTS {COLUMN_SELECTED} VARCHAR(500)"
            )

    await conn.run_sync(_add)


async def main() -> None:
    engine = create_async_engine(config.db_url, echo=False, future=True)
    try:
        async with engine.begin() as conn:
            exists = await table_exists(conn, TABLE_NAME)
            if not exists:
                await create_table(conn)
                print(f"✅ Created table {TABLE_NAME}")
            else:
                # 表已存在，确保新增列存在
                col_ok = await column_exists(conn, TABLE_NAME, COLUMN_SELECTED)
                if not col_ok:
                    await add_selected_option_column(conn)
                    print(f"✅ Added column {COLUMN_SELECTED} on {TABLE_NAME}")
                else:
                    print(f"✔️  Table {TABLE_NAME} already up-to-date")
    except SQLAlchemyError as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(main())
