from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.sql import async_session_maker  # noqa: E402


async def get_async_engine() -> AsyncEngine:
    async with async_session_maker() as session:
        bind = session.bind
    if bind is None:
        raise RuntimeError("Could not acquire database engine from session maker")
    if not isinstance(bind, AsyncEngine):
        raise TypeError(f"Expected AsyncEngine, got {type(bind)!r}")
    return bind


def ensure_sqlite_directory(engine: AsyncEngine) -> None:
    if not engine.url.drivername.startswith("sqlite"):
        return
    database = engine.url.database
    if not database or database == ":memory:":
        return
    db_path = Path(database)
    if not db_path.is_absolute():
        db_path = Path.cwd() / db_path
    directory = db_path.parent
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)


async def exec_safe(conn: AsyncConnection, sql: str, *, error_msg: str | None = None) -> None:
    try:
        await conn.execute(text(sql))
        print(f"[migrate] executed: {sql}")
    except Exception as exc:  # noqa: BLE001
        if error_msg:
            print(error_msg.format(error=exc))
        else:
            print(f"[migrate] skip: {sql} ({exc})")


async def run_sqlite_migration(conn: AsyncConnection) -> None:
    for ddl in [
        "ALTER TABLE achievements ADD COLUMN code TEXT",
        "ALTER TABLE achievements ADD COLUMN condition_type TEXT",
        "ALTER TABLE achievements ADD COLUMN threshold INTEGER",
    ]:
        await exec_safe(conn, ddl)
    await exec_safe(
        conn,
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_achievements_code_unique ON achievements(code)",
    )
    await exec_safe(
        conn,
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_user_achievements_uniq ON user_achievements(user_id, achievement_id)",
    )


async def run_generic_migration(conn: AsyncConnection) -> None:
    await exec_safe(conn, "ALTER TABLE achievements ADD COLUMN code VARCHAR(100)")
    await exec_safe(conn, "UPDATE achievements SET code = 'default_code' WHERE code IS NULL")
    await exec_safe(
        conn,
        "ALTER TABLE achievements ALTER COLUMN code SET NOT NULL",
        error_msg="[migrate] Could not set 'code' column as NOT NULL: {error}",
    )
    await exec_safe(conn, "ALTER TABLE achievements ADD COLUMN condition_type VARCHAR(50)")
    await exec_safe(conn, "ALTER TABLE achievements ADD COLUMN threshold INTEGER")
    await exec_safe(
        conn,
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_achievements_code_unique ON achievements(code)",
    )
    await exec_safe(
        conn,
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_user_achievements_uniq ON user_achievements(user_id, achievement_id)",
    )


async def main() -> None:
    engine = await get_async_engine()
    ensure_sqlite_directory(engine)
    try:
        async with engine.begin() as conn:
            dialect = conn.dialect.name
            print(f"[migrate] Detected database dialect: {dialect}")
            if dialect == "sqlite":
                await run_sqlite_migration(conn)
            else:
                await run_generic_migration(conn)
    finally:
        await engine.dispose()
    print("[migrate] achievements minimal migration done.")


if __name__ == "__main__":
    asyncio.run(main())
