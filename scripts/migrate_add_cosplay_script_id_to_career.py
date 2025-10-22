"""
Migration script to add the 'cosplay_script_id' column to the 'careers' table.

This script connects to the database, checks for the existence of the column,
and adds it if it is missing. It is designed to be idempotent and safe to run
multiple times.
"""

import asyncio
import logging
import sys
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from app.core.config import config  # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

DATABASE_URL = str(config.db_url)
TABLE_NAME = "careers"
COLUMN_NAME = "cosplay_script_id"
INDEX_NAME = f"ix_{TABLE_NAME}_{COLUMN_NAME}"


async def column_exists(conn, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table (async-safe via run_sync)."""

    def _inner(sync_conn) -> bool:
        inspector = sa.inspect(sync_conn)
        columns = inspector.get_columns(table_name)
        return any(c.get("name") == column_name for c in columns)

    return await conn.run_sync(_inner)


async def add_cosplay_script_id_column():
    """
    Adds the 'cosplay_script_id' integer column with a foreign key constraint
    to the 'careers' table if it does not already exist.
    """
    logger.info(f"Connecting to the database at {DATABASE_URL.split('@')[-1]}")
    engine = create_async_engine(DATABASE_URL, echo=False)

    async with engine.connect() as conn:
        try:
            logger.info(f"Checking for column '{COLUMN_NAME}' in table '{TABLE_NAME}'...")
            if await column_exists(conn, TABLE_NAME, COLUMN_NAME):
                logger.info(f"Column '{COLUMN_NAME}' already exists in '{TABLE_NAME}'. No action needed.")
                return

            logger.info(f"Column '{COLUMN_NAME}' not found. Proceeding with migration.")

            dialect_name = conn.dialect.name
            logger.info(f"Database dialect detected: {dialect_name}")

            if dialect_name == "sqlite":
                # SQLite does not support adding foreign key constraints via ALTER TABLE in older versions.
                # However, modern versions handle this better. We will try the standard SQL first.
                # A full data migration (create new table, copy data, drop old, rename) is the
                # most robust way but is significantly more complex.
                # This simpler approach is often sufficient for development environments.
                logger.warning(
                    "Attempting to add a column with a foreign key to a SQLite table. "
                    "This might not be fully supported on older SQLite versions."
                )
                alter_sql = text(
                    f"""
                    ALTER TABLE {TABLE_NAME}
                    ADD COLUMN {COLUMN_NAME} INTEGER
                    REFERENCES cosplay_scripts(id) ON DELETE SET NULL
                    """
                )
                from sqlalchemy.sql import quoted_name

                index_sql = text("CREATE INDEX IF NOT EXISTS :index_name ON :table_name(:column_name)").bindparams(
                    index_name=quoted_name(INDEX_NAME, quote=True),
                    table_name=quoted_name(TABLE_NAME, quote=True),
                    column_name=quoted_name(COLUMN_NAME, quote=True),
                )

            elif dialect_name == "postgresql":
                alter_sql = text(
                    f"""
                    ALTER TABLE {TABLE_NAME}
                    ADD COLUMN IF NOT EXISTS {COLUMN_NAME} INTEGER
                    REFERENCES cosplay_scripts(id) ON DELETE SET NULL
                    """
                )
                index_sql = text(f"CREATE INDEX IF NOT EXISTS {INDEX_NAME} ON {TABLE_NAME}({COLUMN_NAME})")

            else:
                logger.error(f"Unsupported database dialect: {dialect_name}")
                raise NotImplementedError(f"Migration for {dialect_name} is not implemented.")

            logger.info(f"Executing ALTER TABLE statement for {dialect_name}...")
            await conn.execute(alter_sql)
            logger.info("Table altered successfully.")

            logger.info(f"Creating index '{INDEX_NAME}' on '{TABLE_NAME}({COLUMN_NAME})'...")
            await conn.execute(index_sql)
            logger.info("Index created successfully.")

            await conn.commit()
            logger.info("Migration committed successfully.")

        except SQLAlchemyError as e:
            logger.error(f"An error occurred during the migration: {e}")
            await conn.rollback()
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            await conn.rollback()
            raise
        finally:
            await engine.dispose()
            logger.info("Database connection closed.")


async def main():
    try:
        await add_cosplay_script_id_column()
        logger.info("Migration script finished successfully.")
    except Exception as e:
        logger.error(f"Migration script failed: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
