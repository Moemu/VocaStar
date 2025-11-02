from __future__ import annotations

"""Create community posts, attachments, likes, comments tables and group likes (idempotent)."""

import asyncio
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import config  # noqa: E402

TABLES = {
    "groups": "community_groups",
    "group_likes": "community_group_likes",
    "posts": "community_posts",
    "attachments": "community_post_attachments",
    "post_likes": "community_post_likes",
    "comments": "community_post_comments",
    "comment_likes": "community_comment_likes",
}


def _table_exists(sync_conn, table: str) -> bool:
    if sync_conn.dialect.name == "sqlite":
        res = sync_conn.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        return res.fetchone() is not None
    else:
        res = sync_conn.execute(text("SELECT to_regclass(:name)"), {"name": table})
        row = res.fetchone()
        return bool(row and row[0])


def _column_exists(sync_conn, table: str, column: str) -> bool:
    if sync_conn.dialect.name == "sqlite":
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


def _ensure_group_likes_column(sync_conn):
    # add likes_count to community_groups if missing
    if not _column_exists(sync_conn, TABLES["groups"], "likes_count"):
        dtype = "INTEGER" if sync_conn.dialect.name == "sqlite" else "INTEGER"
        sync_conn.exec_driver_sql(f"ALTER TABLE {TABLES['groups']} ADD COLUMN likes_count {dtype} DEFAULT 0")


def _create_group_likes(sync_conn):
    t = TABLES["group_likes"]
    if sync_conn.dialect.name == "sqlite":
        sync_conn.exec_driver_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {t} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL REFERENCES {TABLES['groups']}(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMP NOT NULL DEFAULT (datetime('now')),
                UNIQUE(group_id, user_id)
            )
            """
        )
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_group_like_group ON {t}(group_id)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_group_like_user ON {t}(user_id)")
    else:
        sync_conn.exec_driver_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {t} (
                id SERIAL PRIMARY KEY,
                group_id INTEGER NOT NULL REFERENCES {TABLES['groups']}(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                CONSTRAINT uniq_group_like UNIQUE (group_id, user_id)
            )
            """
        )
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_group_like_group ON {t}(group_id)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_group_like_user ON {t}(user_id)")


def _create_posts(sync_conn):
    t = TABLES["posts"]
    if sync_conn.dialect.name == "sqlite":
        sync_conn.exec_driver_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {t} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL REFERENCES {TABLES['groups']}(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                likes_count INTEGER NOT NULL DEFAULT 0,
                comments_count INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT (datetime('now')),
                updated_at TIMESTAMP NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_post_group ON {t}(group_id)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_post_user ON {t}(user_id)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_post_created ON {t}(created_at)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_post_likes ON {t}(likes_count)")
    else:
        sync_conn.exec_driver_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {t} (
                id SERIAL PRIMARY KEY,
                group_id INTEGER NOT NULL REFERENCES {TABLES['groups']}(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                likes_count INTEGER NOT NULL DEFAULT 0,
                comments_count INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_post_group ON {t}(group_id)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_post_user ON {t}(user_id)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_post_created ON {t}(created_at)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_post_likes ON {t}(likes_count)")


def _create_attachments(sync_conn):
    t = TABLES["attachments"]
    p = TABLES["posts"]
    if sync_conn.dialect.name == "sqlite":
        sync_conn.exec_driver_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {t} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL REFERENCES {p}(id) ON DELETE CASCADE,
                type VARCHAR(20) NOT NULL,
                url VARCHAR(1000) NOT NULL,
                title VARCHAR(300) NULL,
                file_size INTEGER NULL,
                download_count INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_attach_post ON {t}(post_id)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_attach_type ON {t}(type)")
    else:
        sync_conn.exec_driver_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {t} (
                id SERIAL PRIMARY KEY,
                post_id INTEGER NOT NULL REFERENCES {p}(id) ON DELETE CASCADE,
                type VARCHAR(20) NOT NULL,
                url VARCHAR(1000) NOT NULL,
                title VARCHAR(300) NULL,
                file_size INTEGER NULL,
                download_count INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_attach_post ON {t}(post_id)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_attach_type ON {t}(type)")


def _create_post_likes(sync_conn):
    t = TABLES["post_likes"]
    p = TABLES["posts"]
    if sync_conn.dialect.name == "sqlite":
        sync_conn.exec_driver_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {t} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL REFERENCES {p}(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMP NOT NULL DEFAULT (datetime('now')),
                UNIQUE(post_id, user_id)
            )
            """
        )
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_post_like_post ON {t}(post_id)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_post_like_user ON {t}(user_id)")
    else:
        sync_conn.exec_driver_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {t} (
                id SERIAL PRIMARY KEY,
                post_id INTEGER NOT NULL REFERENCES {p}(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                CONSTRAINT uniq_post_like UNIQUE (post_id, user_id)
            )
            """
        )
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_post_like_post ON {t}(post_id)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_post_like_user ON {t}(user_id)")


def _create_comments(sync_conn):
    t = TABLES["comments"]
    p = TABLES["posts"]
    if sync_conn.dialect.name == "sqlite":
        sync_conn.exec_driver_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {t} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL REFERENCES {p}(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                content VARCHAR(1000) NOT NULL,
                likes_count INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_comment_post ON {t}(post_id)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_comment_user ON {t}(user_id)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_comment_created ON {t}(created_at)")
    else:
        sync_conn.exec_driver_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {t} (
                id SERIAL PRIMARY KEY,
                post_id INTEGER NOT NULL REFERENCES {p}(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                content VARCHAR(1000) NOT NULL,
                likes_count INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_comment_post ON {t}(post_id)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_comment_user ON {t}(user_id)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_comment_created ON {t}(created_at)")


def _create_comment_likes(sync_conn):
    t = TABLES["comment_likes"]
    c = TABLES["comments"]
    if sync_conn.dialect.name == "sqlite":
        sync_conn.exec_driver_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {t} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comment_id INTEGER NOT NULL REFERENCES {c}(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMP NOT NULL DEFAULT (datetime('now')),
                UNIQUE(comment_id, user_id)
            )
            """
        )
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_comment_like_comment ON {t}(comment_id)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_comment_like_user ON {t}(user_id)")
    else:
        sync_conn.exec_driver_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {t} (
                id SERIAL PRIMARY KEY,
                comment_id INTEGER NOT NULL REFERENCES {c}(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                CONSTRAINT uniq_comment_like UNIQUE (comment_id, user_id)
            )
            """
        )
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_comment_like_comment ON {t}(comment_id)")
        sync_conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS idx_comment_like_user ON {t}(user_id)")


async def main() -> None:
    engine = create_async_engine(config.db_url, echo=False)
    async with engine.begin() as conn:
        # ensure group likes_count column
        await conn.run_sync(_ensure_group_likes_column)
        # group likes table
        if not await conn.run_sync(lambda s: _table_exists(s, TABLES["group_likes"])):
            await conn.run_sync(_create_group_likes)
        # core post tables
        if not await conn.run_sync(lambda s: _table_exists(s, TABLES["posts"])):
            await conn.run_sync(_create_posts)
        if not await conn.run_sync(lambda s: _table_exists(s, TABLES["attachments"])):
            await conn.run_sync(_create_attachments)
        if not await conn.run_sync(lambda s: _table_exists(s, TABLES["post_likes"])):
            await conn.run_sync(_create_post_likes)
        if not await conn.run_sync(lambda s: _table_exists(s, TABLES["comments"])):
            await conn.run_sync(_create_comments)
        if not await conn.run_sync(lambda s: _table_exists(s, TABLES["comment_likes"])):
            await conn.run_sync(_create_comment_likes)

    await engine.dispose()
    print("✔️  Community posts tables up-to-date")


if __name__ == "__main__":
    asyncio.run(main())
