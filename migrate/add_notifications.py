"""迁移脚本：创建通知表"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

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


async def get_async_engine() -> AsyncEngine:
    """获取数据库引擎"""
    from app.core.sql import _engine

    return _engine


async def ensure_notifications_table() -> None:
    """确保通知表存在"""
    engine = await get_async_engine()

    async with engine.begin() as conn:
        logger.info("检查 notifications 表是否存在...")
        dialect = conn.dialect.name

        if dialect == "sqlite":
            # SQLite: 创建表
            create_sql = """
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message_type VARCHAR NOT NULL,
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                is_read BOOLEAN NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                read_at DATETIME,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
            await conn.execute(text(create_sql))
            logger.info("✅ Created notifications table for SQLite")

            # 创建索引
            for index_sql in [
                "CREATE INDEX IF NOT EXISTS idx_notification_user_id ON notifications(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_notification_is_read ON notifications(is_read)",
                "CREATE INDEX IF NOT EXISTS idx_notification_created_at ON notifications(created_at)",
            ]:
                await conn.execute(text(index_sql))
                logger.info(f"✅ {index_sql}")

        elif dialect == "postgresql":
            # PostgreSQL: 使用 IF NOT EXISTS
            create_sql = """
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                message_type VARCHAR NOT NULL,
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                is_read BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                read_at TIMESTAMP,
                CONSTRAINT fk_notifications_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
            await conn.execute(text(create_sql))
            logger.info("✅ Created notifications table for PostgreSQL")

            # 创建索引
            for index_sql in [
                "CREATE INDEX IF NOT EXISTS idx_notification_user_id ON notifications(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_notification_is_read ON notifications(is_read)",
                "CREATE INDEX IF NOT EXISTS idx_notification_created_at ON notifications(created_at)",
            ]:
                await conn.execute(text(index_sql))
                logger.info(f"✅ {index_sql}")
        else:
            logger.warning(f"Unsupported dialect: {dialect}, skipping migrations")


async def main() -> None:
    try:
        logger.info(f"Starting migration against {DATABASE_URL.split('@')[-1]}")
        await ensure_notifications_table()
        logger.info("✅ Migration completed successfully")
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
