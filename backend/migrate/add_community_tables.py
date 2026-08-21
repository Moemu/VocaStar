from __future__ import annotations

"""Create community tables: categories, groups, members (idempotent, SQLite/PG compatible)."""

import asyncio
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Ensure project root is on sys.path when executing as a standalone script
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import config  # noqa: E402

TABLES = {
    "categories": "community_categories",
    "groups": "community_groups",
    "members": "community_group_members",
}


def _table_exists(sync_conn, table: str) -> bool:
    dialect_name = sync_conn.dialect.name
    if dialect_name == "sqlite":
        res = sync_conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name"), {"table_name": table}
        )
        return res.fetchone() is not None
    else:
        res = sync_conn.execute(text("SELECT to_regclass(:name)"), {"name": table})
        row = res.fetchone()
        return bool(row and row[0])


def _create_categories(sync_conn) -> None:
    dialect_name = sync_conn.dialect.name
    if dialect_name == "sqlite":
        sync_conn.exec_driver_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {TABLES['categories']} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug VARCHAR(50) NOT NULL UNIQUE,
                name VARCHAR(100) NOT NULL,
                "order" INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
    else:
        sync_conn.exec_driver_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {TABLES['categories']} (
                id SERIAL PRIMARY KEY,
                slug VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                "order" INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )


def _create_groups(sync_conn) -> None:
    dialect_name = sync_conn.dialect.name
    if dialect_name == "sqlite":
        sync_conn.exec_driver_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {TABLES['groups']} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                summary VARCHAR(300) NOT NULL,
                description TEXT NULL,
                cover_url VARCHAR(500) NULL,
                category_id INTEGER NULL REFERENCES {TABLES['categories']}(id) ON DELETE SET NULL,
                owner_name VARCHAR(100) NULL,
                owner_avatar_url VARCHAR(500) NULL,
                rules_json TEXT NULL,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                members_count INTEGER NOT NULL DEFAULT 0,
                last_activity_at TIMESTAMP NULL,
                created_at TIMESTAMP NOT NULL DEFAULT (datetime('now')),
                updated_at TIMESTAMP NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_group_category ON {TABLES['groups']}(category_id)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_group_active ON {TABLES['groups']}(is_active)")
        sync_conn.exec_driver_sql(
            f"CREATE INDEX IF NOT EXISTS idx_group_last_activity ON {TABLES['groups']}(last_activity_at)"
        )
    else:
        sync_conn.exec_driver_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {TABLES['groups']} (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                summary VARCHAR(300) NOT NULL,
                description TEXT NULL,
                cover_url VARCHAR(500) NULL,
                category_id INTEGER NULL REFERENCES {TABLES['categories']}(id) ON DELETE SET NULL,
                owner_name VARCHAR(100) NULL,
                owner_avatar_url VARCHAR(500) NULL,
                rules_json TEXT NULL,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                members_count INTEGER NOT NULL DEFAULT 0,
                last_activity_at TIMESTAMPTZ NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_group_category ON {TABLES['groups']}(category_id)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_group_active ON {TABLES['groups']}(is_active)")
        sync_conn.exec_driver_sql(
            f"CREATE INDEX IF NOT EXISTS idx_group_last_activity ON {TABLES['groups']}(last_activity_at)"
        )


def _create_members(sync_conn) -> None:
    dialect_name = sync_conn.dialect.name
    if dialect_name == "sqlite":
        sync_conn.exec_driver_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {TABLES['members']} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL REFERENCES {TABLES['groups']}(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                role VARCHAR(20) NOT NULL DEFAULT 'member',
                joined_at TIMESTAMP NOT NULL DEFAULT (datetime('now')),
                UNIQUE(group_id, user_id)
            )
            """
        )
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_member_user ON {TABLES['members']}(user_id)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_member_group ON {TABLES['members']}(group_id)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_member_role ON {TABLES['members']}(role)")
    else:
        sync_conn.exec_driver_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {TABLES['members']} (
                id SERIAL PRIMARY KEY,
                group_id INTEGER NOT NULL REFERENCES {TABLES['groups']}(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                role VARCHAR(20) NOT NULL DEFAULT 'member',
                joined_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                CONSTRAINT uniq_group_user UNIQUE (group_id, user_id)
            )
            """
        )
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_member_user ON {TABLES['members']}(user_id)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_member_group ON {TABLES['members']}(group_id)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_member_role ON {TABLES['members']}(role)")


async def main() -> None:
    engine = create_async_engine(config.db_url, echo=False)
    async with engine.begin() as conn:
        if not await conn.run_sync(lambda s: _table_exists(s, TABLES["categories"])):
            await conn.run_sync(_create_categories)
        if not await conn.run_sync(lambda s: _table_exists(s, TABLES["groups"])):
            await conn.run_sync(_create_groups)
        if not await conn.run_sync(lambda s: _table_exists(s, TABLES["members"])):
            await conn.run_sync(_create_members)

        # Ensure newly added columns exist when upgrading from older schema
        def _column_exists(sync_conn, table: str, column: str) -> bool:
            if sync_conn.dialect.name == "sqlite":
                # Validate table name using whitelist
                if table not in TABLES.values():
                    raise ValueError(f"Invalid table name: {table}")
                res = sync_conn.exec_driver_sql(f"PRAGMA table_info({table})")
                names = {str(row[1]).lower() for row in res.fetchall()}
                return column.lower() in names
            else:
                res = sync_conn.execute(
                    text(
                        """
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = :table AND column_name = :column
                        """
                    ),
                    {"table": table, "column": column},
                )
                return res.fetchone() is not None

        def _add_missing_columns(sync_conn):
            table = TABLES["groups"]
            # owner_name
            if not _column_exists(sync_conn, table, "owner_name"):
                sync_conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN owner_name VARCHAR(100)")
            # owner_avatar_url
            if not _column_exists(sync_conn, table, "owner_avatar_url"):
                sync_conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN owner_avatar_url VARCHAR(500)")
            # rules_json
            if not _column_exists(sync_conn, table, "rules_json"):
                sync_conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN rules_json TEXT")

        def _ensure_columns(sync_conn):
            # groups table new columns
            _add_missing_columns(sync_conn)
            # members.role column
            table_m = TABLES["members"]
            if not _column_exists(sync_conn, table_m, "role"):
                sync_conn.exec_driver_sql(f"ALTER TABLE {table_m} ADD COLUMN role VARCHAR(20) DEFAULT 'member'")

        await conn.run_sync(_ensure_columns)

    await engine.dispose()
    print("✔️  Community tables up-to-date")


if __name__ == "__main__":
    asyncio.run(main())
