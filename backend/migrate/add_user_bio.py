"""
Migration script to add a 'bio' column to the 'users' table.
Idempotent and works for SQLite/PostgreSQL.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from app.core.config import config  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DATABASE_URL = str(config.db_url)
TABLE = "users"
COLUMN = "bio"


async def column_exists(conn, table: str, column: str) -> bool:
    def _inner(sync_conn) -> bool:
        inspector = sa.inspect(sync_conn)
        cols = inspector.get_columns(table)
        return any(c.get("name") == column for c in cols)

    return await conn.run_sync(_inner)


async def run() -> None:
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.connect() as conn:
        if await column_exists(conn, TABLE, COLUMN):
            logger.info("Column %s already exists on %s", COLUMN, TABLE)
            return
        dialect = conn.dialect.name
        logger.info("Adding column %s to %s (dialect=%s)", COLUMN, TABLE, dialect)
        if dialect == "sqlite":
            sql = text("ALTER TABLE {} ADD COLUMN {} TEXT".format(TABLE, COLUMN))
            await conn.execute(sql)
        elif dialect == "postgresql":
            sql = text("ALTER TABLE {} ADD COLUMN IF NOT EXISTS {} TEXT".format(TABLE, COLUMN))
            await conn.execute(sql)
        else:
            raise NotImplementedError(f"Unsupported dialect: {dialect}")
        await conn.commit()
        logger.info("Migration completed")
    await engine.dispose()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
