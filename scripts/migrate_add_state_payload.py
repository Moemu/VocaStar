"""Add the state_payload column to cosplay_sessions.

Usage (from project root):

    uv run python scripts/migrate_add_state_payload.py

The script detects the current SQL dialect and executes the appropriate
ALTER TABLE statement. Existing rows that still contain empty or NULL
payloads are backfilled with the default session template so that the
new cosplay workflow can operate safely.
"""

from __future__ import annotations

import asyncio
import json

from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.sql import async_session_maker

DEFAULT_STATE_PAYLOAD = {
    "current_scene_index": 0,
    "scores": {},
    "history": [],
}


async def get_async_engine() -> AsyncEngine:
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


async def ensure_state_payload_column(async_engine: AsyncEngine) -> None:
    async with async_engine.begin() as conn:
        column_exists = await conn.run_sync(_has_column, "cosplay_sessions", "state_payload")
    if column_exists:
        print("✔️  Column state_payload already exists on cosplay_sessions")
        return

    dialect = async_engine.dialect.name
    print(f"Detected database dialect: {dialect}")

    if dialect == "sqlite":
        alter_sql = "ALTER TABLE cosplay_sessions ADD COLUMN state_payload JSON NOT NULL DEFAULT '{}'"
    elif dialect == "postgresql":
        alter_sql = (
            "ALTER TABLE cosplay_sessions ADD COLUMN IF NOT EXISTS state_payload JSONB NOT NULL DEFAULT '{}'::jsonb"
        )
    else:
        raise RuntimeError(f"Unsupported dialect {dialect!r}; please add migration logic for it")

    async with async_engine.begin() as conn:
        await conn.execute(text(alter_sql))
        print("✅ Added state_payload column to cosplay_sessions")


async def backfill_state_payload(async_engine: AsyncEngine) -> None:
    payload_json = json.dumps(DEFAULT_STATE_PAYLOAD, ensure_ascii=True)
    dialect = async_engine.dialect.name

    if dialect == "sqlite":
        update_sql = text(
            """
            UPDATE cosplay_sessions
               SET state_payload = :payload
             WHERE state_payload IS NULL
                OR TRIM(state_payload) = ''
                OR state_payload = '{}'
            """
        )
        params = {"payload": payload_json}
    elif dialect == "postgresql":
        update_sql = text(
            """
            UPDATE cosplay_sessions
               SET state_payload = (:payload)::jsonb
             WHERE state_payload IS NULL
                OR state_payload = '{}'::jsonb
            """
        )
        params = {"payload": payload_json}
    else:
        # This branch should never be reached because ensure_state_payload_column already guards dialects
        raise RuntimeError(f"Unsupported dialect {dialect!r} for data backfill")

    async with async_engine.begin() as conn:
        result = await conn.execute(update_sql, params)
        rowcount = result.rowcount if result.rowcount is not None else 0
        if rowcount:
            print(f"✅ Backfilled default payload for {rowcount} existing session(s)")
        else:
            print("ℹ️  No existing sessions required backfilling")


async def main() -> None:
    engine = await get_async_engine()
    try:
        await ensure_state_payload_column(engine)
        await backfill_state_payload(engine)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
